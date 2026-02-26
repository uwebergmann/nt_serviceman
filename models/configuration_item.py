# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Configuration Item (CI) – Gerät aus NetBox
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

import json
from datetime import datetime

import markupsafe
import requests

from odoo import fields, models


class ConfigurationItem(models.Model):
    """Configuration Item – technisches Gerät aus NetBox."""

    _name = "nt_serviceman.configuration_item"
    _description = "Configuration Item (CI)"

    name = fields.Char(
        string="Name",
        help="Wird bei 'Hole NetBox-Item' automatisch aus dem Anzeigenamen übernommen.",
    )
    netbox_id = fields.Char(string="NetBox-ID")
    netbox_display = fields.Char(
        string="Anzeigename",
        readonly=True,
        help="Display-Name aus NetBox.",
    )
    netbox_display_url = fields.Char(
        string="NetBox-URL",
        readonly=True,
        help="Link zum Gerät in der NetBox-Weboberfläche.",
    )
    netbox_display_link = fields.Html(
        string="Anzeigename",
        compute="_compute_netbox_display_link",
        sanitize=False,
    )
    netbox_serial = fields.Char(
        string="Serial",
        readonly=True,
    )
    netbox_device_type = fields.Char(
        string="Hardware-Typ",
        readonly=True,
    )
    netbox_role_id = fields.Many2one(
        "nt_serviceman.netbox_device_role",
        string="NetBox Device Role",
        readonly=True,
        help="Device Role aus NetBox; über Mapping zur CI-Klasse.",
    )
    netbox_role_netbox_id = fields.Integer(
        string="Device Role NetBox-ID",
        related="netbox_role_id.netbox_id",
        readonly=True,
    )
    ci_class_id = fields.Many2one(
        "nt_serviceman.ci_class",
        string="CI-Klasse",
        related="netbox_role_id.ci_class_id",
        readonly=True,
        help="Leitet sich aus dem Mapping Device Role → CI-Klasse ab.",
    )
    netbox_tenant_name = fields.Char(
        string="Tenant",
        readonly=True,
    )
    netbox_created = fields.Datetime(
        string="NetBox erstellt",
        readonly=True,
        help="Erstellungszeitpunkt aus NetBox",
    )
    netbox_last_updated = fields.Datetime(
        string="NetBox zuletzt geändert",
        readonly=True,
        help="Letzte Änderung in NetBox; steuert die Sync-Logik",
    )
    netbox_last_sync = fields.Datetime(
        string="Letzter Abruf",
        readonly=True,
    )
    netbox_sync_state = fields.Selection(
        [("ok", "OK"), ("failed", "Fehlgeschlagen")],
        string="Sync-Status",
        readonly=True,
    )
    netbox_sync_error = fields.Text(
        string="Sync-Fehler",
        readonly=True,
        help="Wird nur bei Fehlern angezeigt.",
    )
    netbox_raw_response = fields.Text(
        string="NetBox Rohdaten (JSON)",
        readonly=True,
        help="Rohe API-Antwort von NetBox (Debugging).",
    )

    def _parse_netbox_datetime(self, val):
        """NetBox created/last_updated → Odoo Datetime-String (UTC)."""
        if not val:
            return False
        s = str(val).strip().replace("Z", "+00:00")
        try:
            if "T" in s:
                dt = datetime.fromisoformat(s)
            else:
                dt = datetime.fromisoformat(s[:10] + "T00:00:00+00:00")
        except (ValueError, TypeError):
            return False
        return fields.Datetime.to_string(dt) if dt else False

    def _compute_netbox_display_link(self):
        """Klickbarer Anzeigename als Link zu NetBox."""
        for rec in self:
            if rec.netbox_display_url and rec.netbox_display:
                url = markupsafe.escape(rec.netbox_display_url)
                text = markupsafe.escape(rec.netbox_display)
                rec.netbox_display_link = markupsafe.Markup(
                    f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>'
                )
            else:
                rec.netbox_display_link = markupsafe.Markup(
                    markupsafe.escape(rec.netbox_display or "")
                )

    def _extract_netbox_fields(self, data):
        """Extrahiert Anzeigename, Serial, Hardware-Typ, Rolle, Tenant und Timestamps aus NetBox-JSON."""
        data = data or {}
        display = data.get("display") or ""
        self.netbox_display = display
        if display:
            self.name = display
        self.netbox_display_url = data.get("display_url") or ""
        self.netbox_serial = data.get("serial") or ""
        device_type = data.get("device_type") or {}
        self.netbox_device_type = device_type.get("display") or device_type.get("model") or ""
        role = data.get("role") or data.get("device_role")
        role_nb_id = None
        if isinstance(role, dict):
            role_nb_id = role.get("id")
        elif isinstance(role, (int, float)):
            role_nb_id = int(role)
        if role_nb_id is not None:
            try:
                role_nb_id = int(role_nb_id)
            except (TypeError, ValueError):
                role_nb_id = None
        if role_nb_id:
            device_role = self.env["nt_serviceman.netbox_device_role"].search(
                [("netbox_id", "=", role_nb_id)], limit=1
            )
            self.netbox_role_id = device_role if device_role else False
        else:
            self.netbox_role_id = False
        tenant = data.get("tenant") or {}
        self.netbox_tenant_name = tenant.get("display") or tenant.get("name") or ""
        self.netbox_created = self._parse_netbox_datetime(data.get("created"))
        self.netbox_last_updated = self._parse_netbox_datetime(data.get("last_updated"))

    def action_fetch_from_netbox(self):
        """Ruft das Gerät per REST aus NetBox ab und speichert die Rohdaten."""
        self.ensure_one()
        config = self.env["nt_serviceman.config"].search([], limit=1)
        base_url = (config.netbox_base_url or "").strip().rstrip("/")
        nb_id = (self.netbox_id or "").strip()

        if not base_url:
            self.netbox_raw_response = '{"error": "Keine NetBox-URL konfiguriert."}'
            self._extract_netbox_fields({})
            self.netbox_sync_state = "failed"
            self.netbox_sync_error = "Keine NetBox-URL konfiguriert."
            return

        if not nb_id:
            self.netbox_raw_response = '{"error": "Keine NetBox-ID eingetragen."}'
            self._extract_netbox_fields({})
            self.netbox_sync_state = "failed"
            self.netbox_sync_error = "Keine NetBox-ID eingetragen."
            return

        url = f"{base_url}/api/dcim/devices/{nb_id}/"
        headers = {}
        token = (config.netbox_api_token or "").strip()
        if token:
            headers["Authorization"] = f"Token {token}"

        try:
            r = requests.get(url, headers=headers, timeout=15, verify=False)
            r.raise_for_status()
            data = r.json()
            nb_last_updated = self._parse_netbox_datetime(data.get("last_updated"))

            # Sync-Logik: nur aktualisieren wenn Feld leer oder NetBox jünger
            do_update = False
            if not self.netbox_last_updated:
                do_update = True
            elif nb_last_updated:
                nb_dt = fields.Datetime.from_string(nb_last_updated)
                local_dt = fields.Datetime.from_string(self.netbox_last_updated)
                if nb_dt > local_dt:
                    do_update = True

            if do_update:
                self.netbox_raw_response = json.dumps(data, indent=2, ensure_ascii=False)
                self._extract_netbox_fields(data)
                self.netbox_last_sync = fields.Datetime.now()
                self.netbox_sync_state = "ok"
                self.netbox_sync_error = False
        except requests.RequestException as e:
            self._extract_netbox_fields({})
            self.netbox_sync_state = "failed"
            err_response = getattr(e, "response", None)
            if err_response is not None and err_response.text:
                try:
                    self.netbox_raw_response = json.dumps(
                        json.loads(err_response.text),
                        indent=2,
                        ensure_ascii=False,
                    )
                except Exception:
                    self.netbox_raw_response = err_response.text
                self.netbox_sync_error = err_response.text[:500]
            else:
                self.netbox_raw_response = json.dumps(
                    {"error": str(e)},
                    indent=2,
                )
                self.netbox_sync_error = str(e)
        except (json.JSONDecodeError, ValueError) as e:
            self._extract_netbox_fields({})
            self.netbox_sync_state = "failed"
            self.netbox_sync_error = str(e)
            self.netbox_raw_response = json.dumps(
                {"error": f"Kein gültiges JSON: {e}"},
                indent=2,
            )
