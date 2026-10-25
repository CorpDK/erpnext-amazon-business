"""OAuth callback handling for Direct connection mode."""

from __future__ import annotations

from typing import Any

__all__ = ["handle_callback"]


def __getattr__(name: str) -> Any:
	if name == "handle_callback":
		from erpnext_amazon_business.oauth.callback import handle_callback

		return handle_callback
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
