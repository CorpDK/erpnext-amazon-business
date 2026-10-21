import frappe


def after_install() -> None:
	_ensure_settings_defaults()


def after_migrate() -> None:
	_ensure_settings_defaults()


def _ensure_settings_defaults() -> None:
	if not frappe.db.exists("DocType", "Amazon Business Settings"):
		return
	settings = frappe.get_single("Amazon Business Settings")
	if settings.enable_p1 is None:
		settings.enable_p1 = 1
	if not settings.sync_lookback_days:
		settings.sync_lookback_days = 30
	if not settings.sync_schedule:
		settings.sync_schedule = "Daily"
	if settings.sync_cron_hour is None:
		settings.sync_cron_hour = 2
	if settings.document_poll_max_minutes is None:
		settings.document_poll_max_minutes = 15
	if settings.relay_subscription_enabled is None:
		settings.relay_subscription_enabled = 1
	settings.save(ignore_permissions=True)
