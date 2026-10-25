"""Direct OAuth callback: exchange code and update company storefront tokens."""

from __future__ import annotations

from typing import Any

import frappe

from erpnext_amazon_business.amazon.auth import (
	apply_token_payload,
	connection_row,
	exchange_authorization_code,
)
from erpnext_amazon_business.oauth.state import parse_signed_state


@frappe.whitelist(allow_guest=True)
def handle_callback(code: str | None = None, state: str | None = None, error: str | None = None):
	"""Whitelisted entry for Amazon LWA redirect (Direct mode)."""
	if error:
		frappe.respond_as_web_page(
			"Amazon Business OAuth",
			f"Authorization failed: {error}",
			indicator_color="red",
		)
		return

	if not code or not state:
		frappe.throw("Missing OAuth code or state")

	payload = parse_signed_state(state)
	company = payload["company"]
	storefront = payload["storefront"]

	settings = frappe.get_single("Amazon Business Settings")
	if settings.connection_mode != "Direct":
		frappe.throw("Direct OAuth callback is only valid when connection mode is Direct")

	redirect_uri = settings.oauth_redirect_uri
	if not redirect_uri:
		frappe.throw("OAuth redirect URI is not configured")

	if not connection_row(company, storefront):
		frappe.throw(
			f"No storefront row for company={company}, storefront={storefront}"
		)

	token_data = exchange_authorization_code(code, redirect_uri)
	apply_token_payload(company, storefront, token_data)

	frappe.publish_realtime(
		"amazon_business_relay",
		{"event": "oauth_connected", "company": company, "storefront": storefront},
	)

	frappe.respond_as_web_page(
		"Amazon Business",
		f"Connected {storefront} for {company}. You can close this window.",
		indicator_color="green",
	)


def handle_callback_payload(code: str, state: str) -> dict[str, Any]:
	"""Non-whitelisted helper for tests and internal callers."""
	payload = parse_signed_state(state)
	company = payload["company"]
	storefront = payload["storefront"]
	if not connection_row(company, storefront):
		frappe.throw(
			f"No storefront row for company={company}, storefront={storefront}"
		)
	settings = frappe.get_single("Amazon Business Settings")
	token_data = exchange_authorization_code(code, settings.oauth_redirect_uri)
	apply_token_payload(payload["company"], payload["storefront"], token_data)
	return {"company": payload["company"], "storefront": payload["storefront"]}
