"""Payment verification regression tests; no network or real payments."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fulfillment import service


class CaptureTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        for name, value in (("ROOT", root), ("DB", root / "orders.sqlite3")):
            patcher = patch.object(service, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        with service._connect() as db:
            db.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?)",
                       ("MYCP-TEST", "PAYPAL123", "buyer@example.com", "149.00", "USD",
                        "CREATED", json.dumps({"clinic": {}}), None, "2026-09-10", None))
        self.order = {"id": "PAYPAL123", "intent": "CAPTURE", "status": "COMPLETED",
                      "purchase_units": [{"custom_id": "MYCP-TEST", "invoice_id": "MYCP-TEST",
                       "amount": {"value": "149.00", "currency_code": "USD"},
                       "payments": {"captures": [{"id": "CAPTURE123", "status": "COMPLETED",
                           "amount": {"value": "149.00", "currency_code": "USD"}}]}}]}
        self.request = service.Capture(orderReference="MYCP-TEST", paypalOrderId="PAYPAL123")

    async def run_capture(self, responses):
        with patch.object(service, "_paypal", AsyncMock(side_effect=responses)) as paypal, \
             patch.object(service.httpx, "AsyncClient") as client, \
             patch.object(service, "make_package", return_value=b"test-package") as package, \
             patch.object(service, "_download_url", return_value="https://example.com/download"), \
             patch.object(service, "_send_email", AsyncMock(return_value=False)):
            self.package_mock = package
            result = await service.capture_checkout(self.request)
            return result, paypal, package

    async def test_minimal_capture_response_reconciled_from_full_order(self):
        approved = copy.deepcopy(self.order)
        approved["status"] = "APPROVED"
        approved["purchase_units"][0].pop("payments")
        result, paypal, package = await self.run_capture(
            [approved, {"id": "PAYPAL123", "status": "COMPLETED"}, self.order])
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual([c.args[1] for c in paypal.call_args_list], ["GET", "POST", "GET"])
        package.assert_called_once()

    async def test_already_captured_order_does_not_capture_again(self):
        result, paypal, _ = await self.run_capture([self.order])
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual([c.args[1] for c in paypal.call_args_list], ["GET"])
        result, paypal, package = await self.run_capture([])
        self.assertEqual(result["status"], "COMPLETED")
        paypal.assert_not_called()
        package.assert_not_called()

    async def test_lost_capture_response_reconciles(self):
        approved = copy.deepcopy(self.order)
        approved["status"] = "APPROVED"
        result, _, _ = await self.run_capture([
            approved, HTTPException(502, "response lost"), self.order])
        self.assertEqual(result["status"], "COMPLETED")

    async def test_mismatches_and_pending_payments_never_release_package(self):
        mutations = [
            lambda o: o.update(id="OTHER"),
            lambda o: o["purchase_units"][0].update(custom_id="OTHER"),
            lambda o: o["purchase_units"][0].update(invoice_id="OTHER"),
            lambda o: o["purchase_units"][0]["amount"].update(value="1.00"),
            lambda o: o["purchase_units"][0]["amount"].update(currency_code="EUR"),
            lambda o: o["purchase_units"][0]["payments"]["captures"][0].update(status="PENDING"),
            lambda o: o["purchase_units"][0]["payments"]["captures"][0]["amount"].update(value="1.00"),
            lambda o: o.update(purchase_units=[]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                order = copy.deepcopy(self.order)
                mutate(order)
                with self.assertRaises(HTTPException) as raised:
                    await self.run_capture([order])
                self.assertEqual(raised.exception.status_code, 409)
                self.package_mock.assert_not_called()
                with service._connect() as db:
                    self.assertEqual(db.execute("SELECT status FROM orders").fetchone()[0], "CREATED")


if __name__ == "__main__":
    unittest.main()
