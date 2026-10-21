"""Catalog consistency tests (no Frappe bench required)."""

from __future__ import annotations

import unittest

from erpnext_amazon_business.amazon_business.data.storefronts import STOREFRONTS
from erpnext_amazon_business.amazon_business.utils.api_hosts import API_REGION_HOSTS, api_base_url_for_region


class TestStorefrontCatalog(unittest.TestCase):
	def test_fixture_row_count(self) -> None:
		self.assertEqual(len(STOREFRONTS), 11)

	def test_unique_storefront_keys(self) -> None:
		keys = [row["storefront"] for row in STOREFRONTS]
		self.assertEqual(len(keys), len(set(keys)))

	def test_oauth_base_matches_storefront_host(self) -> None:
		for row in STOREFRONTS:
			host = row["storefront"]
			self.assertIn(host, row["oauth_authorize_base"])
			self.assertTrue(row["oauth_authorize_base"].startswith("https://www."))

	def test_api_regions_have_hosts(self) -> None:
		regions = {row["api_region"] for row in STOREFRONTS}
		self.assertTrue(regions.issubset(API_REGION_HOSTS.keys()))
		for region in regions:
			url = api_base_url_for_region(region)
			self.assertTrue(url.startswith("https://"))


if __name__ == "__main__":
	unittest.main()
