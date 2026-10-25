"""Signed OAuth state for Direct mode."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

import frappe


def _signing_key() -> bytes:
	secret = frappe.conf.get("secret") or frappe.local.conf.get("encryption_key")
	if not secret:
		raise frappe.ValidationError("Site secret is not configured for OAuth state signing")
	return secret.encode() if isinstance(secret, str) else secret


def make_signed_state(company: str, storefront: str) -> str:
	payload = {"company": company, "storefront": storefront}
	body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
	digest = hmac.new(_signing_key(), body.encode(), hashlib.sha256).hexdigest()
	return f"{body}|{digest}"


def parse_signed_state(state: str) -> dict[str, Any]:
	if "|" not in state:
		frappe.throw("Invalid OAuth state")
	body, digest = state.rsplit("|", 1)
	expected = hmac.new(_signing_key(), body.encode(), hashlib.sha256).hexdigest()
	if not hmac.compare_digest(expected, digest):
		frappe.throw("OAuth state signature mismatch")
	payload = json.loads(body)
	if not payload.get("company") or not payload.get("storefront"):
		frappe.throw("OAuth state missing company or storefront")
	return payload
