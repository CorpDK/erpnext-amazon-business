# ERPNext Amazon Business

Frappe v16 app: Amazon Business buyer sync → purchase register, draft Purchase Invoices, and reconciliation. Optional [amazon-business-relay](https://github.com/CorpDK/amazon-business-relay) for OAuth and webhooks on private benches.

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).

## Requirements

- Frappe **v16.x** and **ERPNext v16.x** on `bench` with `erpnext` (v17 is rejected at install/migrate)
- Python **3.10+**

## Install on a bench

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/CorpDK/erpnext-amazon-business
bench --site your-site install-app erpnext_amazon_business
```

After install, open **Amazon Business** workspace on the site. Core ships schema, storefront master data, and an OAuth **Connect** shell (Direct or Relay); purchase sync and PINV flows activate when phase **P1** is enabled in the sibling **Amazon Business Reconciliation** app (not on core Settings).

## App layout

| Path | Purpose |
|------|---------|
| `erpnext_amazon_business/` | Frappe app package (`hooks.py`, DocTypes, workspace) |
| `docs/` | Product docs + `manifest.yaml` (CorpDK documentation framework) |
| `tests/` | Unit tests (storefront catalog, OAuth state, Wave 2 auth gates); CI migrate job is a skeleton until bench wiring |

**Required apps:** `erpnext` (Frappe v16). **Optional:** `india_compliance`, `drive` — guarded in tax helpers for P1+.

## Development

See [docs/README.md](docs/README.md). Design specs: private **CorpDK/ERP** `docs/amazon-business-*.md`.

```bash
# from a v16 bench
bench get-app /path/to/this/repo   # or GitHub URL
bench --site your-site install-app erpnext_amazon_business
bench --site your-site migrate
```

## Status

**P0-A** foundation plus **Wave 2** core trim: schema DocTypes, storefront master catalog, workspace, OAuth Connect shell, sibling APIs (`get_access_token`, `resolve_storefront`), ruff CI, unit tests. Scope detail: [docs/README.md](docs/README.md). Sync, phase flags, and PINV defaults live on reconciliation/Books sibling apps per the three-app architecture.
