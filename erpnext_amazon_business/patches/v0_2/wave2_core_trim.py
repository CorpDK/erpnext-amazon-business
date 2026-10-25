"""Wave 2: rename company integration flag; note moved Settings fields.

Sync, drive, phase flags, and relay_events_cursor now belong on the reconciliation app
(see amazon-business-apps-architecture.md). PINV defaults belong on Books Config (A2).
Storefront sync cursors move to Storefront Sync State (reconciliation).
"""

from __future__ import annotations

import frappe


def execute() -> None:
	if frappe.db.has_column("tabAmazon Business Company Config", "integration_enabled"):
		if not frappe.db.has_column("tabAmazon Business Company Config", "amazon_integration_enabled"):
			frappe.db.sql(
				"""
				ALTER TABLE `tabAmazon Business Company Config`
				ADD COLUMN amazon_integration_enabled int(1) not null default 0
				"""
			)
		frappe.db.sql(
			"""
			UPDATE `tabAmazon Business Company Config`
			SET amazon_integration_enabled = COALESCE(integration_enabled, 0)
			"""
		)
		frappe.db.sql_ddl("ALTER TABLE `tabAmazon Business Company Config` DROP COLUMN integration_enabled")
