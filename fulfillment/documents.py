"""Generate customer-specific draft files without making clinical decisions."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from textwrap import wrap
from zipfile import ZIP_DEFLATED, ZipFile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen.canvas import Canvas


DRAFT_LABEL = "DRAFT — Qualified Provider Review Required"


def _clean(value: object, fallback: str = "Not provided") -> str:
    text = " ".join(str(value or "").split())
    return text or fallback


def _sections(order: dict, treatment: str) -> list[tuple[str, list[str]]]:
    clinic = order.get("clinic", {})
    oversight = order.get("oversight", {})
    detail = order.get("details", {}).get(treatment, {})
    providers = ", ".join(order.get("providers", [])) or "Not provided"
    documents = ", ".join(order.get("documents", [])) or "Protocol"
    return [
        ("Document status", [
            DRAFT_LABEL,
            "This instant document organizes the purchaser's intake. It is not the RN-reviewed version, a standing order, or authorization to treat.",
            "The clinic's appropriately qualified medical director or supervising provider must review and approve all clinical content before use.",
        ]),
        ("Clinic and service", [
            f"Clinic: {_clean(clinic.get('name'))}",
            f"Primary state: {_clean(clinic.get('state'))}",
            f"Additional states: {_clean(clinic.get('additionalStates'), 'None')}",
            f"Practice type: {_clean(clinic.get('type'))}",
            f"Treatment: {_clean(treatment)}",
            f"Requested document set: {_clean(documents)}",
        ]),
        ("Provider and oversight context", [
            f"Provider roles: {_clean(providers)}",
            f"Medical director / supervising provider: {_clean(oversight.get('director'))}",
            f"Licensing state(s): {_clean(oversight.get('licensingStates'))}",
            f"Treatment setting: {_clean(oversight.get('facility'))}",
            f"Ownership structure: {_clean(oversight.get('ownership'))}",
            f"Additional oversight notes: {_clean(oversight.get('notes'), 'None provided')}",
        ]),
        ("Purchaser-supplied treatment details", [
            f"Product or device: {_clean(detail.get('product'))}",
            f"Dose, settings, or parameters: {_clean(detail.get('dose'))}",
            f"Technique or method: {_clean(detail.get('method'))}",
            f"Current workflow: {_clean(detail.get('workflow'))}",
        ]),
        ("Required review checklist", [
            "Confirm applicable law, scope of practice, delegation, supervision, and prescribing requirements for every relevant jurisdiction.",
            "Confirm patient selection, contraindications, consent, infection prevention, emergency response, aftercare, follow-up, and documentation requirements.",
            "Confirm all product labeling, device instructions for use, dosing or settings, storage, traceability, maintenance, and adverse-event procedures.",
            "Resolve every field marked “Not provided” and record the qualified approver, approval date, effective date, and version before implementation.",
        ]),
        ("Delivery and revisions", [
            "An RN-reviewed version is normally delivered within 1–2 hours and may take up to 24 hours depending on the document set.",
            "Up to two consolidated revision rounds may be requested within 14 calendar days after receipt of the RN-reviewed version.",
            "Revision requests are normally completed within 3–5 business days.",
        ]),
    ]


def make_docx(order: dict, treatment: str) -> bytes:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    title = doc.add_heading(f"{treatment} Protocol Draft", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    label = doc.add_paragraph()
    label.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = label.add_run(DRAFT_LABEL)
    run.bold = True
    run.font.size = Pt(11)
    for heading, lines in _sections(order, treatment):
        doc.add_heading(heading, level=1)
        for line in lines:
            doc.add_paragraph(line, style="List Bullet" if heading == "Required review checklist" else None)
    doc.add_paragraph(f"Order reference: {_clean(order.get('orderReference'))}")
    doc.add_paragraph(f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    stream = BytesIO()
    doc.save(stream)
    return stream.getvalue()


def make_pdf(order: dict, treatment: str) -> bytes:
    stream = BytesIO()
    canvas = Canvas(stream, pagesize=LETTER)
    width, height = LETTER
    y = height - 48

    def line(text: str, size: int = 10, bold: bool = False, gap: int = 15) -> None:
        nonlocal y
        font = "Helvetica-Bold" if bold else "Helvetica"
        canvas.setFont(font, size)
        for part in wrap(text, width=96) or [""]:
            if y < 55:
                canvas.showPage()
                y = height - 48
                canvas.setFont(font, size)
            canvas.drawString(48, y, part)
            y -= gap

    line(f"{treatment} Protocol Draft", 18, True, 22)
    line(DRAFT_LABEL, 11, True, 22)
    for heading, lines in _sections(order, treatment):
        line(heading, 13, True, 19)
        for item in lines:
            line(f"• {item}")
        y -= 5
    line(f"Order reference: {_clean(order.get('orderReference'))}", 9)
    canvas.save()
    return stream.getvalue()


def make_package(order: dict) -> bytes:
    treatments = order.get("treatments") or []
    if not treatments:
        raise ValueError("At least one treatment is required")
    stream = BytesIO()
    with ZipFile(stream, "w", ZIP_DEFLATED) as archive:
        for index, treatment in enumerate(treatments, 1):
            safe = "-".join(part.lower() for part in _clean(treatment).split() if part.isalnum()) or f"treatment-{index}"
            archive.writestr(f"{index:02d}-{safe}-DRAFT.docx", make_docx(order, treatment))
            archive.writestr(f"{index:02d}-{safe}-DRAFT.pdf", make_pdf(order, treatment))
        archive.writestr("READ-ME.txt", DRAFT_LABEL + "\n\nSee each document for review, delivery, and revision terms.\n")
    return stream.getvalue()
