# ERPNext Amazon Business

Frappe v16 app: Amazon Business buyer sync → purchase register, draft Purchase Invoices, and reconciliation. Optional [amazon-business-relay](https://github.com/CorpDK/amazon-business-relay) for OAuth and webhooks on private benches.

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).

## Requirements

- Frappe **v16** and **ERPNext v16** (`bench` with `erpnext` installed)
- Python **3.10+**

## Install on a bench

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/CorpDK/erpnext-amazon-business
bench --site your-site install-app erpnext_amazon_business
```

After install, open **Amazon Business** workspace on the site. P0 ships schema and storefront master data only; purchase sync and PINV flows activate when phase **P1** is enabled in **Amazon Business Settings**.

## Development

See [docs/README.md](docs/README.md) and the implementation plan in private CorpDK/ERP design docs.

## Status

P0-A foundation (schema, fixtures, CI). Feature phases: `enable_p1` … `enable_p4` on Settings.
