"""Storefront master resolution for reconciliation and buying apps."""

from __future__ import annotations

from typing import Any

import frappe

from erpnext_amazon_business.amazon_business.utils.api_hosts import api_base_url_for_region


def resolve_storefront(storefront: str) -> dict[str, Any]:
	"""Return api host, marketplace_id, and related master fields for a storefront key."""
	if not storefront:
		raise ValueError("storefront is required")

	doc = frappe.get_doc("Amazon Business Storefront", storefront)
	if not doc.is_active:
		raise frappe.ValidationError(f"Storefront {storefront} is not active")

	api_base = api_base_url_for_region(doc.api_region)
	return {
		"storefront": doc.storefront,
		"api_region": doc.api_region,
		"api_base": api_base,
		"marketplace_id": doc.marketplace_id,
		"oauth_authorize_base": doc.oauth_authorize_base,
		"country_code": doc.country_code,
	}


def get_storefront_master(storefront: str) -> dict[str, Any]:
	"""Alias used in architecture docs."""
	return resolve_storefront(storefront)
