import io
import unittest
from zipfile import ZipFile

from docx import Document

from fulfillment.documents import DRAFT_LABEL, make_package


ORDER = {
    "orderReference": "MYCP-TEST-001",
    "clinic": {"name": "Example Clinic", "state": "California", "type": "Medical spa"},
    "oversight": {"director": "Dr. Example", "licensingStates": "California"},
    "providers": ["RN", "NP"],
    "documents": ["Protocol", "Consent"],
    "treatments": ["Microneedling", "IV Hydration"],
    "details": {
        "Microneedling": {"product": "Example device", "workflow": "Consult, treat, follow up"},
        "IV Hydration": {"product": "Purchaser to complete"},
    },
}


class DocumentTests(unittest.TestCase):
    def test_package_has_docx_and_pdf_per_treatment(self):
        package = make_package(ORDER)
        with ZipFile(io.BytesIO(package)) as archive:
            names = archive.namelist()
            self.assertEqual(sum(name.endswith(".docx") for name in names), 2)
            self.assertEqual(sum(name.endswith(".pdf") for name in names), 2)
            self.assertTrue(all(archive.read(name).startswith(b"%PDF-") for name in names if name.endswith(".pdf")))

    def test_draft_label_and_customer_fields_are_in_docx(self):
        package = make_package(ORDER)
        with ZipFile(io.BytesIO(package)) as archive:
            name = next(name for name in archive.namelist() if name.endswith(".docx"))
            document = Document(io.BytesIO(archive.read(name)))
            text = "\n".join(p.text for p in document.paragraphs)
            self.assertIn(DRAFT_LABEL, text)
            self.assertIn("Example Clinic", text)
            self.assertIn("MYCP-TEST-001", text)
            self.assertIn("not the RN-reviewed version", text)

    def test_treatment_is_required(self):
        with self.assertRaises(ValueError):
            make_package({"treatments": []})


if __name__ == "__main__":
    unittest.main()
