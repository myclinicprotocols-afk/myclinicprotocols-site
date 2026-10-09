from pathlib import Path


def update(path, pairs):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new)
        else:
            print(f'NOTE {path}: not found: {old[:100]}')
    p.write_text(text, encoding='utf-8')


update('index.html', [
    ('<article class="process-card"><div class="process-number">3</div><h3>Review and pay</h3><p>Confirm the scope, bundle pricing, requested documents, and final order before secure checkout.</p></article>',
     '<article class="process-card"><div class="process-number">3</div><h3>Review and checkout</h3><p>Confirm your order details and complete checkout.</p></article>'),
    ('<article class="process-card"><div class="process-number">4</div><h3>Receive your documents</h3><p>Download the Initial Version after verified payment. Your RN-reviewed final version normally follows in 1–2 hours and may take up to 24 hours.</p></article>',
     '<article class="process-card"><div class="process-number">4</div><h3>Receive your completed package</h3><p>After checkout, your order is confirmed and we prepare your customized package from the appropriate MYCP master protocols. Delivery is usually within 1-2 hours and may take up to 24 hours.</p></article>'),
    ('forms-prepared for provider review', 'forms prepared for provider review'),
    ('forms-prepared for qualified provider review', 'forms prepared for qualified provider review')
])

update('order.html', [
    ('provider roles-not individual patient records.', 'provider roles, not individual patient records.'),
    ('<label class="inline-check"><input type="checkbox" id="approveClinical"> I understand that final clinical approval remains the responsibility of my clinic’s appropriately qualified medical director or supervising provider.</label>\n            <label class="inline-check"><input type="checkbox" id="approveScope"> I confirm that this order contains no patient-identifying or protected health information.</label>',
     '<label class="inline-check"><input type="checkbox" id="approveTerms"> I agree to the <a href="terms-and-conditions.html" target="_blank" rel="noopener"><strong>Terms &amp; Conditions</strong></a>.</label>\n            <label class="inline-check"><input type="checkbox" id="approveClinical"> I understand that final clinical approval remains with my clinic’s qualified provider or medical director.</label>\n            <label class="inline-check"><input type="checkbox" id="approveScope"> I confirm that this order contains no patient-identifying or protected health information.</label>'),
    ("function toggleCheckout(){$('#checkout').disabled=!($('#approveClinical').checked&&$('#approveScope').checked)}$('#approveClinical').onchange=toggleCheckout;$('#approveScope').onchange=toggleCheckout;",
     "function toggleCheckout(){$('#checkout').disabled=!($('#approveTerms').checked&&$('#approveClinical').checked&&$('#approveScope').checked)}$('#approveTerms').onchange=toggleCheckout;$('#approveClinical').onchange=toggleCheckout;$('#approveScope').onchange=toggleCheckout;"),
    ('button.textContent="Opening secure checkout…";status.textContent="Creating your verified PayPal order…";',
     'button.textContent="Opening checkout...";status.textContent="Preparing checkout...";'),
    ('model.orderReference=result.orderReference;model.paymentStatus="PayPal checkout created";save();',
     'model.orderReference=result.orderReference;model.paymentStatus="Checkout created";save();'),
    ('status.textContent="Opening PayPal…";location.href=approvalUrl;',
     'status.textContent="Opening checkout...";location.href=approvalUrl;'),
    ('const FULFILLMENT_API=MYCPCommerce.API;\n    const states=',
     "const FULFILLMENT_API=MYCPCommerce.API;\n    const TERMS_VERSION='2026-10-10';\n    const states="),
    ('const d=orderData(),payload={...d,customerEmail:d.clinic.email,treatments:allTreatments(),expectedTotal:d.estimatedTotal,pricingVersion:MYCPCommerce.VERSION};',
     "const d=orderData(),acceptedAt=new Date().toISOString(),payload={...d,customerEmail:d.clinic.email,treatments:allTreatments(),details:{...d.details,orderConsent:{termsAccepted:true,termsVersion:TERMS_VERSION,termsAcceptedAt:acceptedAt,finalClinicalApprovalAcknowledged:true,noPhiConfirmed:true}},expectedTotal:d.estimatedTotal,pricingVersion:MYCPCommerce.VERSION};")
])

update('editorial-standards.html', [
    ('designed to support qualified professional review-not replace medical judgment', 'designed to support qualified professional review, not replace medical judgment')
])

update('assets/mycp-search-support.js', [
    ("if(hasAny(q,['initial version','instant draft','draft after payment','immediate download','download after payment'])){",
     "if(hasAny(q,['immediate download','download after payment','download right away','instant download'])){")
])

# Audit every public HTML page plus the customer-facing JavaScript.
customer_files = list(Path('.').glob('*.html')) + [
    Path('assets/mycp-search-support.js'), Path('assets/mycp-commerce.js')
]
banned = [
    'Initial Version', 'RN-reviewed final version', 'instant draft',
    'Continue to Secure PayPal Checkout', 'Opening PayPal', 'Creating your verified PayPal order',
    '1, 3, 5, or 10', 'review-not replace', 'roles-not individual', 'forms-prepared'
]
failures = []
for p in customer_files:
    text = p.read_text(encoding='utf-8')
    if '—' in text:
        failures.append(f'{p}: em dash')
    for phrase in banned:
        if phrase.lower() in text.lower():
            failures.append(f'{p}: {phrase}')
if failures:
    raise SystemExit('Stale customer copy remains:\n' + '\n'.join(failures))
print(f'Customer-facing copy audit passed across {len(customer_files)} public files.')
