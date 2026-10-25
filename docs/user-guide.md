# Amazon Business — user guide (stub)

Core ships schema, master data, and an OAuth **Connect** shell. Purchase sync, Create Purchase Invoice, and reconciliation desk tools land with the **Amazon Business Reconciliation** app when phase **P1** is enabled there.

## What you can do today

1. Install the app on a Frappe v16 site with ERPNext and run `bench migrate` (applies Wave 2 rename patch when upgrading from older builds).
2. Open **Amazon Business** workspace.
3. As **System Manager**, configure **Amazon Business Settings** (connection mode Direct or Relay, LWA credentials, relay pairing when using Relay).
4. As **Accounts Manager**, create **Amazon Business Company Config** per ERP Company, set **Amazon Integration Enabled**, and add enabled storefront rows on the child table.
5. As **System Manager**, open **Connect storefronts** from the workspace to start Direct OAuth or pull relay OAuth for a company/storefront pair (requires a storefront row first).

Sibling Frappe apps call `resolve_storefront` and `get_access_token` server-side; tokens are stored on the company storefront child row when OAuth completes.

## Coming with reconciliation P1

- Scheduled and manual sync into **Amazon Business Purchase**
- **Create Purchase Invoice** and reconciliation desk tool

Refer to CorpDK/ERP design docs for the full product specification.
