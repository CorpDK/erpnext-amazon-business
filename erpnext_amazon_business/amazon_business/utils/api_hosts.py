"""Map storefront API region to Amazon Business API host."""

from __future__ import annotations

API_REGION_HOSTS = {
	"NA": "https://na.business-api.amazon.com",
	"EU": "https://eu.business-api.amazon.com",
	"FE": "https://jp.business-api.amazon.com",
}


def api_base_url_for_region(api_region: str) -> str:
	try:
		return API_REGION_HOSTS[api_region]
	except KeyError:
		raise ValueError(f"Unknown Amazon Business API region: {api_region}") from None
