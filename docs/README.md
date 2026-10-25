# ERPNext Amazon Business — documentation

Product documentation for the `erpnext_amazon_business` Frappe app. Authoritative design and API mapping specs remain in the private **CorpDK/ERP** monorepo; this tree tracks shipped user-facing docs and release readiness (`manifest.yaml`).

## P0 + Wave 2 core scope

- DocTypes: Settings (connection/LWA/relay only), Storefront master, Company Config (+ per-storefront child table with OAuth token fields)
- Eleven storefront master rows (api-mapping §17), seeded on `bench migrate` via
  `patches/v0_1/seed_storefronts` from `amazon_business/data/storefronts.py`
- Wave 2 patch `patches/v0_2/wave2_core_trim`: renames Company Config `integration_enabled` → `amazon_integration_enabled`; sync schedules, Drive paths, phase flags, and sync cursors are **removed from core** and owned by sibling apps (reconciliation / Books)
- **Amazon Business** workspace (configuration + **Connect storefronts** page)
- OAuth shell: Direct `oauth.handle_callback`, relay `registerSite` client + worker skeleton, desk Connect UX (**System Manager**)
- Python APIs for sibling apps: `resolve_storefront`, `get_access_token` (gated on integration/storefront enabled + Connected status)

Phase toggles `enable_p1` … `enable_p4` are on **Amazon Business Reconciliation Settings** when that app is installed (`phase_flags.phase_enabled` delegates there).

## Install

See the repository [README](../README.md) for `bench get-app` and `install-app` on Frappe v16.

## Manuals (planned)

| Audience | Path |
|----------|------|
| Users | `docs/manuals/external/user/` |
| Admins | `docs/manuals/external/admin/` |
| Developers | `docs/manuals/external/developer/` |

Start with [user-guide.md](user-guide.md) for Connect and configuration; sync and PINV desk flows remain P1 on the reconciliation app.
