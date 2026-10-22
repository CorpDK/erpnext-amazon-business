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

After install, open **Amazon Business** workspace on the site. P0 ships schema and storefront master data only; purchase sync and PINV flows activate when phase **P1** is enabled in **Amazon Business Settings**.

## App layout

| Path | Purpose |
|------|---------|
| `erpnext_amazon_business/` | Frappe app package (`hooks.py`, DocTypes, workspace) |
| `docs/` | Product docs + `manifest.yaml` (CorpDK documentation framework) |
| `tests/` | Unit tests (storefront catalog); CI migrate job is a skeleton until bench wiring |

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

**P0-A** foundation: schema DocTypes, storefront master catalog, phase flags, workspace, ruff CI, unit tests. P0 scope detail: [docs/README.md](docs/README.md). Purchase sync and PINV flows ship under `enable_p1` in P1.
