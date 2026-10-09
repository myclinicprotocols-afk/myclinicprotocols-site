from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else 'fulfillment/service.py')
text = path.read_text(encoding='utf-8')

old = 'fulfillment_mode = "all_access" if checkout.package == "all_access" else _fulfillment_mode(checkout.treatments)'
if old in text:
    text = text.replace(old, 'fulfillment_mode = "all_access" if checkout.package == "all_access" else "manual"', 1)
elif 'fulfillment_mode = "all_access" if checkout.package == "all_access" else "manual"' not in text:
    raise SystemExit('Expected create-checkout fulfillment mode not found')

text = text.replace(
    'This treatment requires clinic-specific preparation before delivery. Online payment is not available for it yet; please email myclinicprotocols@gmail.com and we’ll help you complete the order.',
    'Checkout is temporarily unavailable while order confirmation email is being configured. Please email myclinicprotocols@gmail.com and we will help you complete the order.'
)

start_marker = '        fulfillment_mode = order.get("_fulfillmentMode") or _fulfillment_mode(order.get("treatments") or [])'
end_marker = '\n\n\n@app.post("/api/all-access/request")'
if start_marker in text:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    replacement = '''        fulfillment_mode = "manual"
        order["_fulfillmentMode"] = "manual"
        paid_at = datetime.now(timezone.utc).isoformat()
        await _update_order(client, row["order_reference"], {
            "payment_status": "COMPLETED",
            "paid_at": paid_at,
            "package_storage_path": None,
            "intake": order,
        })
        row.update({
            "payment_status": "COMPLETED",
            "paid_at": paid_at,
            "package_storage_path": None,
            "intake": order,
        })

    customer_subject = f"Order confirmed: {row['order_reference']}"
    customer_html = (
        "<p><strong>Order confirmed.</strong></p>"
        "<p>We received your payment and are preparing your customized package from the appropriate MyClinicProtocols master protocols.</p>"
        "<p>Most completed packages are delivered within 1-2 hours and may take up to 24 hours depending on the package, customization, and review needed.</p>"
        "<p>Your completed Word and PDF files will be sent to this email address with a private download link. You do not need to place another order.</p>"
        "<p>Final clinical approval remains with your clinic's qualified provider or medical director.</p>"
    )
    owner_subject = f"NEW PAID MYCP ORDER: {row['order_reference']}"
    customer_email_sent = await _send_email([row["customer_email"]], customer_subject, customer_html)
    owner_email_sent = await _send_email(
        [OWNER_EMAIL], owner_subject,
        f"<p>A verified payment of ${_row_amount(row)} USD was received.</p><p>Customer: {row['customer_email']}</p>"
        f"<p>Clinic: {row.get('clinic_name') or 'Not provided'}</p><p>Order: {row['order_reference']}</p>"
        f"<p>Fulfillment: Prepare from the appropriate MYCP master protocols and deliver by email/private download.</p>"
        f"<p>Treatment(s): {row.get('treatment') or ''}</p>"
    )
    async with httpx.AsyncClient(timeout=15) as client:
        await _update_order(client, row["order_reference"], {"email_delivery": customer_email_sent})
    row["email_delivery"] = customer_email_sent
    response = _completed_response(row)
    response["emailDelivery"] = {"customer": customer_email_sent, "owner": owner_email_sent}
    return response'''
    text = text[:start] + replacement + text[end:]
elif 'customer_subject = f"Order confirmed: {row[\'order_reference\']}"' not in text:
    raise SystemExit('Expected standard fulfillment block not found')

text = text.replace('Your MYCP 30-Day All Access is active — ', 'Your MYCP 30-Day All Access is active: ')
text = text.replace('Payment confirmed — your 30-Day All Access is active.', 'Payment confirmed. Your 30-Day All Access is active.')
text = text.replace('NEW $249 ALL ACCESS — ', 'NEW $249 ALL ACCESS: ')

path.write_text(text, encoding='utf-8')
print(f'Updated {path}')
