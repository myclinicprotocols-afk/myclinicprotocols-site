from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
service = ROOT / "fulfillment" / "service.py"


def replace_once(old: str, new: str) -> None:
    text = service.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Expected backend text not found: {old[:120]!r}")
    service.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
'''PRICES = {
    "protocol": {1: 29, 2: 58, 3: 87, 4: 116, 5: 145, 6: 174, 7: 203, 8: 232, 9: 261, 10: 290},
    "complete": {1: 49, 2: 98, 3: 147, 4: 196, 5: 245, 6: 294, 7: 343, 8: 392, 9: 441, 10: 490},
}
PRICING_VERSION = "2026-10-09-2"''',
'''PRICES = {
    "protocol": {1: 29, 2: 58, 3: 87, 4: 116, 5: 145, 6: 174, 7: 203, 8: 232, 9: 261, 10: 290},
    "complete": {1: 49, 2: 98, 3: 147, 4: 196, 5: 245, 6: 294, 7: 343, 8: 392, 9: 441, 10: 490},
    "all_access": {1: 249},
}
PRICING_VERSION = "2026-10-10"''')

replace_once(
'''class Capture(BaseModel):
    orderReference: str | None = None
    paypalOrderId: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9-]+$")
''',
'''class Capture(BaseModel):
    orderReference: str | None = None
    paypalOrderId: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9-]+$")


class AllAccessRequest(BaseModel):
    orderReference: str = Field(min_length=10, max_length=64, pattern=r"^MYCP-[A-Z0-9-]+$")
    customerEmail: EmailStr
    treatment: str = Field(min_length=2, max_length=200)
    requestType: str = Field(default="complete", pattern=r"^(protocol|complete)$")
    notes: str = Field(default="", max_length=5000)
''')

replace_once(
'    intake["_fulfillmentMode"] = _fulfillment_mode(checkout.treatments)',
'    intake["_fulfillmentMode"] = "all_access" if checkout.package == "all_access" else _fulfillment_mode(checkout.treatments)')

replace_once(
'''    fulfillment_mode = _fulfillment_mode(checkout.treatments)
    if fulfillment_mode == "manual" and not _email_configured():''',
'''    fulfillment_mode = "all_access" if checkout.package == "all_access" else _fulfillment_mode(checkout.treatments)
    if fulfillment_mode == "manual" and not _email_configured():''')

replace_once(
'"description": "MyClinicProtocols customized document package",',
'"description": "MyClinicProtocols 30-Day All Access" if checkout.package == "all_access" else "MyClinicProtocols customized document package",')

# Replace completed response so an All Access purchase is ACTIVE and links to its request portal rather than looking like a file package.
text = service.read_text(encoding="utf-8")
pattern = r"def _completed_response\(row: dict\) -> dict:\n.*?\n\n\ndef _verify_paypal_order"
replacement = '''def _completed_response(row: dict) -> dict:
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
        origin = os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com").rstrip("/")
        response["requestUrl"] = f"{origin}/all-access-request.html?ref={quote(row['order_reference'])}"
    return response


def _verify_paypal_order'''
updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise RuntimeError(f"Could not patch _completed_response; matches={count}")
service.write_text(updated, encoding="utf-8")

# Activate All Access immediately after PayPal verification and before normal document fulfillment.
replace_once(
'''        order = _order_intake(row)
        order["orderReference"] = row["order_reference"]
        fulfillment_mode = order.get("_fulfillmentMode") or _fulfillment_mode(order.get("treatments") or [])
        storage_path = None
''',
'''        order = _order_intake(row)
        order["orderReference"] = row["order_reference"]
        if order.get("package") == "all_access":
            paid_dt = datetime.now(timezone.utc)
            expires_dt = paid_dt + timedelta(days=30)
            paid_at = paid_dt.isoformat()
            access_expires_at = expires_dt.isoformat()
            order["_fulfillmentMode"] = "all_access"
            await _update_order(client, row["order_reference"], {
                "payment_status": "COMPLETED",
                "paid_at": paid_at,
                "access_starts_at": paid_at,
                "access_expires_at": access_expires_at,
                "package_storage_path": None,
                "intake": order,
            })
            row.update({"payment_status": "COMPLETED", "paid_at": paid_at, "access_starts_at": paid_at,
                        "access_expires_at": access_expires_at, "package_storage_path": None, "intake": order})
            origin = os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com").rstrip("/")
            request_url = f"{origin}/all-access-request.html?ref={quote(row['order_reference'])}"
            customer_email_sent = await _send_email(
                [row["customer_email"]],
                f"Your MYCP 30-Day All Access is active — {row['order_reference']}",
                f"<p>Payment confirmed — your 30-Day All Access is active.</p><p>Your access is valid through <strong>{expires_dt.strftime('%B %d, %Y')}</strong>.</p><p><a href='{request_url}'>Submit a protocol request</a> any time during your active period.</p><p>This pass is for one clinic/legal practice and is non-transferable. Specialty or investigational requests may require scope review. Please do not submit PHI.</p>")
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
''')

request_endpoint = '''\n\n@app.post("/api/all-access/request")\nasync def submit_all_access_request(request: AllAccessRequest):\n    async with httpx.AsyncClient(timeout=20) as client:\n        row = await _get_order(client, reference=request.orderReference)\n        if not row:\n            raise HTTPException(status_code=404, detail="All Access order not found")\n        intake = _order_intake(row)\n        if (row.get("payment_status") != "COMPLETED"\n                or (row.get("package_type") != "all_access" and intake.get("package") != "all_access")):\n            raise HTTPException(status_code=409, detail="This order is not an active All Access pass")\n        if str(row.get("customer_email") or "").strip().lower() != str(request.customerEmail).strip().lower():\n            raise HTTPException(status_code=403, detail="The order email does not match this All Access pass")\n        expires_raw = row.get("access_expires_at")\n        if not expires_raw:\n            paid_raw = row.get("paid_at")\n            if not paid_raw:\n                raise HTTPException(status_code=409, detail="This All Access pass does not have a valid activation date")\n            paid_dt = datetime.fromisoformat(str(paid_raw).replace("Z", "+00:00"))\n            expires_dt = paid_dt + timedelta(days=30)\n        else:\n            expires_dt = datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))\n        if expires_dt.tzinfo is None:\n            expires_dt = expires_dt.replace(tzinfo=timezone.utc)\n        if datetime.now(timezone.utc) > expires_dt:\n            raise HTTPException(status_code=410, detail="This 30-Day All Access pass has expired")\n\n        request_reference = "MYCP-REQ-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + secrets.token_hex(3).upper()\n        payload = {\n            "request_reference": request_reference,\n            "access_order_reference": row["order_reference"],\n            "customer_email": row["customer_email"],\n            "clinic_name": row.get("clinic_name"),\n            "treatment": request.treatment.strip(),\n            "request_type": request.requestType,\n            "request_details": {"notes": request.notes.strip()},\n            "status": "RECEIVED",\n        }\n        await _supabase_request(client, "POST", "/rest/v1/all_access_requests", payload=payload, prefer="return=minimal")\n\n    customer_email_sent = await _send_email(\n        [str(request.customerEmail)],\n        f"MYCP All Access request received — {request_reference}",\n        f"<p>We received your request for <strong>{request.treatment}</strong>.</p><p>Request: {request_reference}</p><p>All Access order: {request.orderReference}</p><p>We’ll prepare the requested documents using your clinic profile and submitted details. Please do not send PHI by email.</p>")\n    owner_email_sent = await _send_email(\n        [OWNER_EMAIL],\n        f"ALL ACCESS REQUEST — {request_reference}",\n        f"<p>New All Access request.</p><p>Clinic: {row.get('clinic_name') or 'Not provided'}</p><p>Customer: {row['customer_email']}</p><p>Treatment: {request.treatment}</p><p>Type: {request.requestType}</p><p>All Access order: {request.orderReference}</p><p>Request: {request_reference}</p>")\n    return {\n        "status": "RECEIVED",\n        "requestReference": request_reference,\n        "accessOrderReference": request.orderReference,\n        "accessExpiresAt": expires_dt.isoformat(),\n        "emailDelivery": {"customer": customer_email_sent, "owner": owner_email_sent},\n    }\n'''
text = service.read_text(encoding="utf-8")
if '@app.post("/api/all-access/request")' not in text:
    marker = '\n\n@app.get("/api/download/{reference}")'
    if marker not in text:
        raise RuntimeError("Download endpoint marker not found")
    service.write_text(text.replace(marker, request_endpoint + marker, 1), encoding="utf-8")

print("All Access backend patch applied")
