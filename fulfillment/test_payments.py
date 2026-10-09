"""Payment verification regression tests; no network or real payments."""
import copy
import json
from decimal import Decimal
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

    async def test_return_without_browser_storage_recovers_by_paypal_token(self):
        self.request = service.Capture(paypalOrderId="PAYPAL123")
        result, _, _ = await self.run_capture([self.order])
        self.assertEqual(result["orderReference"], "MYCP-TEST")
        # A price change must never reprice an already-created PayPal order.
        self.assertEqual(result["amount"], "149.00")
        self.assertEqual(result["paymentMode"], "unknown")

    async def test_wrong_supplied_reference_is_rejected(self):
        self.request = service.Capture(orderReference="MYCP-OTHER", paypalOrderId="PAYPAL123")
        with self.assertRaises(HTTPException) as raised:
            await self.run_capture([])
        self.assertEqual(raised.exception.status_code, 404)

    async def test_current_price_and_recorded_mode_survive_repeated_return(self):
        self.order["purchase_units"][0]["amount"]["value"] = "49.00"
        self.order["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"] = "49.00"
        with service._connect() as db:
            db.execute("UPDATE orders SET amount=?, intake=?", ("49.00", json.dumps({
                "package": "complete", "treatments": ["Example treatment"], "_paymentMode": "sandbox"})))
        with patch.dict(service.os.environ, {"PAYPAL_MODE": "live"}):
            first, _, _ = await self.run_capture([self.order])
            again, _, _ = await self.run_capture([])
        for result in (first, again):
            self.assertEqual(result["amount"], "49.00")
            self.assertEqual(result["currency"], "USD")
            self.assertEqual(result["paymentMode"], "sandbox")
            self.assertEqual(result["package"], "complete")
            self.assertEqual(result["treatmentCount"], 1)

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


class PricingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        patcher = patch.object(service, "DB", Path(self.temp.name) / "orders.sqlite3")
        patcher.start()
        self.addCleanup(patcher.stop)

    def checkout(self, package="complete", count=1, **extra):
        return service.Checkout(customerEmail="buyer@example.com", package=package,
            treatments=[f"Treatment {n}" for n in range(count)], clinic={}, **extra)

    async def test_new_prices_sent_to_paypal_and_stored_for_each_quantity(self):
        with patch.dict(service.os.environ, {"PAYPAL_MODE": "sandbox",
                    "PAYPAL_RETURN_URL": "https://example.com/return",
                    "PAYPAL_CANCEL_URL": "https://example.com/cancel"}):
            for package, unit in (("protocol", 29), ("complete", 49)):
                for count in (1, 3, 5, 10):
                    with self.subTest(package=package, count=count):
                        amount = f"{unit * count:.2f}"
                        payment = {"id": f"{package}{count}", "links": [{"rel": "payer-action",
                            "href": "https://www.sandbox.paypal.com/checkoutnow?token=TEST"}]}
                        with patch.object(service, "_paypal", AsyncMock(return_value=payment)) as paypal, \
                             patch.object(service.httpx, "AsyncClient"):
                            result = await service.create_checkout(self.checkout(package, count,
                                expectedTotal=Decimal(amount), pricingVersion=service.PRICING_VERSION))
                        payload = paypal.call_args.args[3]
                        self.assertEqual(payload["purchase_units"][0]["amount"]["value"], amount)
                        self.assertEqual(result["amount"], amount)
                        self.assertEqual(result["currency"], "USD")
                        self.assertEqual(result["pricingVersion"], service.PRICING_VERSION)
                        with service._connect() as db:
                            row = db.execute("SELECT * FROM orders WHERE reference=?", (result["orderReference"],)).fetchone()
                        self.assertEqual(row["amount"], amount)
                        self.assertEqual(json.loads(row["intake"])["_paymentMode"], "sandbox")

    async def test_stale_or_tampered_quote_never_creates_paypal_order(self):
        for extra in ({"expectedTotal": 149}, {"expectedTotal": 1},
                      {"expectedTotal": 49, "pricingVersion": "old"}):
            with self.subTest(extra=extra), patch.object(service, "_paypal", AsyncMock()) as paypal:
                with self.assertRaises(HTTPException) as raised:
                    await service.create_checkout(self.checkout(**extra))
                self.assertEqual(raised.exception.status_code, 409)
                paypal.assert_not_called()

    async def test_unsupported_quantity_never_creates_paypal_order(self):
        with patch.object(service, "_paypal", AsyncMock()) as paypal:
            with self.assertRaises(HTTPException) as raised:
                await service.create_checkout(self.checkout(count=2))
            self.assertEqual(raised.exception.status_code, 400)
            paypal.assert_not_called()


if __name__ == "__main__":
    unittest.main()
