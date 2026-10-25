import frappe


def after_install() -> None:
	_ensure_settings_defaults()


def after_migrate() -> None:
	_ensure_settings_defaults()


def _ensure_settings_defaults() -> None:
	if not frappe.db.exists("DocType", "Amazon Business Settings"):
		return
	settings = frappe.get_single("Amazon Business Settings")
	changed = False
	if settings.relay_subscription_enabled is None:
		settings.relay_subscription_enabled = 1
		changed = True
	if changed:
		settings.save(ignore_permissions=True)
