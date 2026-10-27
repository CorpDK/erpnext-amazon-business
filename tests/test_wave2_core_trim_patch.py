"""Behavioral tests for wave2_core_trim migrate patch (execute() side effects)."""

from __future__ import annotations

import importlib
import sys
import unittest

from tests import frappe_unit_stub  # noqa: F401 — installs frappe stub


class FrappeLikeDB:
	"""Minimal frappe.db stand-in with table/column semantics used by the patch."""

	def __init__(
		self,
		*,
		tables: set[str],
		columns: dict[str, set[str]],
	) -> None:
		self._tables = set(tables)
		self._columns = {k: set(v) for k, v in columns.items()}
		self.sql_calls: list[tuple] = []
		self.sql_ddl_calls: list[tuple] = []

	def table_exists(self, doctype: str) -> bool:
		table = doctype if doctype.startswith("tab") else f"tab{doctype}"
		return table in self._tables

	def has_column(self, doctype: str, column: str) -> bool:
		table = doctype if doctype.startswith("tab") else f"tab{doctype}"
		if table not in self._tables:
			raise RuntimeError(f"Unknown column {column} on {table}")
		return column in self._columns.get(table, set())

	def sql(self, query: str, *args, **kwargs):
		self.sql_calls.append(("sql", query.strip(), args, kwargs))
		return None

	def sql_ddl(self, query: str, *args, **kwargs):
		self.sql_ddl_calls.append(("sql_ddl", query.strip(), args, kwargs))
		return None


def _load_execute():
	mod_name = "erpnext_amazon_business.patches.v0_2.wave2_core_trim"
	if mod_name in sys.modules:
		return importlib.reload(sys.modules[mod_name]).execute
	return importlib.import_module(mod_name).execute


class TestWave2CoreTrimPatch(unittest.TestCase):
	def test_skips_all_sql_when_company_config_table_missing(self) -> None:
		frappe = sys.modules["frappe"]
		frappe.db = FrappeLikeDB(tables=set(), columns={})
		execute = _load_execute()

		execute()

		self.assertEqual(frappe.db.sql_calls, [])
		self.assertEqual(frappe.db.sql_ddl_calls, [])

	def test_renames_integration_enabled_when_legacy_column_present(self) -> None:
		table = "tabAmazon Business Company Config"
		frappe = sys.modules["frappe"]
		frappe.db = FrappeLikeDB(
			tables={table},
			columns={table: {"integration_enabled", "name"}},
		)
		execute = _load_execute()

		execute()

		self.assertEqual(len(frappe.db.sql_calls), 2)
		self.assertIn("amazon_integration_enabled", frappe.db.sql_calls[0][1])
		self.assertIn("integration_enabled", frappe.db.sql_calls[1][1])
		self.assertEqual(len(frappe.db.sql_ddl_calls), 1)
		self.assertIn("DROP COLUMN integration_enabled", frappe.db.sql_ddl_calls[0][1])

	def test_no_op_when_table_exists_without_legacy_column(self) -> None:
		table = "tabAmazon Business Company Config"
		frappe = sys.modules["frappe"]
		frappe.db = FrappeLikeDB(
			tables={table},
			columns={table: {"amazon_integration_enabled", "name"}},
		)
		execute = _load_execute()

		execute()

		self.assertEqual(frappe.db.sql_calls, [])
		self.assertEqual(frappe.db.sql_ddl_calls, [])

	def test_pre_fix_has_column_tab_prefix_raises_without_table(self) -> None:
		"""Regression: old patch called has_column with tab-prefixed name before any guard."""
		frappe = sys.modules["frappe"]
		db = FrappeLikeDB(tables=set(), columns={})
		frappe.db = db

		with self.assertRaises(RuntimeError):
			frappe.db.has_column("tabAmazon Business Company Config", "integration_enabled")


if __name__ == "__main__":
	unittest.main()
