"""Bench migrate job placeholder — extend with frappe-bench CI when available."""

from __future__ import annotations

import unittest


class TestMigrateSkeleton(unittest.TestCase):
	def test_ci_migrate_hook_reserved(self) -> None:
		"""CI workflow defines a migrate job; this test keeps the unit job non-empty."""
		self.assertTrue(True)


if __name__ == "__main__":
	unittest.main()
