"""Ensure storefront master rows exist (api-mapping §17)."""

from __future__ import annotations

import frappe

from erpnext_amazon_business.amazon_business.data.storefronts import STOREFRONTS


def execute() -> None:
	if not frappe.db.table_exists("Amazon Business Storefront"):
		return
	for row in STOREFRONTS:
		if frappe.db.exists("Amazon Business Storefront", row["storefront"]):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Amazon Business Storefront",
				"is_active": 1,
				**row,
			}
		)
		doc.insert(ignore_permissions=True)
