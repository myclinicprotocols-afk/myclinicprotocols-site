import io
import unittest
from zipfile import ZipFile

from docx import Document

from fulfillment.documents import INITIAL_VERSION_LABEL, make_package, validate_production_treatments


ORDER = {
    "orderReference": "MYCP-TEST-001",
    "package": "complete",
    "clinic": {"name": "Example Clinic", "state": "California", "type": "Medical spa", "phone": "555-555-5555"},
    "oversight": {"director": "Dr. Example", "licensingStates": "California"},
    "providers": ["RN", "NP"],
    "documents": ["Protocol", "Consent", "Treatment Record", "Aftercare"],
    "treatments": ["Neuromodulators"],
    "details": {
        "Neuromodulators": {"product": "BOTOX Cosmetic", "dose": "Patient-specific per current PI and prescriber order"},
    },
}


class DocumentTests(unittest.TestCase):
    def test_complete_neuromodulator_package_uses_master_document_set(self):
        package = make_package(ORDER)
        with ZipFile(io.BytesIO(package)) as archive:
            names = archive.namelist()
            self.assertEqual(sum(name.endswith(".docx") for name in names), 8)
            self.assertEqual(sum(name.endswith(".pdf") for name in names), 8)
            self.assertTrue(all("INITIAL-VERSION" in name for name in names if name.endswith((".docx", ".pdf"))))
            self.assertFalse(any("DRAFT" in name.upper() for name in names))
            self.assertTrue(all(archive.read(name).startswith(b"%PDF-") for name in names if name.endswith(".pdf")))

    def test_initial_version_contains_real_clinical_master_content_and_customer_fields(self):
        package = make_package(ORDER)
        with ZipFile(io.BytesIO(package)) as archive:
            name = next(name for name in archive.namelist() if name.startswith("01-neuromodulators") and name.endswith(".docx"))
            document = Document(io.BytesIO(archive.read(name)))
            text = "\n".join(p.text for p in document.paragraphs)
            self.assertIn(INITIAL_VERSION_LABEL, text)
            self.assertIn("Example Clinic", text)
            self.assertIn("MYCP-TEST-001", text)
            self.assertIn("units are not interchangeable", text.lower())
            self.assertIn("California", text)
            self.assertIn("RN or PA may inject", text)
            self.assertNotIn("DRAFT", text.upper())

    def test_protocol_package_contains_only_protocol_pair(self):
        order = {**ORDER, "package": "protocol"}
        package = make_package(order)
        with ZipFile(io.BytesIO(package)) as archive:
            names = archive.namelist()
            self.assertEqual(sum(name.endswith(".docx") for name in names), 1)
            self.assertEqual(sum(name.endswith(".pdf") for name in names), 1)

    def test_unconnected_master_is_blocked_before_checkout(self):
        with self.assertRaises(ValueError):
            validate_production_treatments(["Microneedling / SkinPen"])

    def test_treatment_is_required(self):
        with self.assertRaises(ValueError):
            make_package({"treatments": []})


if __name__ == "__main__":
    unittest.main()
