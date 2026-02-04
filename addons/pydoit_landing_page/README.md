# Pydo-IT Landing Page (Odoo 19)

This module adds a coded landing page at:
- `/pydo-it` (landing)
- `/pydo-it/gracias` (thank you)

It includes a lead form that creates a `crm.lead` via Odoo's website form endpoint.

## Install
1. Copy this folder into your custom addons path (e.g. `./addons/`).
2. Restart Odoo, update apps list.
3. Install **Pydo-IT Landing Page**.

## Notes
- Requires `website`, `website_form`, `crm`, `website_crm`.
- If you want leads instead of opportunities, enable Leads in CRM settings.
