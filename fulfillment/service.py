"""PayPal-verified private fulfillment API.

The public website must never decide that an order is paid. It creates an
order here, sends the buyer to PayPal, and asks this service to capture it.
Only a verified COMPLETED capture at the server-calculated price releases a
draft package.

Order/payment state is persisted in Supabase so it survives Render restarts.
Generated packages are uploaded to the private Supabase Storage bucket when
available, with a local fallback so a verified payment is never stranded by a
transient storage error.
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

from fulfillment.documents import make_package


OWNER_EMAIL = "myclinicprotocols@gmail.com"
PRICES = {
    "protocol": {1: 99, 3: 249, 5: 379, 10: 699},
    "complete": {1: 149, 3: 399, 5: 625, 10: 1099},
}
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


class Capture(BaseModel):
    orderReference: str | None = None
    paypalOrderId: str


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


async def _supabase_request(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    params: dict | None = None,
    payload: dict | None = None,
    prefer: str | None = None,
) -> httpx.Response:
    url, key = _supabase_config()
    headers = {"apikey": key, "Content-Type": "application/json"}
    if prefer:
        headers["Prefer"] = prefer
    response = await client.request(
        method,
        f"{url}{path}",
        params=params,
        json=payload,
        headers=headers,
    )
    if response.status_code >= 400:
        logging.error("Supabase request failed: %s %s -> %s", method, path, response.status_code)
        raise HTTPException(status_code=503, detail="Order database is temporarily unavailable")
    return response


async def _insert_order(client: httpx.AsyncClient, checkout: Checkout, reference: str, paypal_id: str, amount: str) -> None:
    clinic = checkout.clinic or {}
    details = checkout.details or {}
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
        "intake": checkout.model_dump(mode="json"),
    }
    await _supabase_request(
        client,
        "POST",
        "/rest/v1/orders",
        payload=row,
        prefer="return=minimal",
    )


async def _get_order(client: httpx.AsyncClient, *, reference: str | None = None, paypal_id: str | None = None) -> dict | None:
    params: dict[str, str] = {"select": "*", "limit": "1"}
    if reference:
        params["order_reference"] = f"eq.{reference}"
    if paypal_id:
        params["paypal_order_id"] = f"eq.{paypal_id}"
    response = await _supabase_request(client, "GET", "/rest/v1/orders", params=params)
    rows = response.json()
    return rows[0] if rows else None


async def _update_order(client: httpx.AsyncClient, reference: str, values: dict) -> None:
    values = {**values, "updated_at": datetime.now(timezone.utc).isoformat()}
    await _supabase_request(
        client,
        "PATCH",
        "/rest/v1/orders",
        params={"order_reference": f"eq.{reference}"},
        payload=values,
        prefer="return=minimal",
    )


def _storage_headers() -> dict[str, str]:
    _, key = _supabase_config()
    return {"apikey": key, "Authorization": f"Bearer {key}"}


async def _storage_upload(client: httpx.AsyncClient, storage_path: str, package_bytes: bytes) -> bool:
    """Upload to the private Supabase bucket. Return False for a safe local fallback."""
    try:
        url, _ = _supabase_config()
        bucket = quote(_storage_bucket(), safe="")
        object_path = quote(storage_path, safe="/")
        response = await client.post(
            f"{url}/storage/v1/object/{bucket}/{object_path}",
            content=package_bytes,
            headers={**_storage_headers(), "Content-Type": "application/zip", "x-upsert": "true"},
        )
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
    response = await client.get(
        f"{url}/storage/v1/object/authenticated/{bucket}/{object_path}",
        headers=_storage_headers(),
    )
    if response.status_code >= 400:
        logging.error("Supabase Storage download failed with status %s", response.status_code)
        raise HTTPException(status_code=404, detail="Package not found")
    return response.content


@app.on_event("startup")
async def verify_supabase_connectivity() -> None:
    """Log safe connectivity status at deploy time without exposing credentials."""
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        logging.warning("Supabase is not configured in this Render environment")
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await _supabase_request(
                client,
                "GET",
                "/rest/v1/orders",
                params={"select": "id", "limit": "1"},
            )
            logging.info("Supabase database connectivity OK")

            url, _ = _supabase_config()
            bucket = quote(_storage_bucket(), safe="")
            storage = await client.get(
                f"{url}/storage/v1/bucket/{bucket}",
                headers=_storage_headers(),
            )
            if storage.status_code < 400:
                logging.info("Supabase Storage connectivity OK for private bucket %s", _storage_bucket())
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
    response = await client.post(
        f"{_paypal_base()}/v1/oauth2/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, secret),
    )
    response.raise_for_status()
    return response.json()["access_token"]


async def _paypal(client: httpx.AsyncClient, method: str, path: str, payload: dict | None = None) -> dict:
    token = await _paypal_token(client)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json",
               "Prefer": "return=representation"}
    if method == "POST" and path.endswith("/capture"):
        headers["PayPal-Request-Id"] = "capture-" + path.split("/")[-2]
    response = await client.request(
        method, f"{_paypal_base()}{path}", json=payload,
        headers=headers,
    )
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
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}"},
            json={"from": sender, "to": to, "subject": subject, "html": html},
        )
        return response.status_code < 400


@app.post("/api/checkout/create")
async def create_checkout(checkout: Checkout):
    count = len(checkout.treatments)
    amount = f"{_price(checkout.package, count):.2f}"
    reference = "MYCP-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + secrets.token_hex(4).upper()
    return_url = os.environ.get("PAYPAL_RETURN_URL")
    cancel_url = os.environ.get("PAYPAL_CANCEL_URL")
    if not return_url or not cancel_url:
        raise HTTPException(status_code=503, detail="Payment return URLs are not configured")
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "custom_id": reference,
            "invoice_id": reference,
            "description": "MyClinicProtocols customized document package",
            "amount": {"currency_code": "USD", "value": amount},
        }],
        "payment_source": {"paypal": {"experience_context": {
            "brand_name": "MyClinicProtocols",
            "user_action": "PAY_NOW",
            "return_url": return_url,
            "cancel_url": cancel_url,
        }}},
    }
    async with httpx.AsyncClient(timeout=25) as client:
        paypal = await _paypal(client, "POST", "/v2/checkout/orders", payload)
        await _insert_order(client, checkout, reference, paypal["id"], amount)
    approval = next(link["href"] for link in paypal.get("links", []) if link.get("rel") == "payer-action")
    return {"orderReference": reference, "paypalOrderId": paypal["id"], "approvalUrl": approval}


def _row_amount(row: dict) -> str:
    return f"{Decimal(str(row['payment_amount'])):.2f}"


def _verify_paypal_order(result: dict, row: dict, *, require_capture: bool) -> None:
    """Verify the full order fetched from PayPal, never a minimal POST response."""
    units = result.get("purchase_units") or []
    unit = units[0] if len(units) == 1 else {}
    expected_amount = {"value": _row_amount(row), "currency_code": row["currency"]}
    valid = (result.get("id") == row["paypal_order_id"]
             and result.get("intent") == "CAPTURE"
             and unit.get("custom_id") == row["order_reference"]
             and unit.get("invoice_id") == row["order_reference"]
             and all(unit.get("amount", {}).get(k) == v for k, v in expected_amount.items()))
    if require_capture:
        captures = unit.get("payments", {}).get("captures") or []
        payment = captures[0] if len(captures) == 1 else {}
        valid = (valid and result.get("status") == "COMPLETED"
                 and payment.get("status") == "COMPLETED"
                 and bool(payment.get("id"))
                 and all(payment.get("amount", {}).get(k) == v for k, v in expected_amount.items()))
    if not valid:
        logging.warning("PayPal verification failed for %s (order status %s)",
                        row["order_reference"], result.get("status"))
        raise HTTPException(status_code=409, detail="Payment could not be verified")


@app.post("/api/checkout/capture")
async def capture_checkout(capture: Capture):
    async with httpx.AsyncClient(timeout=25) as client:
        row = await _get_order(
            client,
            reference=capture.orderReference,
            paypal_id=capture.paypalOrderId,
        )
        if not row:
            raise HTTPException(status_code=404, detail="Order not found")
        if row["payment_status"] == "COMPLETED":
            return {
                "status": "COMPLETED",
                "orderReference": row["order_reference"],
                "downloadUrl": _download_url(row["order_reference"]),
            }

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

        order = row.get("intake") or {}
        if isinstance(order, str):
            order = json.loads(order)
        order["orderReference"] = row["order_reference"]
        package_bytes = make_package(order)
        storage_path = f"{row['order_reference']}/draft-package.zip"
        stored_in_supabase = await _storage_upload(client, storage_path, package_bytes)
        if not stored_in_supabase:
            local_path = ROOT / row["order_reference"] / "draft-package.zip"
            local_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            local_path.write_bytes(package_bytes)
            storage_path = "local:" + str(local_path)

        paid_at = datetime.now(timezone.utc).isoformat()
        await _update_order(client, row["order_reference"], {
            "payment_status": "COMPLETED",
            "package_storage_path": storage_path,
            "paid_at": paid_at,
        })

    url = _download_url(row["order_reference"])
    customer_email_sent = await _send_email(
        [row["customer_email"]],
        f"Your MyClinicProtocols draft — {row['order_reference']}",
        f"<p>Payment confirmed.</p><p><a href='{url}'>Download your draft DOCX + PDF package</a>. This private link expires in 24 hours.</p><p><strong>DRAFT — Qualified Provider Review Required.</strong></p><p>Your RN-reviewed version is normally delivered within 1–2 hours and may take up to 24 hours depending on the document set.</p>",
    )
    owner_email_sent = await _send_email(
        [OWNER_EMAIL], f"Paid MYCP order — {row['order_reference']}",
        f"<p>A verified payment of ${_row_amount(row)} USD was received.</p><p>Customer: {row['customer_email']}</p><p>Order: {row['order_reference']}</p>",
    )
    async with httpx.AsyncClient(timeout=15) as client:
        await _update_order(client, row["order_reference"], {"email_delivery": customer_email_sent})
    return {
        "status": "COMPLETED",
        "orderReference": row["order_reference"],
        "downloadUrl": url,
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
            return FileResponse(local_path, filename=f"{reference}-DRAFT.zip", media_type="application/zip")
        package_bytes = await _storage_download(client, storage_path)

    return Response(
        package_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{reference}-DRAFT.zip"'},
    )


@app.get("/health")
async def health():
    configured = bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"))
    database = "not-configured"
    storage = "not-configured"
    if configured:
        try:
            async with httpx.AsyncClient(timeout=8) as client:
                response = await _supabase_request(
                    client,
                    "GET",
                    "/rest/v1/orders",
                    params={"select": "id", "limit": "1"},
                )
                database = "ok" if response.status_code < 400 else "unavailable"
                url, _ = _supabase_config()
                bucket = quote(_storage_bucket(), safe="")
                storage_response = await client.get(
                    f"{url}/storage/v1/bucket/{bucket}",
                    headers=_storage_headers(),
                )
                storage = "ok" if storage_response.status_code < 400 else "unavailable"
        except Exception:
            logging.exception("Supabase health check failed")
            database = "unavailable"
            storage = "unavailable"
    return {
        "status": "ok",
        "supabaseConfigured": configured,
        "database": database,
        "storage": storage,
    }
