"""PayPal-verified private fulfillment API.

The public website must never decide that an order is paid. It creates an
order here, sends the buyer to PayPal, and asks this service to capture it.
Only a verified COMPLETED capture at the server-calculated price releases a
draft package.
"""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field

from fulfillment.documents import make_package


OWNER_EMAIL = "myclinicprotocols@gmail.com"
PRICES = {
    "protocol": {1: 99, 3: 249, 5: 379, 10: 699},
    "complete": {1: 149, 3: 399, 5: 625, 10: 1099},
}
ROOT = Path(os.environ.get("MYCP_PRIVATE_ROOT", "private-orders")).resolve()
ROOT.mkdir(parents=True, exist_ok=True)
DB = ROOT / "orders.sqlite3"
DOWNLOAD_TTL = timedelta(hours=24)


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
    orderReference: str
    paypalOrderId: str


app = FastAPI(title="MyClinicProtocols Fulfillment", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com")],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS orders (
        reference TEXT PRIMARY KEY, paypal_id TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL, amount TEXT NOT NULL, currency TEXT NOT NULL,
        status TEXT NOT NULL, intake TEXT NOT NULL, package_path TEXT,
        created_at TEXT NOT NULL, paid_at TEXT
    )""")
    return db


def _price(package: str, count: int) -> int:
    try:
        return PRICES[package][count]
    except KeyError as error:
        raise HTTPException(status_code=400, detail="Unsupported package or treatment quantity") from error


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
    response = await client.request(
        method, f"{_paypal_base()}{path}", json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
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
    with _connect() as db:
        db.execute(
            "INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?)",
            (reference, paypal["id"], str(checkout.customerEmail), amount, "USD", "CREATED",
             checkout.model_dump_json(), None, datetime.now(timezone.utc).isoformat(), None),
        )
    approval = next(link["href"] for link in paypal.get("links", []) if link.get("rel") == "payer-action")
    return {"orderReference": reference, "paypalOrderId": paypal["id"], "approvalUrl": approval}


@app.post("/api/checkout/capture")
async def capture_checkout(capture: Capture):
    with _connect() as db:
        row = db.execute("SELECT * FROM orders WHERE reference=? AND paypal_id=?", (capture.orderReference, capture.paypalOrderId)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    if row["status"] == "COMPLETED":
        return {"status": "COMPLETED", "downloadUrl": _download_url(row["reference"])}
    async with httpx.AsyncClient(timeout=25) as client:
        result = await _paypal(client, "POST", f"/v2/checkout/orders/{row['paypal_id']}/capture")
    unit = result.get("purchase_units", [{}])[0]
    capture_data = unit.get("payments", {}).get("captures", [{}])[0]
    amount = capture_data.get("amount", {})
    if (result.get("status") != "COMPLETED" or capture_data.get("status") != "COMPLETED"
            or unit.get("custom_id") != row["reference"] or amount.get("value") != row["amount"]
            or amount.get("currency_code") != row["currency"]):
        raise HTTPException(status_code=409, detail="Payment could not be verified")
    order = json.loads(row["intake"])
    order["orderReference"] = row["reference"]
    package_path = ROOT / row["reference"] / "draft-package.zip"
    package_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    package_path.write_bytes(make_package(order))
    paid_at = datetime.now(timezone.utc).isoformat()
    with _connect() as db:
        db.execute("UPDATE orders SET status='COMPLETED', package_path=?, paid_at=? WHERE reference=?",
                   (str(package_path), paid_at, row["reference"]))
    url = _download_url(row["reference"])
    customer_email_sent = await _send_email(
        [row["email"]],
        f"Your MyClinicProtocols draft — {row['reference']}",
        f"<p>Payment confirmed.</p><p><a href='{url}'>Download your draft DOCX + PDF package</a>. This private link expires in 24 hours.</p><p><strong>DRAFT — Qualified Provider Review Required.</strong></p><p>Your RN-reviewed version is normally delivered within 1–2 hours and may take up to 24 hours depending on the document set.</p>",
    )
    owner_email_sent = await _send_email(
        [OWNER_EMAIL], f"Paid MYCP order — {row['reference']}",
        f"<p>A verified payment of ${row['amount']} USD was received.</p><p>Customer: {row['email']}</p><p>Order: {row['reference']}</p>",
    )
    return {
        "status": "COMPLETED",
        "downloadUrl": url,
        "emailDelivery": {"customer": customer_email_sent, "owner": owner_email_sent},
    }


@app.get("/api/download/{reference}")
async def download(reference: str, expires: int, signature: str, request: Request):
    if expires < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=410, detail="Download link expired")
    if not hmac.compare_digest(signature, _sign(reference, expires)):
        raise HTTPException(status_code=403, detail="Invalid download link")
    with _connect() as db:
        row = db.execute("SELECT * FROM orders WHERE reference=? AND status='COMPLETED'", (reference,)).fetchone()
    if not row or not row["package_path"] or not Path(row["package_path"]).is_file():
        raise HTTPException(status_code=404, detail="Package not found")
    return FileResponse(row["package_path"], filename=f"{reference}-DRAFT.zip", media_type="application/zip")


@app.get("/health")
async def health():
    return {"status": "ok"}
