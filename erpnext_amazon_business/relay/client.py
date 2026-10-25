"""GraphQL client configuration and mutations for the Amazon Business relay."""

from __future__ import annotations

from typing import Any

import frappe
import requests

REGISTER_SITE_MUTATION = """
mutation RegisterSite($input: RegisterSiteInput!) {
  registerSite(input: $input) {
    sitePairingId
    pairingSecret
  }
}
"""

OAUTH_PENDING_QUERY = """
query OauthPending($sitePairingId: String!, $company: String!, $storefront: String!) {
  oauthPending(sitePairingId: $sitePairingId, company: $company, storefront: $storefront) {
    status
    refreshToken
    accessToken
    expiresAt
  }
}
"""


def get_graphql_config() -> dict[str, str]:
	"""Pairing and GraphQL endpoint for relay workers and sibling apps."""
	settings = frappe.get_single("Amazon Business Settings")
	url = settings.relay_graphql_url
	pairing_id = settings.site_pairing_id
	secret = settings.get_password("pairing_secret", raise_exception=False)
	if not url or not pairing_id or not secret:
		raise frappe.ValidationError("Relay GraphQL URL, site pairing id, and pairing secret are required")
	return {
		"graphql_url": url,
		"site_pairing_id": pairing_id,
		"pairing_secret": secret,
		"relay_base_url": settings.relay_base_url or "",
	}


def get_connection_mode() -> str:
	return frappe.get_single("Amazon Business Settings").connection_mode or "Relay"


def get_relay_client() -> dict[str, str]:
	return get_graphql_config()


def graphql_request(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
	config = get_graphql_config()
	response = requests.post(
		config["graphql_url"],
		json={"query": query, "variables": variables or {}},
		headers={"Authorization": f"Bearer {config['pairing_secret']}"},
		timeout=60,
	)
	if response.status_code >= 400:
		frappe.throw(f"Relay GraphQL HTTP {response.status_code}: {response.text}")
	payload = response.json()
	if payload.get("errors"):
		frappe.throw(f"Relay GraphQL errors: {payload['errors']}")
	return payload.get("data") or {}


def register_site(
	site_label: str,
	erp_version: str,
	registration_token: str,
) -> dict[str, str]:
	"""Call relay registerSite and return pairing credentials."""
	data = graphql_request(
		REGISTER_SITE_MUTATION,
		{
			"input": {
				"siteLabel": site_label,
				"erpVersion": erp_version,
				"registrationToken": registration_token,
			}
		},
	)
	result = data.get("registerSite") or {}
	if not result.get("sitePairingId") or not result.get("pairingSecret"):
		frappe.throw("registerSite did not return pairing credentials")
	return {
		"site_pairing_id": result["sitePairingId"],
		"pairing_secret": result["pairingSecret"],
	}


def fetch_oauth_pending(company: str, storefront: str) -> dict[str, Any] | None:
	config = get_graphql_config()
	data = graphql_request(
		OAUTH_PENDING_QUERY,
		{
			"sitePairingId": config["site_pairing_id"],
			"company": company,
			"storefront": storefront,
		},
	)
	return data.get("oauthPending")
