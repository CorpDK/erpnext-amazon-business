"""Install or extend a frappe module stub for unit tests (import before app code)."""

from __future__ import annotations

import sys
import types
from unittest import mock


class ValidationError(Exception):
	pass


class PermissionError(Exception):
	pass


def _throw(msg, exc=ValidationError, *args, **kwargs):
	if isinstance(exc, type) and issubclass(exc, BaseException):
		raise exc(msg)
	raise ValidationError(msg)


def ensure_frappe_unit_stub() -> None:
	if "frappe" in sys.modules:
		frappe_mod = sys.modules["frappe"]
	else:
		frappe_mod = types.ModuleType("frappe")
		sys.modules["frappe"] = frappe_mod

	frappe_mod.ValidationError = ValidationError
	frappe_mod.PermissionError = PermissionError
	frappe_mod.throw = _throw
	frappe_mod.conf = {"secret": "test-site-secret"}
	frappe_mod.local = types.SimpleNamespace(conf={"encryption_key": "test-site-secret"})
	frappe_mod.utils = types.SimpleNamespace(
		now_datetime=lambda: __import__("datetime").datetime(2026, 1, 1, 12, 0, 0),
		get_datetime=lambda s: (
			__import__("datetime").datetime.fromisoformat(s.replace("Z", "+00:00"))
			if isinstance(s, str)
			else s
		),
	)
	frappe_mod.db = mock.MagicMock()
	frappe_mod.get_all = mock.MagicMock()
	frappe_mod.get_doc = mock.MagicMock()
	frappe_mod.get_single = mock.MagicMock()
	frappe_mod.has_permission = mock.MagicMock(return_value=True)
	frappe_mod.respond_as_web_page = lambda *a, **k: None
	frappe_mod.publish_realtime = lambda *a, **k: None
	frappe_mod.whitelist = lambda *a, **k: lambda fn: fn


ensure_frappe_unit_stub()
