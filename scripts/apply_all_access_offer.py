from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def must_replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Expected text not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def must_regex(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Expected one regex match in {path}, found {count}: {pattern}")
    path.write_text(updated, encoding="utf-8")


index = ROOT / "index.html"
commerce = ROOT / "assets" / "mycp-commerce.js"
support = ROOT / "assets" / "mycp-search-support.js"
service = ROOT / "fulfillment" / "service.py"
checkout_return = ROOT / "checkout-return.html"

# Homepage pricing: replace the old bundle card with the 30-Day All Access offer.
must_replace(
    index,
    '<div class="section-head"><div class="section-kicker">Pricing</div><h2>More complete documentation. Simple pricing.</h2><p>Choose a customized protocol for $29 or add the supporting documents for just $20 more. Both options include RN review and two consolidated revision rounds.</p></div>',
    '<div class="section-head"><div class="section-kicker">Pricing</div><h2>More complete documentation. Simple pricing.</h2><p>Choose a customized protocol for $29, a Complete Treatment Package for $49, or get 30 days of All Access for $249. All options are prepared for qualified provider review.</p></div>',
)
must_replace(
    index,
    '<div class="price"><h3>Multiple Treatments</h3><div class="amount">From $87</div><p>Choose different treatments at the same package level.</p><ul><li>3 Customized Protocols - $87</li><li>5 Customized Protocols - $145</li><li>10 Customized Protocols - $290</li><li>3 Complete Packages - $147</li><li>5 Complete Packages - $245</li><li>10 Complete Packages - $490</li></ul><button class="btn-secondary choose-plan" data-plan="Complete Treatment Package" data-price="49">Build a Bundle</button></div>',
    '<div class="price featured"><span class="badge">BEST VALUE</span><h3>30-Day All Access</h3><div class="amount">$249 <small>/ 30 days</small></div><p>One clinic can request as many eligible protocols and Complete Treatment Packages as needed during the active 30-day period.</p><ul><li>Any eligible protocol in the MYCP library</li><li>Complete Treatment Packages included</li><li>Multiple requests throughout the month</li><li>State, provider, product, device, workflow &amp; branding customization</li><li>Editable Word + polished PDF deliverables</li><li>RN-prepared and quality-checked</li><li>Up to two consolidated revision rounds per delivered request</li></ul><a class="btn-primary" href="all-access.html">Get 30-Day All Access</a></div>',
)
must_replace(
    index,
    '<p class="price-note">Prices are in USD, per treatment. Order 1, 3, 5, or 10 treatments at the same $29 protocol or $49 complete-package rate.</p>',
    '<p class="price-note">Prices are in USD. Individual protocols are $29 per treatment and Complete Treatment Packages are $49 per treatment. The $249 All Access pass is a one-time purchase valid for 30 days for one clinic/legal practice; it does not auto-renew.</p>',
)
# Add the offer to structured data.
must_replace(
    index,
    '''        {
          "@type": "Offer",
          "name": "Complete Treatment Package",
          "price": "49",
          "priceCurrency": "USD",
          "url": "https://myclinicprotocols.com/order.html?package=complete",
          "availability": "https://schema.org/InStock"
        }
      ]''',
    '''        {
          "@type": "Offer",
          "name": "Complete Treatment Package",
          "price": "49",
          "priceCurrency": "USD",
          "url": "https://myclinicprotocols.com/order.html?package=complete",
          "availability": "https://schema.org/InStock"
        },
        {
          "@type": "Offer",
          "name": "30-Day All Access",
          "price": "249",
          "priceCurrency": "USD",
          "url": "https://myclinicprotocols.com/all-access.html",
          "availability": "https://schema.org/InStock"
        }
      ]''',
)

# Shared commerce: add All Access analytics and bump pricing contract version.
must_replace(commerce, "const VERSION = '2026-10-09-2';", "const VERSION = '2026-10-10';")
must_replace(
    commerce,
    "const names = {protocol: 'Customized Protocol', complete: 'Complete Treatment Package'};",
    "const names = {protocol: 'Customized Protocol', complete: 'Complete Treatment Package', all_access: '30-Day All Access'};",
)

# Website assistant: explain the new offer instead of presenting the old bundles as the main value proposition.
must_replace(
    support,
    """  const PRICING={
    protocol:{label:'Customized Protocol',prices:{1:29,3:87,5:145,10:290}},
    complete:{label:'Complete Treatment Package',prices:{1:49,3:147,5:245,10:490}}
  };""",
    """  const PRICING={
    protocol:{label:'Customized Protocol',prices:{1:29,3:87,5:145,10:290}},
    complete:{label:'Complete Treatment Package',prices:{1:49,3:147,5:245,10:490}},
    allAccess:{label:'30-Day All Access',price:249}
  };""",
)
must_regex(
    support,
    r"  function priceText\(\)\{.*?\n  \}\n",
    """  function priceText(){
    return `Current pricing in USD is:
Customized Protocol - $29 per treatment.
Complete Treatment Package - $49 per treatment.
30-Day All Access - $249 one-time for 30 days for one clinic/legal practice.

All Access lets the purchasing clinic submit as many eligible protocol and Complete Treatment Package requests as needed during the active 30-day period. It does not automatically renew.`;
  }
""",
)
marker = "    if(hasAny(q,['price','pricing','cost','how much','bundle price','founding price','29','49','87','145','290','147','245','490'])){"
all_access_answer = """    if(hasAny(q,['all access','all-access','unlimited protocols','unlimited protocol','249','subscription','30-day','30 day access'])){
      return response(
        `MYCP offers a 30-Day All Access pass for $249. It is a one-time purchase, not an automatic renewal. One clinic/legal practice can submit as many eligible Customized Protocol or Complete Treatment Package requests as needed during the active 30-day period. Specialty or investigational requests may require scope review, and final clinical approval remains with the clinic’s qualified reviewer.`,
        links({label:'Get 30-Day All Access',href:'all-access.html'},{label:'View pricing',href:`${HOME_URL}#pricing`})
      );
    }

"""
text = support.read_text(encoding="utf-8")
if all_access_answer not in text:
    if marker not in text:
        raise RuntimeError("Pricing intent marker not found in support assistant")
    support.write_text(text.replace(marker, all_access_answer + marker, 1), encoding="utf-8")
must_replace(
    support,
    """        `Yes. You can select multiple treatments in one order and keep them together in a single clinic intake. Orders support 1, 3, 5, or 10 treatments at the same $29 per protocol or $49 per complete-package rate.`,
        links({label:'Build a multi-treatment package',href:ORDER_URL},{label:'See bundle pricing',href:`${HOME_URL}#pricing`})""",
    """        `Yes. You can select multiple treatments in one order at the regular $29 per protocol or $49 per Complete Treatment Package rate. If your clinic expects to request several protocols during the month, the $249 30-Day All Access pass is usually the better value and allows repeated eligible requests throughout the active period.`,
        links({label:'Get 30-Day All Access',href:'all-access.html'},{label:'Build a standard order',href:ORDER_URL})""",
)

# Backend pricing + activation + request portal.
must_replace(
    service,
    '''PRICES = {
    "protocol": {1: 29, 3: 87, 5: 145, 10: 290},
    "complete": {1: 49, 3: 147, 5: 245, 10: 490},
}
PRICING_VERSION = "2026-10-09"''',
    '''PRICES = {
    "protocol": {1: 29, 3: 87, 5: 145, 10: 290},
    "complete": {1: 49, 3: 147, 5: 245, 10: 490},
    "all_access": {1: 249},
}
PRICING_VERSION = "2026-10-10"''',
)
must_replace(
    service,
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
''',
)
# Allow normal orders that need manual preparation instead of blocking payment before checkout.
must_replace(
    service,
    '''@app.post("/api/checkout/create")
async def create_checkout(checkout: Checkout):
    try:
        validate_production_treatments(checkout.treatments)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    count = len(checkout.treatments)''',
    '''@app.post("/api/checkout/create")
async def create_checkout(checkout: Checkout):
    count = len(checkout.treatments)''',
)
must_replace(
    service,
    '"description": "MyClinicProtocols customized document package",',
    '"description": "MyClinicProtocols 30-Day All Access" if checkout.package == "all_access" else "MyClinicProtocols customized document package",',
)
# Completed responses only expose a download when a package actually exists; All Access returns its portal and expiry.
must_regex(
    service,
    r"def _completed_response\(row: dict\) -> dict:\n.*?\n\n\ndef _verify_paypal_order",
    '''def _completed_response(row: dict) -> dict:
    intake = _order_intake(row)
    package_key = intake.get("package")
    response = {
        "status": "COMPLETED",
        "orderReference": row["order_reference"],
        "downloadUrl": None,
        "amount": _row_amount(row),
        "currency": row.get("currency") or "USD",
        "paymentMode": intake.get("_paymentMode", "unknown"),
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
    elif row.get("package_storage_path"):
        response["downloadUrl"] = _download_url(row["order_reference"])
    return response


def _processing_response(row: dict) -> dict:
    intake = _order_intake(row)
    return {
        "status": "PROCESSING",
        "orderReference": row["order_reference"],
        "downloadUrl": None,
        "amount": _row_amount(row),
        "currency": row.get("currency") or "USD",
        "paymentMode": intake.get("_paymentMode", "unknown"),
        "package": intake.get("package"),
        "treatmentCount": len(intake.get("treatments") or []),
        "pricingVersion": intake.get("_pricingVersion"),
        "emailDelivery": {"customer": bool(row.get("email_delivery"))},
    }


def _verify_paypal_order''',
)
# Repeated return-page calls should not re-run fulfillment.
must_replace(
    service,
    '''        if row["payment_status"] == "COMPLETED":
            return _completed_response(row)
''',
    '''        if row["payment_status"] == "COMPLETED":
            return _completed_response(row)
        if row["payment_status"] == "PROCESSING":
            return _processing_response(row)
''',
)
# Add the All Access activation path before document generation.
must_replace(
    service,
    '''        order = _order_intake(row)
        order["orderReference"] = row["order_reference"]
        try:
            package_bytes = make_package(order)
        except ValueError as error:
            logging.error("Production master validation failed after payment for %s: %s", row["order_reference"], error)
            raise HTTPException(status_code=409, detail="The paid order needs manual fulfillment review before files can be released") from error
''',
    '''        order = _order_intake(row)
        order["orderReference"] = row["order_reference"]
        if order.get("package") == "all_access":
            paid_dt = datetime.now(timezone.utc)
            expires_dt = paid_dt + timedelta(days=30)
            paid_at = paid_dt.isoformat()
            access_expires_at = expires_dt.isoformat()
            await _update_order(client, row["order_reference"], {
                "payment_status": "COMPLETED",
                "paid_at": paid_at,
                "access_starts_at": paid_at,
                "access_expires_at": access_expires_at,
                "package_storage_path": None,
            })
            row.update({"payment_status": "COMPLETED", "paid_at": paid_at, "access_starts_at": paid_at, "access_expires_at": access_expires_at, "package_storage_path": None})
            origin = os.environ.get("WEBSITE_ORIGIN", "https://myclinicprotocols.com").rstrip("/")
            request_url = f"{origin}/all-access-request.html?ref={quote(row['order_reference'])}"
            customer_email_sent = await _send_email(
                [row["customer_email"]],
                f"Your MYCP 30-Day All Access is active - {row['order_reference']}",
                f"<p>Payment confirmed - your 30-Day All Access is active.</p><p>Your access is valid through <strong>{expires_dt.strftime('%B %d, %Y')}</strong>.</p><p><a href='{request_url}'>Submit a protocol request</a> any time during your active period.</p><p>This pass is for one clinic/legal practice and is non-transferable. Specialty or investigational requests may require scope review. Please do not submit PHI.</p>",
            )
            owner_email_sent = await _send_email(
                [OWNER_EMAIL],
                f"NEW $249 ALL ACCESS - {row['order_reference']}",
                f"<p>A verified $249 30-Day All Access purchase was received.</p><p>Customer: {row['customer_email']}</p><p>Clinic: {row.get('clinic_name') or 'Not provided'}</p><p>Order: {row['order_reference']}</p><p>Access expires: {expires_dt.strftime('%B %d, %Y')}</p>",
            )
            await _update_order(client, row["order_reference"], {"email_delivery": customer_email_sent})
            row["email_delivery"] = customer_email_sent
            return {**_completed_response(row), "emailDelivery": {"customer": customer_email_sent, "owner": owner_email_sent}}

        try:
            package_bytes = make_package(order)
        except ValueError as error:
            logging.info("Order %s requires prepared-after-payment fulfillment: %s", row["order_reference"], error)
            paid_at = datetime.now(timezone.utc).isoformat()
            await _update_order(client, row["order_reference"], {
                "payment_status": "PROCESSING",
                "paid_at": paid_at,
                "package_storage_path": None,
            })
            row.update({"payment_status": "PROCESSING", "paid_at": paid_at, "package_storage_path": None})
            customer_email_sent = await _send_email(
                [row["customer_email"]],
                f"Payment confirmed - we’re preparing your MYCP order {row['order_reference']}",
                "<p>Payment confirmed. We’re preparing your customized protocol package from the appropriate MyClinicProtocols master documents.</p><p>Your order is confirmed; you do not need to pay again. Most Initial Versions are delivered within 1–2 hours and may take up to 24 hours for larger or more complex requests.</p>",
            )
            owner_email_sent = await _send_email(
                [OWNER_EMAIL],
                f"PAID MYCP ORDER - PREPARATION REQUIRED - {row['order_reference']}",
                f"<p>A verified payment of ${_row_amount(row)} USD was received and this order needs prepared-after-payment fulfillment.</p><p>Customer: {row['customer_email']}</p><p>Clinic: {row.get('clinic_name') or 'Not provided'}</p><p>Treatment(s): {row.get('treatment') or 'Not provided'}</p><p>Order: {row['order_reference']}</p>",
            )
            await _update_order(client, row["order_reference"], {"email_delivery": customer_email_sent})
            row["email_delivery"] = customer_email_sent
            return {**_processing_response(row), "emailDelivery": {"customer": customer_email_sent, "owner": owner_email_sent}}
''',
)
# All Access request endpoint, stored server-side and validated against the paid 30-day window.
request_endpoint = '''\n\n@app.post("/api/all-access/request")\nasync def submit_all_access_request(request: AllAccessRequest):\n    async with httpx.AsyncClient(timeout=20) as client:\n        row = await _get_order(client, reference=request.orderReference)\n        if not row:\n            raise HTTPException(status_code=404, detail="All Access order not found")\n        intake = _order_intake(row)\n        if (row.get("payment_status") != "COMPLETED"\n                or (row.get("package_type") != "all_access" and intake.get("package") != "all_access")):\n            raise HTTPException(status_code=409, detail="This order is not an active All Access pass")\n        if str(row.get("customer_email") or "").strip().lower() != str(request.customerEmail).strip().lower():\n            raise HTTPException(status_code=403, detail="The order email does not match this All Access pass")\n        expires_raw = row.get("access_expires_at")\n        if not expires_raw:\n            paid_raw = row.get("paid_at")\n            if not paid_raw:\n                raise HTTPException(status_code=409, detail="This All Access pass does not have a valid activation date")\n            paid_dt = datetime.fromisoformat(str(paid_raw).replace("Z", "+00:00"))\n            expires_dt = paid_dt + timedelta(days=30)\n        else:\n            expires_dt = datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))\n        if expires_dt.tzinfo is None:\n            expires_dt = expires_dt.replace(tzinfo=timezone.utc)\n        if datetime.now(timezone.utc) > expires_dt:\n            raise HTTPException(status_code=410, detail="This 30-Day All Access pass has expired")\n\n        request_reference = "MYCP-REQ-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + secrets.token_hex(3).upper()\n        payload = {\n            "request_reference": request_reference,\n            "access_order_reference": row["order_reference"],\n            "customer_email": row["customer_email"],\n            "clinic_name": row.get("clinic_name"),\n            "treatment": request.treatment.strip(),\n            "request_type": request.requestType,\n            "request_details": {"notes": request.notes.strip()},\n            "status": "RECEIVED",\n        }\n        await _supabase_request(client, "POST", "/rest/v1/all_access_requests", payload=payload, prefer="return=minimal")\n\n    customer_email_sent = await _send_email(\n        [str(request.customerEmail)],\n        f"MYCP All Access request received - {request_reference}",\n        f"<p>We received your request for <strong>{request.treatment}</strong>.</p><p>Request: {request_reference}</p><p>All Access order: {request.orderReference}</p><p>We’ll prepare the requested documents using your clinic profile and submitted details. Please do not send PHI by email.</p>",\n    )\n    owner_email_sent = await _send_email(\n        [OWNER_EMAIL],\n        f"ALL ACCESS REQUEST - {request_reference}",\n        f"<p>New All Access request.</p><p>Clinic: {row.get('clinic_name') or 'Not provided'}</p><p>Customer: {row['customer_email']}</p><p>Treatment: {request.treatment}</p><p>Type: {request.requestType}</p><p>All Access order: {request.orderReference}</p><p>Request: {request_reference}</p>",\n    )\n    return {\n        "status": "RECEIVED",\n        "requestReference": request_reference,\n        "accessOrderReference": request.orderReference,\n        "accessExpiresAt": expires_dt.isoformat(),\n        "emailDelivery": {"customer": customer_email_sent, "owner": owner_email_sent},\n    }\n'''
service_text = service.read_text(encoding="utf-8")
if '@app.post("/api/all-access/request")' not in service_text:
    marker = '\n\n@app.get("/api/download/{reference}")'
    if marker not in service_text:
        raise RuntimeError("Download endpoint marker not found")
    service.write_text(service_text.replace(marker, request_endpoint + marker, 1), encoding="utf-8")

# Confirmation page: All Access gets an activation experience and portal link, not a fake file download.
must_replace(checkout_return, 'assets/mycp-commerce.js?v=20261009b', 'assets/mycp-commerce.js?v=20261010')
must_replace(
    checkout_return,
    '''      if(result.status==='COMPLETED'&&result.downloadUrl){
        title.textContent="Payment confirmed. Your Initial Version is ready";''',
    '''      if(result.package==='all_access'){
        title.textContent="Your 30-Day All Access is active";
        const expiry=result.accessExpiresAt?new Date(result.accessExpiresAt).toLocaleDateString(undefined,{year:'numeric',month:'long',day:'numeric'}):'30 days from activation';
        message.textContent=`Payment confirmed. Your clinic can submit eligible protocol requests through ${expiry}.`;
        status.textContent=`Order ${reference} - All Access active`;
        download.textContent="Submit a Protocol Request";download.href=result.requestUrl||`all-access-request.html?ref=${encodeURIComponent(reference)}`;download.classList.add('show');
        const details=document.querySelector('.details');if(details)details.innerHTML='<strong>30-DAY ALL ACCESS</strong><br>Submit as many eligible Customized Protocol or Complete Treatment Package requests as your clinic needs during the active 30-day period. This pass is for one clinic/legal practice, is non-transferable, and does not auto-renew. Specialty or investigational requests may require scope review. Final clinical approval remains with your clinic’s appropriately qualified medical director or supervising provider.';
      }else if(result.status==='COMPLETED'&&result.downloadUrl){
        title.textContent="Payment confirmed. Your Initial Version is ready";''',
)

print("All Access rollout patches applied successfully")
