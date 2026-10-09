from pathlib import Path
import re

changed = []

for path in Path('.').glob('*.html'):
    if path.name == 'all-access-request.html':
        continue
    text = path.read_text(encoding='utf-8')
    original = text

    # Main navigation style used across the primary MYCP pages.
    pattern = re.compile(
        r'(<a class="nav-tab" href="(?:index\.html)?#contact">CONTACT</a>\s*)'
        r'(<a class="nav-cta" href="order\.html">GET STARTED</a>)'
    )
    text = pattern.sub(
        r'\1<a class="nav-tab" href="all-access-request.html">ACCESS</a>\n  \2',
        text,
        count=1,
    )

    # Some pages use a compact top navigation without nav-tab classes.
    compact = re.compile(
        r'(<a href="(?:index\.html)?#contact">CONTACT</a>\s*)'
        r'(<a class="nav-cta" href="order\.html">GET STARTED</a>)'
    )
    text = compact.sub(
        r'\1<a href="all-access-request.html">ACCESS</a>\n        \2',
        text,
        count=1,
    )

    # Add an obvious returning-customer link next to the All Access purchase CTA when present.
    if 'Pay $249 & Get Access Code' in text and 'Already have a code?' not in text:
        text = text.replace(
            'Pay $249 & Get Access Code</a>',
            'Pay $249 & Get Access Code</a><div style="margin-top:10px;font-size:12px"><a href="all-access-request.html" style="color:#07969b;font-weight:700">Already have a code? Open ACCESS</a></div>',
            1,
        )

    if text != original:
        path.write_text(text, encoding='utf-8')
        changed.append(path.name)

print('Updated:', ', '.join(changed) if changed else 'no files')
