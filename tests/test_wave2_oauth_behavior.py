"""Executable behavior checks for Wave 2 OAuth and auth gates (frappe stubbed)."""

from __future__ import annotations

import json
import sys
import types
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

if "frappe" in sys.modules:
	frappe_mod = sys.modules["frappe"]
else:
	frappe_mod = types.ModuleType("frappe")
	sys.modules["frappe"] = frappe_mod


class ValidationError(Exception):
	pass


class PermissionError(Exception):
	pass


def _throw(msg, exc=ValidationError, *args, **kwargs):
	if isinstance(exc, type) and issubclass(exc, BaseException):
		raise exc(msg)
	raise ValidationError(msg)


frappe_mod.ValidationError = ValidationError
frappe_mod.PermissionError = PermissionError
frappe_mod.throw = _throw
frappe_mod.conf = {"secret": "test-site-secret"}
frappe_mod.local = types.SimpleNamespace(conf={"encryption_key": "test-site-secret"})
frappe_mod.utils = types.SimpleNamespace(
	now_datetime=lambda: __import__("datetime").datetime(2026, 1, 1, 12, 0, 0),
	get_datetime=lambda s: (
		__import__("datetime").datetime.fromisoformat(s.replace("Z", "+00:00"))
		if isinstance(s, str)
		else s
	),
)
frappe_mod.db = mock.MagicMock()
frappe_mod.get_all = mock.MagicMock()
frappe_mod.get_doc = mock.MagicMock()
frappe_mod.get_single = mock.MagicMock()
frappe_mod.has_permission = mock.MagicMock(return_value=True)
frappe_mod.respond_as_web_page = lambda *a, **k: None
frappe_mod.publish_realtime = lambda *a, **k: None
frappe_mod.whitelist = lambda *a, **k: lambda fn: fn

import frappe

from erpnext_amazon_business.amazon import resolve_storefront
from erpnext_amazon_business.amazon.auth import apply_token_payload, get_access_token
from erpnext_amazon_business.relay.desk import get_connect_url
from erpnext_amazon_business.relay.worker import process_oauth_pending


def _storefront_row(
	*,
	enabled: int = 1,
	connection_status: str = "Connected",
	token_expiry=None,
	access_token: str | None = "cached-access",
	refresh_token: str | None = "refresh-secret",
	parent: str = "CFG-1",
):
	row = mock.MagicMock()
	row.parent = parent
	row.enabled = enabled
	row.connection_status = connection_status
	row.token_expiry = token_expiry or frappe.utils.now_datetime() + timedelta(hours=1)

	def get_password(field, raise_exception=False):
		if field == "access_token":
			return access_token
		if field == "refresh_token":
			return refresh_token
		return None

	row.get_password = get_password
	row.db_set = mock.MagicMock()
	return row


class TestResolveStorefrontExport(unittest.TestCase):
	def test_public_package_export(self) -> None:
		master = mock.MagicMock()
		master.is_active = 1
		master.storefront = "amazon.in"
		master.api_region = "EU"
		master.marketplace_id = "A21TJRUUN4KGV"
		master.oauth_authorize_base = "https://www.amazon.in/ap/oa"
		master.country_code = "IN"
		frappe.get_doc.return_value = master

		result = resolve_storefront("amazon.in")
		self.assertEqual(result["storefront"], "amazon.in")
		self.assertTrue(result["api_base"].startswith("https://"))


class TestGetAccessTokenGates(unittest.TestCase):
	def setUp(self) -> None:
		self.row = _storefront_row()

	def test_refuses_when_integration_disabled(self) -> None:
		with mock.patch(
			"erpnext_amazon_business.amazon.auth.connection_row",
			return_value=self.row,
		):
			frappe.db.get_value.return_value = 0
			with self.assertRaises(frappe.ValidationError):
				get_access_token("Co", "amazon.in")

	def test_refuses_when_not_connected(self) -> None:
		self.row.connection_status = "Revoked"
		with mock.patch(
			"erpnext_amazon_business.amazon.auth.connection_row",
			return_value=self.row,
		):
			frappe.db.get_value.return_value = 1
			with self.assertRaises(frappe.ValidationError):
				get_access_token("Co", "amazon.in")

	def test_returns_cached_token_when_valid(self) -> None:
		with mock.patch(
			"erpnext_amazon_business.amazon.auth.connection_row",
			return_value=self.row,
		):
			frappe.db.get_value.return_value = 1
			self.assertEqual(get_access_token("Co", "amazon.in"), "cached-access")


class TestApplyTokenPayload(unittest.TestCase):
	def test_requires_refresh_token(self) -> None:
		with mock.patch(
			"erpnext_amazon_business.amazon.auth.connection_row",
			return_value=_storefront_row(),
		):
			with self.assertRaises(frappe.ValidationError):
				apply_token_payload("Co", "amazon.in", {"access_token": "only-access"})


class TestRelayOAuthPending(unittest.TestCase):
	def test_ready_without_refresh_token_not_handled(self) -> None:
		pending = {
			"status": "READY",
			"accessToken": "at",
			"refreshToken": None,
		}
		with mock.patch(
			"erpnext_amazon_business.relay.worker.fetch_oauth_pending",
			return_value=pending,
		):
			with mock.patch(
				"erpnext_amazon_business.relay.worker.apply_token_payload",
			) as apply_mock:
				self.assertFalse(process_oauth_pending("Co", "amazon.in"))
				apply_mock.assert_not_called()

	def test_ready_with_both_tokens_applies(self) -> None:
		pending = {
			"status": "READY",
			"accessToken": "at",
			"refreshToken": "rt",
		}
		with mock.patch(
			"erpnext_amazon_business.relay.worker.fetch_oauth_pending",
			return_value=pending,
		):
			with mock.patch(
				"erpnext_amazon_business.relay.worker.apply_token_payload",
			) as apply_mock:
				self.assertTrue(process_oauth_pending("Co", "amazon.in"))
				apply_mock.assert_called_once()


class TestWave2DocTypeTrim(unittest.TestCase):
	ROOT = Path(__file__).resolve().parents[1] / "erpnext_amazon_business"

	def _fieldnames(self, rel: str) -> set[str]:
		data = json.loads((self.ROOT / rel).read_text(encoding="utf-8"))
		return {f["fieldname"] for f in data["fields"]}

	def test_settings_dropped_sync_fields(self) -> None:
		names = self._fieldnames(
			"amazon_business/doctype/amazon_business_settings/amazon_business_settings.json"
		)
		for removed in (
			"sync_lookback_days",
			"sync_schedule",
			"sync_cron_hour",
			"document_poll_max_minutes",
			"enable_p1",
		):
			self.assertNotIn(removed, names)

	def test_company_config_uses_amazon_integration_enabled(self) -> None:
		names = self._fieldnames(
			"amazon_business/doctype/amazon_business_company_config/amazon_business_company_config.json"
		)
		self.assertIn("amazon_integration_enabled", names)
		self.assertNotIn("integration_enabled", names)


class TestDeskConnectPermissions(unittest.TestCase):
	def test_get_connect_url_requires_settings_write(self) -> None:
		frappe.has_permission.return_value = False
		with self.assertRaises(frappe.PermissionError):
			get_connect_url("Co", "amazon.in")


if __name__ == "__main__":
	unittest.main()
