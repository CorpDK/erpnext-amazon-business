"""Tax helpers; india_compliance is optional on the site."""

from __future__ import annotations

import frappe


def india_compliance_installed() -> bool:
	"""Return True when india_compliance is installed (P1 GST paths use this guard)."""
	return "india_compliance" in frappe.get_installed_apps()
