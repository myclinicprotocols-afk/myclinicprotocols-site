"""PayPal-verified private fulfillment API.

The public website never decides that an order is paid. It creates an order
here, sends the buyer to PayPal, and this service verifies the completed
capture at the server-calculated price before fulfillment begins.

Treatments with a connected production master receive an automatic Initial
Version package. Other accepted catalog treatments can enter a manual
fulfillment queue only when customer/owner email delivery is configured, so a
buyer is never charged for a manual order that cannot be surfaced to the team.

Order/payment state is persisted in Supabase so it survives Render restarts.
Generated packages are uploaded to the private Supabase Storage bucket when
available, with a local fallback for automatic packages.
"""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
from urllib.parse import quote
import secrets

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, EmailStr, Field

from fulfillment.documents import make_package, validate_production_treatments


OWNER_EMAIL = "myclinicprotocols@gmail.com"
PRICES = {
    "protocol": {1: 29, 2: 58, 3: 87, 4: 116, 5: 145, 6: 174, 7: 203, 8: 232},
    "complete": {1: 49, 2: 98, 3: 147, 4: 196, 5: 245},
    "all_access": {1: 249},
}
PRICING_VERSION = "2026-10-10-2"
ROOT = Path(os.environ.get("MYCP_PRIVATE_ROOT", "private-orders")).resolve()
ROOT.mkdir(parents=True, exist_ok=True)
DOWNLOAD_TTL = timedelta(hours=24)
DEFAULT_STORAGE_BUCKET = "order-packages"


class Checkout(BaseModel):
    customerEmail: EmailStr
    package: str
    treatments: list[str] = Field(min_length=1, max_length=10)
    documents: list[str] = Field(default_factory=list, max_length=12)
    clinic: dict
    providers: list[str] = Field(default_factory=list, max_length=20)
    oversight: dict = Field(default_factory=dict)
    details: dict = Field(default_factory=dict)
    expectedTotal: Decimal | None = Field(default=None, ge=0)
    pricingVersion: str | None = None


class Capture(BaseModel):
    orderReference: str | None = None
    paypalOrderId: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9-]+$")


class AllAccessRequest(BaseModel):
    accessCode: str = Field(min_length=20, max_length=64, pattern=r"^MYCP-[A-Z0-9-]+$")
    customerEmail: EmailStr
    treatment: str = Field(min_length=2, max_length=200)
    requestType: str = Field(default="complete", pattern=r"^(protocol|complete)$")
    notes: str = Field(default="", max_length=5000)


app = FastAPI(title="MyClinicProtocols Fulfillment", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com")],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _price(package: str, count: int) -> int:
    try:
        return PRICES[package][count]
    except KeyError as error:
        raise HTTPException(status_code=400, detail="Unsupported package or treatment quantity") from error


def _fulfillment_mode(treatments: list[str]) -> str:
    try:
        validate_production_treatments(treatments)
        return "automatic"
    except ValueError:
        return "manual"


def _email_configured() -> bool:
    return bool(os.environ.get("RESEND_API_KEY") and os.environ.get("ORDER_FROM_EMAIL"))


def _new_access_code() -> str:
    """Create a high-entropy, human-readable 30-day license code after verified payment."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    groups = ["".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(4)]
    return "MYCP-" + "-".join(groups)


def _supabase_config() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        raise HTTPException(status_code=503, detail="Order database is not configured")
    return url, key


def _storage_bucket() -> str:
    return os.environ.get("SUPABASE_STORAGE_BUCKET", DEFAULT_STORAGE_BUCKET).strip() or DEFAULT_STORAGE_BUCKET


def _first(mapping: dict, *keys: str) -> str | None:
    for key in keys:
        value = mapping.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


async def _supabase_request(client: httpx.AsyncClient, method: str, path: str, *, params: dict | None = None,
                            payload: dict | None = None, prefer: str | None = None) -> httpx.Response:
    url, key = _supabase_config()
    headers = {"apikey": key, "Content-Type": "application/json"}
    if prefer:
        headers["Prefer"] = prefer
    response = await client.request(method, f"{url}{path}", params=params, json=payload, headers=headers)
    if response.status_code >= 400:
        logging.error("Supabase request failed: %s %s -> %s", method, path, response.status_code)
        raise HTTPException(status_code=503, detail="Order database is temporarily unavailable")
    return response


async def _insert_order(client: httpx.AsyncClient, checkout: Checkout, reference: str, paypal_id: str, amount: str) -> None:
    clinic = checkout.clinic or {}
    details = checkout.details or {}
    intake = checkout.model_dump(mode="json")
    intake["_paymentMode"] = os.environ.get("PAYPAL_MODE", "sandbox")
    intake["_pricingVersion"] = PRICING_VERSION
    intake["_fulfillmentMode"] = "all_access" if checkout.package == "all_access" else _fulfillment_mode(checkout.treatments)
    row = {
        "order_reference": reference,
        "paypal_order_id": paypal_id,
        "payment_status": "CREATED",
        "payment_amount": amount,
        "currency": "USD",
        "customer_email": str(checkout.customerEmail),
        "clinic_name": _first(clinic, "name", "clinicName", "clinic_name", "businessName", "practiceName"),
        "clinic_state": _first(clinic, "state", "primaryState", "primary_state"),
        "provider_role": ", ".join(checkout.providers) if checkout.providers else None,
        "package_type": checkout.package,
        "treatment": " | ".join(checkout.treatments),
        "document_type": " | ".join(checkout.documents) if checkout.documents else None,
        "customer_notes": _first(details, "notes", "customerNotes", "specialInstructions", "instructions"),
        "intake": intake,
    }
    await _supabase_request(client, "POST", "/rest/v1/orders", payload=row, prefer="return=minimal")


async def _get_order(client: httpx.AsyncClient, *, reference: str | None = None, paypal_id: str | None = None) -> dict | None:
    params: dict[str, str] = {"select": "*", "limit": "1"}
    if reference:
        params["order_reference"] = f"eq.{reference}"
    if paypal_id:
        params["paypal_order_id"] = f"eq.{paypal_id}"
    response = await _supabase_request(client, "GET", "/rest/v1/orders", params=params)
    rows = response.json()
    return rows[0] if rows else None


async def _get_all_access_order_by_code(client: httpx.AsyncClient, access_code: str) -> dict | None:
    response = await _supabase_request(
        client,
        "GET",
        "/rest/v1/orders",
        params={"select": "*", "access_code": f"eq.{access_code}", "limit": "1"},
    )
    rows = response.json()
    return rows[0] if rows else None


async def _update_order(client: httpx.AsyncClient, reference: str, values: dict) -> None:
    values = {**values, "updated_at": datetime.now(timezone.utc).isoformat()}
    await _supabase_request(client, "PATCH", "/rest/v1/orders", params={"order_reference": f"eq.{reference}"},
                            payload=values, prefer="return=minimal")


def _storage_headers() -> dict[str, str]:
    _, key = _supabase_config()
    return {"apikey": key, "Authorization": f"Bearer {key}"}


async def _storage_upload(client: httpx.AsyncClient, storage_path: str, package_bytes: bytes) -> bool:
    try:
        url, _ = _supabase_config()
        bucket = quote(_storage_bucket(), safe="")
        object_path = quote(storage_path, safe="/")
        response = await client.post(
            f"{url}/storage/v1/object/{bucket}/{object_path}", content=package_bytes,
            headers={**_storage_headers(), "Content-Type": "application/zip", "x-upsert": "true"})
        if response.status_code >= 400:
            logging.error("Supabase Storage upload failed with status %s", response.status_code)
            return False
        return True
    except (HTTPException, httpx.HTTPError):
        logging.exception("Supabase Storage upload failed; using local fallback")
        return False


async def _storage_download(client: httpx.AsyncClient, storage_path: str) -> bytes:
    url, _ = _supabase_config()
    bucket = quote(_storage_bucket(), safe="")
    object_path = quote(storage_path, safe="/")
    response = await client.get(f"{url}/storage/v1/object/authenticated/{bucket}/{object_path}", headers=_storage_headers())
    if response.status_code >= 400:
        logging.error("Supabase Storage download failed with status %s", response.status_code)
        raise HTTPException(status_code=404, detail="Package not found")
    return response.content


@app.on_event("startup")
async def verify_supabase_connectivity() -> None:
    print(
        f"MYCP startup: PayPal mode={os.environ.get('PAYPAL_MODE', 'sandbox')}, pricing={PRICING_VERSION}, "
        f"emailConfigured={_email_configured()}", flush=True)
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        logging.warning("Supabase is not configured in this Render environment")
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await _supabase_request(client, "GET", "/rest/v1/orders", params={"select": "id", "limit": "1"})
            print("MYCP startup: Supabase database connectivity OK", flush=True)
            url, _ = _supabase_config()
            bucket = quote(_storage_bucket(), safe="")
            storage = await client.get(f"{url}/storage/v1/bucket/{bucket}", headers=_storage_headers())
            if storage.status_code < 400:
                print(f"MYCP startup: Supabase Storage connectivity OK for {_storage_bucket()}", flush=True)
            else:
                logging.warning("Supabase Storage connectivity check returned status %s", storage.status_code)
    except Exception:
        logging.exception("Supabase startup connectivity check failed")


def _paypal_base() -> str:
    return "https://api-m.sandbox.paypal.com" if os.environ.get("PAYPAL_MODE", "sandbox") == "sandbox" else "https://api-m.paypal.com"


async def _paypal_token(client: httpx.AsyncClient) -> str:
    client_id = os.environ.get("PAYPAL_CLIENT_ID")
    secret = os.environ.get("PAYPAL_CLIENT_SECRET")
    if not client_id or not secret:
        raise HTTPException(status_code=503, detail="Payment service is not configured")
    response = await client.post(f"{_paypal_base()}/v1/oauth2/token", data={"grant_type": "client_credentials"}, auth=(client_id, secret))
    response.raise_for_status()
    return response.json()["access_token"]


async def _paypal(client: httpx.AsyncClient, method: str, path: str, payload: dict | None = None) -> dict:
    token = await _paypal_token(client)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Prefer": "return=representation"}
    if method == "POST" and path.endswith("/capture"):
        headers["PayPal-Request-Id"] = "capture-" + path.split("/")[-2]
    response = await client.request(method, f"{_paypal_base()}{path}", json=payload, headers=headers)
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="PayPal rejected the payment request")
    return response.json()


def _sign(reference: str, expires: int) -> str:
    secret = os.environ.get("DOWNLOAD_SIGNING_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="Download service is not configured")
    message = f"{reference}.{expires}".encode()
    digest = hmac.new(secret.encode(), message, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def _download_url(reference: str) -> str:
    expires = int((datetime.now(timezone.utc) + DOWNLOAD_TTL).timestamp())
    base = os.environ.get("PUBLIC_API_URL", "http://localhost:8000").rstrip("/")
    return f"{base}/api/download/{reference}?expires={expires}&signature={_sign(reference, expires)}"


async def _send_email(to: list[str], subject: str, html: str) -> bool:
    key = os.environ.get("RESEND_API_KEY")
    sender = os.environ.get("ORDER_FROM_EMAIL")
    if not key or not sender:
        return False
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {key}"},
                                     json={"from": sender, "to": to, "subject": subject, "html": html})
        return response.status_code < 400


@app.post("/api/checkout/create")
async def create_checkout(checkout: Checkout):
    count = len(checkout.treatments)
    amount = f"{_price(checkout.package, count):.2f}"
    if ((checkout.expectedTotal is not None and checkout.expectedTotal != Decimal(amount))
            or (checkout.pricingVersion is not None and checkout.pricingVersion != PRICING_VERSION)):
        raise HTTPException(status_code=409, detail="Pricing has changed. Refresh the order page and review your total before paying.")
    payment_mode = os.environ.get("PAYPAL_MODE", "sandbox")
    fulfillment_mode = "all_access" if checkout.package == "all_access" else _fulfillment_mode(checkout.treatments)
    if fulfillment_mode == "manual" and not _email_configured():
        raise HTTPException(
            status_code=409,
            detail="This treatment requires clinic-specific preparation before delivery. Online payment is not available for it yet; please email myclinicprotocols@gmail.com and we’ll help you complete the order."
        )
    reference = "MYCP-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + secrets.token_hex(4).upper()
    return_url = os.environ.get("PAYPAL_RETURN_URL")
    cancel_url = os.environ.get("PAYPAL_CANCEL_URL")
    if not return_url or not cancel_url:
        raise HTTPException(status_code=503, detail="Payment return URLs are not configured")
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{"custom_id": reference, "invoice_id": reference,
                            "description": "MyClinicProtocols 30-Day All Access" if checkout.package == "all_access" else "MyClinicProtocols customized document package",
                            "amount": {"currency_code": "USD", "value": amount}}],
        "payment_source": {"paypal": {"experience_context": {"brand_name": "MyClinicProtocols", "user_action": "PAY_NOW",
                                                                  "return_url": return_url, "cancel_url": cancel_url}}},
    }
    async with httpx.AsyncClient(timeout=25) as client:
        paypal = await _paypal(client, "POST", "/v2/checkout/orders", payload)
        await _insert_order(client, checkout, reference, paypal["id"], amount)
    approval = next(link["href"] for link in paypal.get("links", []) if link.get("rel") == "payer-action")
    return {"orderReference": reference, "paypalOrderId": paypal["id"], "approvalUrl": approval,
            "amount": amount, "currency": "USD", "paymentMode": payment_mode, "fulfillmentMode": fulfillment_mode,
            "pricingVersion": PRICING_VERSION}


def _row_amount(row: dict) -> str:
    return f"{Decimal(str(row['payment_amount'])):.2f}"


def _order_intake(row: dict) -> dict:
    intake = row.get("intake") or {}
    if isinstance(intake, str):
        try:
            intake = json.loads(intake)
        except json.JSONDecodeError:
            return {}
    return intake if isinstance(intake, dict) else {}


def _completed_response(row: dict) -> dict:
    intake = _order_intake(row)
    mode = intake.get("_fulfillmentMode", "automatic")
    package_key = intake.get("package")
    has_package = bool(row.get("package_storage_path"))
    status = "COMPLETED" if has_package or package_key == "all_access" else "PROCESSING"
    response = {
        "status": status,
        "orderReference": row["order_reference"],
        "downloadUrl": _download_url(row["order_reference"]) if has_package else None,
        "amount": _row_amount(row),
        "currency": row.get("currency") or "USD",
        "paymentMode": intake.get("_paymentMode", "unknown"),
        "fulfillmentMode": mode,
        "package": package_key,
        "treatmentCount": 1 if package_key == "all_access" else len(intake.get("treatments") or []),
        "pricingVersion": intake.get("_pricingVersion"),
        "emailDelivery": {"customer": bool(row.get("email_delivery"))},
    }
    if package_key == "all_access":
        response["accessStartsAt"] = row.get("access_starts_at") or row.get("paid_at")
        response["accessExpiresAt"] = row.get("access_expires_at")
        response["accessCode"] = row.get("access_code")
        origin = os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com").rstrip("/")
        response["requestUrl"] = f"{origin}/all-access-request.html"
    return response


def _verify_paypal_order(result: dict, row: dict, *, require_capture: bool) -> None:
    units = result.get("purchase_units") or []
    unit = units[0] if len(units) == 1 else {}
    expected_amount = {"value": _row_amount(row), "currency_code": row["currency"]}
    valid = (result.get("id") == row["paypal_order_id"] and result.get("intent") == "CAPTURE"
             and unit.get("custom_id") == row["order_reference"] and unit.get("invoice_id") == row["order_reference"]
             and all(unit.get("amount", {}).get(k) == v for k, v in expected_amount.items()))
    if require_capture:
        captures = unit.get("payments", {}).get("captures") or []
        payment = captures[0] if len(captures) == 1 else {}
        valid = (valid and result.get("status") == "COMPLETED" and payment.get("status") == "COMPLETED"
                 and bool(payment.get("id")) and all(payment.get("amount", {}).get(k) == v for k, v in expected_amount.items()))
    if not valid:
        logging.warning("PayPal verification failed for %s (order status %s)", row["order_reference"], result.get("status"))
        raise HTTPException(status_code=409, detail="Payment could not be verified")


@app.post("/api/checkout/capture")
async def capture_checkout(capture: Capture):
    async with httpx.AsyncClient(timeout=25) as client:
        row = await _get_order(client, reference=capture.orderReference, paypal_id=capture.paypalOrderId)
        if not row:
            raise HTTPException(status_code=404, detail="Order not found")
        if row["payment_status"] == "COMPLETED":
            intake = _order_intake(row)
            if ((row.get("package_type") == "all_access" or intake.get("package") == "all_access")
                    and not row.get("access_code")):
                access_code = _new_access_code()
                issued_at = datetime.now(timezone.utc).isoformat()
                await _update_order(client, row["order_reference"], {
                    "access_code": access_code,
                    "access_code_issued_at": issued_at,
                })
                row["access_code"] = access_code
                row["access_code_issued_at"] = issued_at
            return _completed_response(row)

        path = f"/v2/checkout/orders/{row['paypal_order_id']}"
        result = await _paypal(client, "GET", path)
        _verify_paypal_order(result, row, require_capture=False)
        if result.get("status") == "APPROVED":
            try:
                await _paypal(client, "POST", path + "/capture")
            except (HTTPException, httpx.TransportError):
                logging.warning("Reconciling capture response for %s", row["order_reference"])
            result = await _paypal(client, "GET", path)
        _verify_paypal_order(result, row, require_capture=True)

        order = _order_intake(row)
        order["orderReference"] = row["order_reference"]
        if order.get("package") == "all_access":
            paid_dt = datetime.now(timezone.utc)
            expires_dt = paid_dt + timedelta(days=30)
            paid_at = paid_dt.isoformat()
            access_expires_at = expires_dt.isoformat()
            access_code = row.get("access_code") or _new_access_code()
            access_code_issued_at = datetime.now(timezone.utc).isoformat()
            order["_fulfillmentMode"] = "all_access"
            await _update_order(client, row["order_reference"], {
                "payment_status": "COMPLETED",
                "paid_at": paid_at,
                "access_starts_at": paid_at,
                "access_expires_at": access_expires_at,
                "access_code": access_code,
                "access_code_issued_at": access_code_issued_at,
                "package_storage_path": None,
                "intake": order,
            })
            row.update({"payment_status": "COMPLETED", "paid_at": paid_at, "access_starts_at": paid_at,
                        "access_expires_at": access_expires_at, "access_code": access_code,
                        "access_code_issued_at": access_code_issued_at, "package_storage_path": None, "intake": order})
            origin = os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com").rstrip("/")
            request_url = f"{origin}/all-access-request.html"
            customer_email_sent = await _send_email(
                [row["customer_email"]],
                f"Your MYCP 30-Day All Access is active — {row['order_reference']}",
                f"<p>Payment confirmed — your 30-Day All Access is active.</p><p>Your access is valid through <strong>{expires_dt.strftime('%B %d, %Y')}</strong>.</p><p>Your 30-Day Access Code is <strong>{access_code}</strong>.</p><p><a href='{request_url}'>Open the All Access Request Portal</a> and use this code with your purchasing email any time during your active period.</p><p>This pass is for one clinic/legal practice and is non-transferable. Specialty or investigational requests may require scope review. Please do not submit PHI.</p>")
            owner_email_sent = await _send_email(
                [OWNER_EMAIL],
                f"NEW $249 ALL ACCESS — {row['order_reference']}",
                f"<p>A verified $249 30-Day All Access purchase was received.</p><p>Customer: {row['customer_email']}</p><p>Clinic: {row.get('clinic_name') or 'Not provided'}</p><p>Order: {row['order_reference']}</p><p>Access expires: {expires_dt.strftime('%B %d, %Y')}</p>")
            await _update_order(client, row["order_reference"], {"email_delivery": customer_email_sent})
            row["email_delivery"] = customer_email_sent
            response = _completed_response(row)
            response["emailDelivery"] = {"customer": customer_email_sent, "owner": owner_email_sent}
            return response

        fulfillment_mode = order.get("_fulfillmentMode") or _fulfillment_mode(order.get("treatments") or [])
        storage_path = None
        if fulfillment_mode == "automatic":
            try:
                package_bytes = make_package(order)
                candidate_path = f"{row['order_reference']}/initial-version-package.zip"
                if await _storage_upload(client, candidate_path, package_bytes):
                    storage_path = candidate_path
                else:
                    local_path = ROOT / row["order_reference"] / "initial-version-package.zip"
                    local_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                    local_path.write_bytes(package_bytes)
                    storage_path = "local:" + str(local_path)
            except ValueError:
                logging.exception("Automatic master generation failed; routing %s to manual fulfillment", row["order_reference"])
                fulfillment_mode = "manual"
                order["_fulfillmentMode"] = "manual"

        paid_at = datetime.now(timezone.utc).isoformat()
        values = {"payment_status": "COMPLETED", "paid_at": paid_at, "intake": order}
        if storage_path:
            values["package_storage_path"] = storage_path
        await _update_order(client, row["order_reference"], values)
        row["payment_status"] = "COMPLETED"
        row["package_storage_path"] = storage_path
        row["paid_at"] = paid_at
        row["intake"] = order

    if storage_path:
        url = _download_url(row["order_reference"])
        customer_subject = f"Your MyClinicProtocols Initial Version — {row['order_reference']}"
        customer_html = (f"<p>Payment confirmed.</p><p><a href='{url}'>Download your Initial Version DOCX + PDF package</a>. "
                         "This private link expires in 24 hours.</p><p><strong>Prepared for qualified provider review.</strong></p>"
                         "<p>Your RN-reviewed final version is normally delivered within 1–2 hours and may take up to 24 hours depending on the document set. "
                         "Up to two consolidated revision rounds may be requested within 14 calendar days of delivery; revisions normally take 3–5 business days.</p>")
        owner_subject = f"Paid MYCP order — {row['order_reference']}"
    else:
        url = None
        customer_subject = f"Your MyClinicProtocols order is confirmed — {row['order_reference']}"
        customer_html = ("<p>Payment confirmed. Your clinic-specific Initial Version is now being prepared from the appropriate MyClinicProtocols master package.</p>"
                         "<p>It is normally emailed within 1–2 hours and may take up to 24 hours for larger or more complex document sets.</p>"
                         "<p>You do not need to place another order. We will send the files to this email address when they are ready.</p>")
        owner_subject = f"MANUAL FULFILLMENT — Paid MYCP order — {row['order_reference']}"

    customer_email_sent = await _send_email([row["customer_email"]], customer_subject, customer_html)
    owner_email_sent = await _send_email(
        [OWNER_EMAIL], owner_subject,
        f"<p>A verified payment of ${_row_amount(row)} USD was received.</p><p>Customer: {row['customer_email']}</p>"
        f"<p>Order: {row['order_reference']}</p><p>Fulfillment mode: {fulfillment_mode}</p>"
        f"<p>Treatment(s): {row.get('treatment') or ''}</p>")
    async with httpx.AsyncClient(timeout=15) as client:
        await _update_order(client, row["order_reference"], {"email_delivery": customer_email_sent})
    row["email_delivery"] = customer_email_sent
    response = _completed_response(row)
    response["emailDelivery"] = {"customer": customer_email_sent, "owner": owner_email_sent}
    if url:
        response["downloadUrl"] = url
    return response


@app.post("/api/all-access/request")
async def submit_all_access_request(request: AllAccessRequest):
    async with httpx.AsyncClient(timeout=20) as client:
        row = await _get_all_access_order_by_code(client, request.accessCode.strip().upper())
        if not row:
            raise HTTPException(status_code=404, detail="Access code not found")
        intake = _order_intake(row)
        if (row.get("payment_status") != "COMPLETED"
                or (row.get("package_type") != "all_access" and intake.get("package") != "all_access")):
            raise HTTPException(status_code=409, detail="This order is not an active All Access pass")
        if str(row.get("customer_email") or "").strip().lower() != str(request.customerEmail).strip().lower():
            raise HTTPException(status_code=403, detail="The purchasing email does not match this 30-Day Access Code")
        expires_raw = row.get("access_expires_at")
        if not expires_raw:
            paid_raw = row.get("paid_at")
            if not paid_raw:
                raise HTTPException(status_code=409, detail="This All Access pass does not have a valid activation date")
            paid_dt = datetime.fromisoformat(str(paid_raw).replace("Z", "+00:00"))
            expires_dt = paid_dt + timedelta(days=30)
        else:
            expires_dt = datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))
        if expires_dt.tzinfo is None:
            expires_dt = expires_dt.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_dt:
            raise HTTPException(status_code=410, detail="This 30-Day All Access pass has expired")

        request_reference = "MYCP-REQ-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + secrets.token_hex(3).upper()
        payload = {
            "request_reference": request_reference,
            "access_order_reference": row["order_reference"],
            "customer_email": row["customer_email"],
            "clinic_name": row.get("clinic_name"),
            "treatment": request.treatment.strip(),
            "request_type": request.requestType,
            "request_details": {"notes": request.notes.strip()},
            "status": "RECEIVED",
        }
        await _supabase_request(client, "POST", "/rest/v1/all_access_requests", payload=payload, prefer="return=minimal")

    customer_email_sent = await _send_email(
        [str(request.customerEmail)],
        f"MYCP All Access request received — {request_reference}",
        f"<p>We received your request for <strong>{request.treatment}</strong>.</p><p>Request: {request_reference}</p><p>All Access order: {row['order_reference']}</p><p>We’ll prepare the requested documents using your clinic profile and submitted details. Please do not send PHI by email.</p>")
    owner_email_sent = await _send_email(
        [OWNER_EMAIL],
        f"ALL ACCESS REQUEST — {request_reference}",
        f"<p>New All Access request.</p><p>Clinic: {row.get('clinic_name') or 'Not provided'}</p><p>Customer: {row['customer_email']}</p><p>Treatment: {request.treatment}</p><p>Type: {request.requestType}</p><p>All Access order: {row['order_reference']}</p><p>Request: {request_reference}</p>")
    return {
        "status": "RECEIVED",
        "requestReference": request_reference,
        "accessOrderReference": row["order_reference"],
        "accessExpiresAt": expires_dt.isoformat(),
        "emailDelivery": {"customer": customer_email_sent, "owner": owner_email_sent},
    }


@app.get("/api/download/{reference}")
async def download(reference: str, expires: int, signature: str):
    if expires < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=410, detail="Download link expired")
    if not hmac.compare_digest(signature, _sign(reference, expires)):
        raise HTTPException(status_code=403, detail="Invalid download link")
    async with httpx.AsyncClient(timeout=25) as client:
        row = await _get_order(client, reference=reference)
        if not row or row["payment_status"] != "COMPLETED" or not row.get("package_storage_path"):
            raise HTTPException(status_code=404, detail="Package not found")
        storage_path = row["package_storage_path"]
        if storage_path.startswith("local:"):
            local_path = Path(storage_path[6:])
            if not local_path.is_file():
                raise HTTPException(status_code=404, detail="Package not found")
            return FileResponse(local_path, filename=f"{reference}-INITIAL-VERSION.zip", media_type="application/zip")
        package_bytes = await _storage_download(client, storage_path)
    return Response(package_bytes, media_type="application/zip",
                    headers={"Content-Disposition": f'attachment; filename="{reference}-INITIAL-VERSION.zip"'})


@app.get("/health")
async def health():
    configured = bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))
    database = "not-configured"
    storage = "not-configured"
    if configured:
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                response = await _supabase_request(client, "GET", "/rest/v1/orders", params={"select": "id", "limit": "1"})
                database = "ok" if response.status_code < 400 else "unavailable"
                url, _ = _supabase_config()
                bucket = quote(_storage_bucket(), safe="")
                storage_response = await client.get(f"{url}/storage/v1/bucket/{bucket}", headers=_storage_headers())
                storage = "ok" if storage_response.status_code < 400 else "unavailable"
        except Exception:
            logging.exception("Supabase health check failed")
            database = "unavailable"
            storage = "unavailable"
    return {"status": "ok", "pricingVersion": PRICING_VERSION, "paymentMode": os.environ.get("PAYPAL_MODE", "sandbox"),
            "emailConfigured": _email_configured(), "supabaseConfigured": configured, "database": database, "storage": storage}
