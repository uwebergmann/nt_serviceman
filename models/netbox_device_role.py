# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: NetBox Device Role – lokaler Spiegel der NetBox Device Roles
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

import requests

from odoo import _, fields, models


class NetBoxDeviceRole(models.Model):
    """NetBox Device Role – ausschließlich aus NetBox befüllt."""

    _name = "nt_serviceman.netbox_device_role"
    _description = "NetBox Device Role"
    _order = "name"

    netbox_id = fields.Integer(
        string="NetBox-ID",
        required=True,
        readonly=True,
        help="Eindeutige ID in NetBox",
    )
    name = fields.Char(
        string="Bezeichnung",
        required=True,
        readonly=True,
    )
    active = fields.Boolean(
        default=True,
        string="Aktiv",
        help="Archivierte Rollen werden nicht gelöscht, nur deaktiviert",
    )

    _sql_constraints = [
        ("netbox_id_unique", "UNIQUE(netbox_id)", "NetBox-ID muss eindeutig sein."),
    ]

    def action_fetch_from_netbox(self):
        """Holt alle Device Roles von NetBox und aktualisiert die lokale Tabelle."""
        config = self.env["nt_serviceman.config"].search([], limit=1)
        base_url = (config.netbox_base_url or "").strip().rstrip("/")
        token = (config.netbox_api_token or "").strip()

        if not base_url:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Fehler"),
                    "message": _("Keine NetBox-URL konfiguriert."),
                    "type": "danger",
                    "sticky": False,
                },
            }

        headers = {}
        if token:
            headers["Authorization"] = f"Token {token}"

        url = f"{base_url}/api/dcim/device-roles/"
        created = updated = archived = 0
        netbox_ids_seen = set()

        try:
            while url:
                r = requests.get(url, headers=headers, timeout=30, verify=False)
                r.raise_for_status()
                data = r.json()

                results = data.get("results", [])
                for item in results:
                    nb_id = item.get("id")
                    name_val = item.get("name") or item.get("display") or str(nb_id)
                    netbox_ids_seen.add(nb_id)

                    existing = self.sudo().search([("netbox_id", "=", nb_id)], limit=1)
                    if existing:
                        vals = {}
                        if existing.name != name_val:
                            vals["name"] = name_val
                        if not existing.active:
                            vals["active"] = True
                        if vals:
                            existing.sudo().write(vals)
                            updated += 1
                    else:
                        self.sudo().create({
                            "netbox_id": nb_id,
                            "name": name_val,
                        })
                        created += 1

                url = data.get("next")
                if url and not url.startswith("http"):
                    url = f"{base_url}{url}" if url.startswith("/") else None

            # Rollen, die in NetBox gelöscht wurden: lokal archivieren (active=False)
            obsolete = self.sudo().search([
                ("netbox_id", "not in", list(netbox_ids_seen)),
                ("active", "=", True),
            ])
            if obsolete:
                obsolete.sudo().write({"active": False})
                archived = len(obsolete)

        except requests.RequestException as e:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("NetBox-Fehler"),
                    "message": str(e),
                    "type": "danger",
                    "sticky": True,
                },
            }

        parts = []
        if created:
            parts.append(_("%s neu angelegt") % created)
        if updated:
            parts.append(_("%s aktualisiert") % updated)
        if archived:
            parts.append(_("%s archiviert (in NetBox gelöscht)") % archived)
        message = ", ".join(parts) if parts else _("Keine Änderungen.")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Device Roles abgerufen"),
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }
