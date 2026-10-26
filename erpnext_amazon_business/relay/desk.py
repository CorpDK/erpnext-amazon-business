"""Desk-facing relay and connect helpers."""

from __future__ import annotations

from urllib.parse import urlencode

import frappe

from erpnext_amazon_business.oauth.state import make_signed_state
from erpnext_amazon_business.relay.client import register_site


@frappe.whitelist()
def get_relay_status() -> dict:
	settings = frappe.get_single("Amazon Business Settings")
	paired = bool(settings.site_pairing_id and settings.get_password("pairing_secret", raise_exception=False))
	return {
		"connection_mode": settings.connection_mode,
		"paired": paired,
		"relay_subscription_enabled": bool(settings.relay_subscription_enabled),
		"enable_oauth": bool(settings.enable_oauth),
	}


@frappe.whitelist()
def trigger_oauth_pull(company: str, storefront: str) -> dict:
	if not frappe.has_permission("Amazon Business Settings", "write"):
		frappe.throw("Not permitted", frappe.PermissionError)

	from erpnext_amazon_business.relay.worker import process_oauth_pending

	handled = process_oauth_pending(company, storefront)
	return {"handled": handled}


@frappe.whitelist()
def get_connect_url(company: str, storefront: str) -> dict:
	if not frappe.has_permission("Amazon Business Settings", "write"):
		frappe.throw("Not permitted", frappe.PermissionError)

	settings = frappe.get_single("Amazon Business Settings")
	if not settings.enable_oauth:
		frappe.throw("OAuth is disabled in Amazon Business Settings")

	mode = settings.connection_mode
	state = make_signed_state(company, storefront)
	master = frappe.get_doc("Amazon Business Storefront", storefront)

	if mode == "Relay":
		if not settings.relay_base_url or not settings.site_pairing_id:
			frappe.throw("Relay base URL and site pairing id are required")
		query = urlencode(
			{
				"site_pairing_id": settings.site_pairing_id,
				"company": company,
				"storefront": storefront,
				"state": state,
			}
		)
		url = f"{settings.relay_base_url.rstrip('/')}/oauth/start?{query}"
	else:
		if not settings.oauth_redirect_uri:
			frappe.throw("OAuth redirect URI is required for Direct mode")
		auth_base = master.oauth_authorize_base.rstrip("/")
		query = urlencode(
			{
				"response_type": "code",
				"client_id": settings.lwa_client_id,
				"redirect_uri": settings.oauth_redirect_uri,
				"scope": "profile",
				"state": state,
			}
		)
		url = f"{auth_base}?{query}"

	return {"url": url, "connection_mode": mode}


@frappe.whitelist()
def register_with_relay(site_label: str, registration_token: str) -> dict:
	if not frappe.has_permission("Amazon Business Settings", "write"):
		frappe.throw("Not permitted", frappe.PermissionError)

	import erpnext_amazon_business as ab_app

	erp_version = getattr(ab_app, "__version__", "2026.10.0")
	result = register_site(site_label, erp_version, registration_token)
	settings = frappe.get_single("Amazon Business Settings")
	settings.site_pairing_id = result["site_pairing_id"]
	settings.pairing_secret = result["pairing_secret"]
	settings.save(ignore_permissions=True)
	return {"site_pairing_id": result["site_pairing_id"]}
