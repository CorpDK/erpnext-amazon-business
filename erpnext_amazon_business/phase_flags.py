"""Read feature phase toggles from Amazon Business Settings."""

from __future__ import annotations

import frappe


def phase_enabled(phase: int) -> bool:
	settings = frappe.get_single("Amazon Business Settings")
	return bool(settings.get(f"enable_p{phase}"))
