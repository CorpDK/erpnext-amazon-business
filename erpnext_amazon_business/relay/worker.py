"""Core relay worker skeleton: oauthPending consumption and SSE hook."""

from __future__ import annotations

import frappe

from erpnext_amazon_business.amazon.auth import apply_token_payload
from erpnext_amazon_business.relay.client import fetch_oauth_pending, get_graphql_config


def relay_worker_enabled() -> bool:
	settings = frappe.get_single("Amazon Business Settings")
	if not settings.relay_subscription_enabled:
		return False
	try:
		get_graphql_config()
	except frappe.ValidationError:
		return False
	return True


def process_oauth_pending(company: str, storefront: str) -> bool:
	"""Poll relay oauthPending and write tokens when READY. Returns True when handled."""
	pending = fetch_oauth_pending(company, storefront)
	if not pending or pending.get("status") != "READY":
		return False
	if not pending.get("accessToken") or not pending.get("refreshToken"):
		return False

	token_data = {
		"access_token": pending.get("accessToken"),
		"refresh_token": pending.get("refreshToken"),
	}
	if pending.get("expiresAt"):
		token_data["expires_in"] = _seconds_until(pending["expiresAt"])

	apply_token_payload(company, storefront, token_data)
	frappe.publish_realtime(
		"amazon_business_relay",
		{"event": "oauth_connected", "company": company, "storefront": storefront},
	)
	return True


def _seconds_until(expires_at: str) -> int:
	expiry = frappe.utils.get_datetime(expires_at)
	delta = expiry - frappe.utils.now_datetime()
	return max(int(delta.total_seconds()), 60)


def run_relay_worker_cycle() -> None:
	"""Scheduled / long-running worker tick: process pending OAuth for enabled rows."""
	if not relay_worker_enabled():
		return

	for row in _enabled_storefront_rows():
		try:
			process_oauth_pending(row.company, row.storefront)
		except Exception:
			frappe.log_error(
				title="Amazon Business relay OAuth pending",
				message=frappe.get_traceback(),
			)


def _enabled_storefront_rows():
	return frappe.db.sql(
		"""
		select cfg.company, cs.storefront
		from `tabAmazon Business Company Config` cfg
		inner join `tabAmazon Business Company Storefront` cs on cs.parent = cfg.name
		where cfg.amazon_integration_enabled = 1 and cs.enabled = 1
		""",
		as_dict=True,
	)
