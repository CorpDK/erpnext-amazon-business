"""Require Frappe / ERPNext >=16.0.0 and reject v17+."""

from __future__ import annotations

import erpnext
import frappe
from packaging import version

MIN_FRAPPE = "16.0.0"
MIN_ERPNEXT = "16.0.0"
MAX_FRAPPE_EXCLUSIVE = "17.0.0"
MAX_ERPNEXT_EXCLUSIVE = "17.0.0"


def execute() -> None:
	_check("Frappe", frappe.__version__, MIN_FRAPPE, MAX_FRAPPE_EXCLUSIVE)
	_check("ERPNext", erpnext.__version__, MIN_ERPNEXT, MAX_ERPNEXT_EXCLUSIVE)


def _check(app_label: str, current: str, minimum: str, maximum_exclusive: str) -> None:
	parsed = version.parse(current)
	if parsed < version.parse(minimum):
		frappe.throw(f"{app_label} {current} is below the minimum for erpnext_amazon_business ({minimum}+).")
	if parsed >= version.parse(maximum_exclusive):
		frappe.throw(
			f"{app_label} {current} is not supported by erpnext_amazon_business "
			f"(requires >= {minimum}, < {maximum_exclusive})."
		)
