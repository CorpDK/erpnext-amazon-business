"""OAuth signed-state round-trip (frappe stubbed for unit CI)."""

from __future__ import annotations

import json
import sys
import types
import unittest
from unittest import mock

if "frappe" not in sys.modules:
	_frappe = types.ModuleType("frappe")

	class ValidationError(Exception):
		pass

	_frappe.ValidationError = ValidationError

	def _throw(msg, *args, **kwargs):
		raise ValidationError(msg)

	_frappe.throw = _throw
	_frappe.conf = {}
	_frappe.local = types.SimpleNamespace(conf={})
	sys.modules["frappe"] = _frappe

import frappe

from erpnext_amazon_business.oauth.state import make_signed_state, parse_signed_state


class TestOAuthState(unittest.TestCase):
	def test_round_trip(self) -> None:
		with mock.patch(
			"erpnext_amazon_business.oauth.state._signing_key",
			return_value=b"unit-test-secret",
		):
			state = make_signed_state("Test Co", "amazon.in")
			body, digest = state.rsplit("|", 1)
			payload = json.loads(body)
			self.assertEqual(payload["company"], "Test Co")
			self.assertEqual(payload["storefront"], "amazon.in")
			self.assertEqual(len(digest), 64)
			self.assertEqual(parse_signed_state(state), payload)

	def test_rejects_tampered_state(self) -> None:
		with mock.patch(
			"erpnext_amazon_business.oauth.state._signing_key",
			return_value=b"unit-test-secret",
		):
			state = make_signed_state("A", "amazon.com")
			bad = state[:-1] + ("0" if state[-1] != "0" else "1")
			with self.assertRaises(frappe.ValidationError):
				parse_signed_state(bad)


if __name__ == "__main__":
	unittest.main()
