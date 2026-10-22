import frappe


def has_app_permission() -> bool:
	if frappe.session.user == "Administrator":
		return True
	return frappe.has_permission("Amazon Business Settings", "read")
