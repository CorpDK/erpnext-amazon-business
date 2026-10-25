"""Feature phase toggles — owned by reconciliation app after Wave 2 core trim."""

from __future__ import annotations

import frappe


def phase_enabled(phase: int) -> bool:
	"""Return whether reconciliation phase P{n} is enabled (delegates to sibling app)."""
	if "erpnext_amazon_business_reconciliation" not in frappe.get_installed_apps():
		return False
	settings = frappe.get_single("Amazon Business Reconciliation Settings")
	return bool(settings.get(f"enable_p{phase}"))
