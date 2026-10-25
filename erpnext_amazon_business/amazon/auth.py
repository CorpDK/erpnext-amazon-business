"""LWA access tokens for sibling Amazon Business API clients."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import frappe
import requests

LWA_TOKEN_URL = "https://api.amazon.com/auth/O2/token"
TOKEN_REFRESH_MARGIN = timedelta(minutes=5)


def get_access_token(company: str, storefront: str) -> str:
	"""Return a valid LWA access token for the company storefront connection."""
	row = connection_row(company, storefront)
	if not row:
		raise frappe.ValidationError(
			f"No Amazon Business connection for company={company}, storefront={storefront}"
		)
	_ensure_active_connection(row, company, storefront)

	expiry = row.token_expiry
	cached = row.get_password("access_token", raise_exception=False)
	if cached and expiry:
		expires_at = frappe.utils.get_datetime(expiry)
		if expires_at > frappe.utils.now_datetime() + TOKEN_REFRESH_MARGIN:
			return cached

	refresh = row.get_password("refresh_token", raise_exception=False)
	if not refresh:
		raise frappe.ValidationError(
			f"Storefront {storefront} is not connected for company {company}"
		)

	token_data = _exchange_refresh_token(refresh)
	_update_connection_tokens(row, token_data)
	return token_data["access_token"]


def _ensure_active_connection(row, company: str, storefront: str) -> None:
	if not frappe.db.get_value(
		"Amazon Business Company Config", row.parent, "amazon_integration_enabled"
	):
		raise frappe.ValidationError(
			f"Amazon Business integration is disabled for company {company}"
		)
	if not row.enabled:
		raise frappe.ValidationError(
			f"Storefront {storefront} is disabled for company {company}"
		)
	if row.connection_status != "Connected":
		raise frappe.ValidationError(
			f"Storefront {storefront} is not connected for company {company}"
		)


def connection_row(company: str, storefront: str):
	config_name = frappe.db.get_value(
		"Amazon Business Company Config", {"company": company}, "name"
	)
	if not config_name:
		return None

	for row in frappe.get_all(
		"Amazon Business Company Storefront",
		filters={"parent": config_name, "storefront": storefront},
		fields=["name"],
	):
		return frappe.get_doc("Amazon Business Company Storefront", row.name)
	return None


def _lwa_client_credentials() -> tuple[str, str]:
	settings = frappe.get_single("Amazon Business Settings")
	client_id = settings.lwa_client_id
	client_secret = settings.get_password("lwa_client_secret", raise_exception=False)
	if not client_id or not client_secret:
		raise frappe.ValidationError(
			"LWA client id and secret must be configured on Amazon Business Settings"
		)
	return client_id, client_secret


def _exchange_refresh_token(refresh_token: str) -> dict[str, Any]:
	client_id, client_secret = _lwa_client_credentials()
	response = requests.post(
		LWA_TOKEN_URL,
		data={
			"grant_type": "refresh_token",
			"refresh_token": refresh_token,
			"client_id": client_id,
			"client_secret": client_secret,
		},
		timeout=30,
	)
	if response.status_code >= 400:
		frappe.throw(f"LWA token refresh failed: {response.text}")
	return response.json()


def exchange_authorization_code(code: str, redirect_uri: str) -> dict[str, Any]:
	"""Exchange an OAuth authorization code for LWA tokens (Direct mode)."""
	client_id, client_secret = _lwa_client_credentials()
	response = requests.post(
		LWA_TOKEN_URL,
		data={
			"grant_type": "authorization_code",
			"code": code,
			"redirect_uri": redirect_uri,
			"client_id": client_id,
			"client_secret": client_secret,
		},
		timeout=30,
	)
	if response.status_code >= 400:
		frappe.throw(f"LWA code exchange failed: {response.text}")
	return response.json()


def _update_connection_tokens(row, token_data: dict[str, Any]) -> None:
	expires_in = int(token_data.get("expires_in", 3600))
	expiry = frappe.utils.now_datetime() + timedelta(seconds=expires_in)
	row.db_set("access_token", token_data["access_token"])
	if token_data.get("refresh_token"):
		row.db_set("refresh_token", token_data["refresh_token"])
	row.db_set("token_expiry", expiry)
	row.db_set("connection_status", "Connected")


def apply_token_payload(company: str, storefront: str, token_data: dict[str, Any]) -> None:
	"""Persist tokens on the company storefront row (relay worker / Direct callback)."""
	if not token_data.get("access_token"):
		raise frappe.ValidationError("OAuth token response is missing access_token")
	if not token_data.get("refresh_token"):
		raise frappe.ValidationError("OAuth token response is missing refresh_token")
	row = connection_row(company, storefront)
	if not row:
		raise frappe.ValidationError(
			f"No storefront row for company={company}, storefront={storefront}"
		)
	_update_connection_tokens(row, token_data)
