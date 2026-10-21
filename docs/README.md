# ERPNext Amazon Business — documentation

Product documentation for the `erpnext_amazon_business` Frappe app. Authoritative design and API mapping specs remain in the private **CorpDK/ERP** monorepo; this tree tracks shipped user-facing docs and release readiness (`manifest.yaml`).

## P0 scope

- DocTypes: Settings, Storefront master, Company Config (+ per-storefront child table)
- Eleven storefront fixtures (api-mapping §17)
- Phase flags `enable_p1` … `enable_p4` on Settings
- **Amazon Business** workspace (configuration links; purchase flows land in P1)

## Install

See the repository [README](../README.md) for `bench get-app` and `install-app` on Frappe v16.

## Manuals (planned)

| Audience | Path |
|----------|------|
| Users | `docs/manuals/external/user/` |
| Admins | `docs/manuals/external/admin/` |
| Developers | `docs/manuals/external/developer/` |

Start with [user-guide.md](user-guide.md) stub until P1 ships Connect and sync flows.
