from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EM_DASH = "\u2014"

TEXT_EXTENSIONS = {
    ".html", ".htm", ".js", ".css", ".xml", ".md", ".txt", ".json", ".py", ".yml", ".yaml"
}

NATURAL_REPLACEMENTS = {
    f"Secure payment {EM_DASH} activate your 30-day license": "Secure payment. Activate your 30-day access",
    f"Payment first {EM_DASH} requests come after.": "Payment first. Requests come after.",
    f"Optional {EM_DASH} e.g. Georgia, Alabama": "Optional. Example: Georgia, Alabama",
    f"Continue to Secure PayPal Checkout {EM_DASH} $249": "Continue to Secure PayPal Checkout: $249",
    f"30-Day All Access {EM_DASH} one clinic/legal practice": "30-Day All Access. One clinic/legal practice",
    f"INITIAL VERSION {EM_DASH} Prepared for Qualified Provider Review.": "INITIAL VERSION: Prepared for Qualified Provider Review.",
    f"Payment confirmed {EM_DASH} your Initial Version is ready": "Payment confirmed. Your Initial Version is ready",
    f"Payment confirmed {EM_DASH} we’re preparing your Initial Version": "Payment confirmed. We’re preparing your Initial Version",
    f"Payment confirmed {EM_DASH} we're preparing your Initial Version": "Payment confirmed. We're preparing your Initial Version",
    f"Order {{reference}} {EM_DASH} All Access active": "Order {reference}: All Access active",
    f"Order {{reference}} confirmed {EM_DASH} preparation in progress": "Order {reference} confirmed. Preparation in progress",
}

changed = []
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
        continue
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    new = text
    for old, replacement in NATURAL_REPLACEMENTS.items():
        new = new.replace(old, replacement)
    # Final safeguard: MYCP website/customer copy should never contain an em dash.
    new = new.replace(EM_DASH, "-")
    if new != text:
        path.write_text(new, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

remaining = []
for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS or ".git" in path.parts:
        continue
    if EM_DASH in path.read_text(encoding="utf-8"):
        remaining.append(str(path.relative_to(ROOT)))

if remaining:
    raise SystemExit("Em dash remains in: " + ", ".join(remaining))

print(f"Updated {len(changed)} files")
for name in changed:
    print(name)
