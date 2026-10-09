from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "order.html"
text = path.read_text(encoding="utf-8")

card = '''<a class="package all-access-package" href="all-access.html#payment" aria-label="Get 30-Day All Access"><span class="popular">BEST VALUE</span><h3>30-Day All Access</h3><div class="price">$249 <small>/ 30 days</small></div><p>Pay once, receive a unique access code after verified payment, and request as many eligible protocols and Complete Treatment Packages as needed for 30 days.</p></a>'''

if card not in text:
    complete = '<button class="package selected" type="button" data-package="complete"><span class="popular">MOST POPULAR</span><h3>Complete Treatment Package</h3><div class="price">$49 <small>/ treatment</small></div><p>For $20 more, add applicable consent, intake, treatment record, aftercare, checklists, and emergency guidance. <strong>Order up to 5 treatments.</strong></p></button>'
    if complete not in text:
        raise RuntimeError("Complete Treatment Package card not found")
    text = text.replace(complete, complete + "\n            " + card, 1)

text = text.replace(
    '.package-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}',
    '.package-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}',
    1,
)

if '@media(max-width:1100px){.package-grid{grid-template-columns:1fr}}' not in text:
    marker = '@media(max-width:900px){'
    if marker not in text:
        raise RuntimeError("Responsive CSS marker not found")
    text = text.replace(marker, '@media(max-width:1100px){.package-grid{grid-template-columns:1fr}}\n    ' + marker, 1)

text = text.replace("$$('.package').forEach(b=>b.onclick=()=>{", "$$('.package[data-package]').forEach(b=>b.onclick=()=>{", 1)

path.write_text(text, encoding="utf-8")
print("Added 30-Day All Access as a third Package Level option")
