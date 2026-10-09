"""Payment and pricing regression tests; no network or real payments."""
from __future__ import annotations

import copy
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fulfillment import service


class PricingTests(unittest.IsolatedAsyncioTestCase):
    def checkout(self, package="complete", count=1, **extra):
        return service.Checkout(
            customerEmail="buyer@example.com",
            package=package,
            treatments=["Neuromodulators"] * count,
            clinic={"name": "Test Clinic", "state": "Florida"},
            **extra,
        )

    async def test_new_prices_are_server_calculated_for_all_supported_quantities(self):
        with patch.dict(service.os.environ, {
            "PAYPAL_MODE": "sandbox",
            "PAYPAL_RETURN_URL": "https://myclinicprotocols.com/checkout-return.html",
            "PAYPAL_CANCEL_URL": "https://myclinicprotocols.com/order.html",
        }):
            for package, unit in (("protocol", 29), ("complete", 49)):
                for count in (1, 3, 5, 10):
                    with self.subTest(package=package, count=count):
                        amount = f"{unit * count:.2f}"
                        payment = {
                            "id": f"PAYPAL-{package}-{count}",
                            "links": [{"rel": "payer-action", "href": "https://www.sandbox.paypal.com/checkoutnow?token=TEST"}],
                        }
                        with patch.object(service, "_paypal", AsyncMock(return_value=payment)) as paypal, \
                             patch.object(service, "_insert_order", AsyncMock()) as insert_order:
                            result = await service.create_checkout(self.checkout(
                                package, count,
                                expectedTotal=Decimal(amount),
                                pricingVersion=service.PRICING_VERSION,
                            ))
                        payload = paypal.call_args.args[3]
                        self.assertEqual(payload["purchase_units"][0]["amount"]["value"], amount)
                        self.assertEqual(result["amount"], amount)
                        self.assertEqual(result["currency"], "USD")
                        self.assertEqual(result["paymentMode"], "sandbox")
                        self.assertEqual(result["pricingVersion"], service.PRICING_VERSION)
                        insert_order.assert_awaited_once()
                        self.assertEqual(insert_order.call_args.args[-1], amount)

    async def test_stale_or_tampered_displayed_total_is_rejected_before_paypal(self):
        for extra in (
            {"expectedTotal": Decimal("149.00"), "pricingVersion": service.PRICING_VERSION},
            {"expectedTotal": Decimal("1.00"), "pricingVersion": service.PRICING_VERSION},
            {"expectedTotal": Decimal("49.00"), "pricingVersion": "old"},
        ):
            with self.subTest(extra=extra), patch.object(service, "_paypal", AsyncMock()) as paypal:
                with self.assertRaises(HTTPException) as raised:
                    await service.create_checkout(self.checkout(**extra))
                self.assertEqual(raised.exception.status_code, 409)
                paypal.assert_not_called()

    async def test_unsupported_quantity_is_rejected_before_paypal(self):
        with patch.object(service, "_paypal", AsyncMock()) as paypal:
            with self.assertRaises(HTTPException) as raised:
                await service.create_checkout(self.checkout(count=2))
            self.assertEqual(raised.exception.status_code, 400)
            paypal.assert_not_called()

    def test_price_table_matches_public_offer(self):
        self.assertEqual(service.PRICES["protocol"], {1: 29, 3: 87, 5: 145, 10: 290})
        self.assertEqual(service.PRICES["complete"], {1: 49, 3: 147, 5: 245, 10: 490})
        self.assertEqual(service.PRICING_VERSION, "2026-10-09")


class CaptureTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.row = {
            "order_reference": "MYCP-TEST-001",
            "paypal_order_id": "PAYPAL123",
            "payment_status": "CREATED",
            "payment_amount": "49.00",
            "currency": "USD",
            "customer_email": "buyer@example.com",
            "package_storage_path": None,
            "email_delivery": False,
            "intake": {
                "package": "complete",
                "treatments": ["Neuromodulators"],
                "clinic": {"name": "Test Clinic", "state": "Florida"},
                "_paymentMode": "sandbox",
                "_pricingVersion": service.PRICING_VERSION,
            },
        }
        self.order = {
            "id": "PAYPAL123",
            "intent": "CAPTURE",
            "status": "COMPLETED",
            "purchase_units": [{
                "custom_id": "MYCP-TEST-001",
                "invoice_id": "MYCP-TEST-001",
                "amount": {"value": "49.00", "currency_code": "USD"},
                "payments": {"captures": [{
                    "id": "CAPTURE123",
                    "status": "COMPLETED",
                    "amount": {"value": "49.00", "currency_code": "USD"},
                }]},
            }],
        }

    async def run_capture(self, capture=None, paypal_responses=None, row=None, storage_ok=True):
        capture = capture or service.Capture(orderReference="MYCP-TEST-001", paypalOrderId="PAYPAL123")
        row = copy.deepcopy(self.row if row is None else row)
        paypal_responses = [self.order] if paypal_responses is None else paypal_responses
        with patch.object(service, "_get_order", AsyncMock(return_value=row)) as get_order, \
             patch.object(service, "_paypal", AsyncMock(side_effect=paypal_responses)) as paypal, \
             patch.object(service, "make_package", return_value=b"test-package") as package, \
             patch.object(service, "_storage_upload", AsyncMock(return_value=storage_ok)), \
             patch.object(service, "_update_order", AsyncMock()) as update_order, \
             patch.object(service, "_download_url", return_value="https://example.com/download"), \
             patch.object(service, "_send_email", AsyncMock(return_value=False)):
            result = await service.capture_checkout(capture)
        return result, get_order, paypal, package, update_order

    async def test_token_only_return_recovers_without_browser_storage(self):
        result, get_order, _, _, _ = await self.run_capture(
            capture=service.Capture(paypalOrderId="PAYPAL123")
        )
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["orderReference"], "MYCP-TEST-001")
        self.assertEqual(result["amount"], "49.00")
        self.assertEqual(result["paymentMode"], "sandbox")
        self.assertEqual(result["package"], "complete")
        self.assertEqual(result["treatmentCount"], 1)
        self.assertIsNone(get_order.call_args.kwargs["reference"])
        self.assertEqual(get_order.call_args.kwargs["paypal_id"], "PAYPAL123")

    async def test_wrong_reference_or_missing_order_never_releases_files(self):
        capture = service.Capture(orderReference="MYCP-OTHER", paypalOrderId="PAYPAL123")
        with patch.object(service, "_get_order", AsyncMock(return_value=None)), \
             patch.object(service, "make_package") as package:
            with self.assertRaises(HTTPException) as raised:
                await service.capture_checkout(capture)
        self.assertEqual(raised.exception.status_code, 404)
        package.assert_not_called()

    async def test_completed_order_is_idempotent_and_preserves_stored_amount(self):
        row = copy.deepcopy(self.row)
        row["payment_status"] = "COMPLETED"
        row["payment_amount"] = "149.00"
        row["intake"]["_paymentMode"] = "unknown"
        row["package_storage_path"] = "MYCP-TEST-001/initial-version-package.zip"
        result, _, paypal, package, _ = await self.run_capture(row=row, paypal_responses=[])
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["amount"], "149.00")
        self.assertEqual(result["paymentMode"], "unknown")
        paypal.assert_not_called()
        package.assert_not_called()

    async def test_paypal_amount_mismatch_never_releases_package(self):
        wrong = copy.deepcopy(self.order)
        wrong["purchase_units"][0]["amount"]["value"] = "1.00"
        with self.assertRaises(HTTPException) as raised:
            await self.run_capture(paypal_responses=[wrong])
        self.assertEqual(raised.exception.status_code, 409)

    async def test_lost_capture_response_is_reconciled_with_full_paypal_order(self):
        approved = copy.deepcopy(self.order)
        approved["status"] = "APPROVED"
        approved["purchase_units"][0].pop("payments")
        result, _, paypal, package, _ = await self.run_capture(
            paypal_responses=[approved, HTTPException(502, "response lost"), self.order]
        )
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual([call.args[1] for call in paypal.call_args_list], ["GET", "POST", "GET"])
        package.assert_called_once()

    async def test_storage_failure_uses_private_local_fallback_without_losing_paid_order(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(service, "ROOT", Path(temp)):
            result, _, _, _, updates = await self.run_capture(storage_ok=False)
            self.assertEqual(result["status"], "COMPLETED")
            payment_update = updates.await_args_list[0].args[2]
            self.assertEqual(payment_update["payment_status"], "COMPLETED")
            self.assertTrue(payment_update["package_storage_path"].startswith("local:"))
            self.assertTrue(Path(payment_update["package_storage_path"][6:]).is_file())


if __name__ == "__main__":
    unittest.main()
