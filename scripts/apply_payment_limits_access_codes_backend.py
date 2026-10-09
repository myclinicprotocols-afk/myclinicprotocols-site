from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / 'fulfillment' / 'service.py'
text = SERVICE.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str):
    global text
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f'Expected backend text not found for {label}')
    text = text.replace(old, new, 1)


replace_once(
'''PRICES = {
    "protocol": {1: 29, 2: 58, 3: 87, 4: 116, 5: 145, 6: 174, 7: 203, 8: 232, 9: 261, 10: 290},
    "complete": {1: 49, 2: 98, 3: 147, 4: 196, 5: 245, 6: 294, 7: 343, 8: 392, 9: 441, 10: 490},
    "all_access": {1: 249},
}
PRICING_VERSION = "2026-10-10"''',
'''PRICES = {
    "protocol": {1: 29, 2: 58, 3: 87, 4: 116, 5: 145, 6: 174, 7: 203, 8: 232},
    "complete": {1: 49, 2: 98, 3: 147, 4: 196, 5: 245},
    "all_access": {1: 249},
}
PRICING_VERSION = "2026-10-10-2"''',
'pricing caps and version')

replace_once(
'''class AllAccessRequest(BaseModel):
    orderReference: str = Field(min_length=10, max_length=64, pattern=r"^MYCP-[A-Z0-9-]+$")
    customerEmail: EmailStr''',
'''class AllAccessRequest(BaseModel):
    accessCode: str = Field(min_length=20, max_length=64, pattern=r"^MYCP-[A-Z0-9-]+$")
    customerEmail: EmailStr''',
'access request credential')

replace_once(
'''def _email_configured() -> bool:
    return bool(os.environ.get("RESEND_API_KEY") and os.environ.get("ORDER_FROM_EMAIL"))


def _supabase_config()''',
'''def _email_configured() -> bool:
    return bool(os.environ.get("RESEND_API_KEY") and os.environ.get("ORDER_FROM_EMAIL"))


def _new_access_code() -> str:
    """Create a high-entropy, human-readable 30-day license code after verified payment."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    groups = ["".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(4)]
    return "MYCP-" + "-".join(groups)


def _supabase_config()''',
'access code generator')

replace_once(
'''    rows = response.json()
    return rows[0] if rows else None


async def _update_order''',
'''    rows = response.json()
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


async def _update_order''',
'access code lookup')

replace_once(
'''    if package_key == "all_access":
        response["accessStartsAt"] = row.get("access_starts_at") or row.get("paid_at")
        response["accessExpiresAt"] = row.get("access_expires_at")
        origin = os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com").rstrip("/")
        response["requestUrl"] = f"{origin}/all-access-request.html?ref={quote(row['order_reference'])}"''',
'''    if package_key == "all_access":
        response["accessStartsAt"] = row.get("access_starts_at") or row.get("paid_at")
        response["accessExpiresAt"] = row.get("access_expires_at")
        response["accessCode"] = row.get("access_code")
        origin = os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com").rstrip("/")
        response["requestUrl"] = f"{origin}/all-access-request.html"''',
'completed response access code')

replace_once(
'''        if row["payment_status"] == "COMPLETED":
            return _completed_response(row)''',
'''        if row["payment_status"] == "COMPLETED":
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
            return _completed_response(row)''',
'legacy all access code issuance')

replace_once(
'''            access_expires_at = expires_dt.isoformat()
            order["_fulfillmentMode"] = "all_access"''',
'''            access_expires_at = expires_dt.isoformat()
            access_code = row.get("access_code") or _new_access_code()
            access_code_issued_at = datetime.now(timezone.utc).isoformat()
            order["_fulfillmentMode"] = "all_access"''',
'generate access code after payment')

replace_once(
'''                "access_expires_at": access_expires_at,
                "package_storage_path": None,
                "intake": order,''',
'''                "access_expires_at": access_expires_at,
                "access_code": access_code,
                "access_code_issued_at": access_code_issued_at,
                "package_storage_path": None,
                "intake": order,''',
'persist access code')

replace_once(
'''            row.update({"payment_status": "COMPLETED", "paid_at": paid_at, "access_starts_at": paid_at,
                        "access_expires_at": access_expires_at, "package_storage_path": None, "intake": order})''',
'''            row.update({"payment_status": "COMPLETED", "paid_at": paid_at, "access_starts_at": paid_at,
                        "access_expires_at": access_expires_at, "access_code": access_code,
                        "access_code_issued_at": access_code_issued_at, "package_storage_path": None, "intake": order})''',
'row access code state')

replace_once(
'''            request_url = f"{origin}/all-access-request.html?ref={quote(row['order_reference'])}"''',
'''            request_url = f"{origin}/all-access-request.html"''',
'clean request portal URL')

replace_once(
'''                f"<p>Payment confirmed — your 30-Day All Access is active.</p><p>Your access is valid through <strong>{expires_dt.strftime('%B %d, %Y')}</strong>.</p><p><a href='{request_url}'>Submit a protocol request</a> any time during your active period.</p><p>This pass is for one clinic/legal practice and is non-transferable. Specialty or investigational requests may require scope review. Please do not submit PHI.</p>")''',
'''                f"<p>Payment confirmed — your 30-Day All Access is active.</p><p>Your access is valid through <strong>{expires_dt.strftime('%B %d, %Y')}</strong>.</p><p>Your 30-Day Access Code is <strong>{access_code}</strong>.</p><p><a href='{request_url}'>Open the All Access Request Portal</a> and use this code with your purchasing email any time during your active period.</p><p>This pass is for one clinic/legal practice and is non-transferable. Specialty or investigational requests may require scope review. Please do not submit PHI.</p>")''',
'activation email access code')

replace_once(
'''        row = await _get_order(client, reference=request.orderReference)
        if not row:
            raise HTTPException(status_code=404, detail="All Access order not found")''',
'''        row = await _get_all_access_order_by_code(client, request.accessCode.strip().upper())
        if not row:
            raise HTTPException(status_code=404, detail="Access code not found")''',
'request access code lookup')

text = text.replace('The order email does not match this All Access pass', 'The purchasing email does not match this 30-Day Access Code')
text = text.replace("<p>All Access order: {request.orderReference}</p>", "<p>All Access order: {row['order_reference']}</p>")
text = text.replace("<p>All Access order: {request.orderReference}</p><p>Request: {request_reference}</p>", "<p>All Access order: {row['order_reference']}</p><p>Request: {request_reference}</p>")
text = text.replace('"accessOrderReference": request.orderReference,', '"accessOrderReference": row["order_reference"],')

SERVICE.write_text(text, encoding='utf-8')
