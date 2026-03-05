# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Konfigurationsmodell für NT:ServiceMan (NetBox)
# Speicherort: ir.config_parameter (Kap. 7.2 Pflichtenheft)
# -----------------------------------------------------------------------------

from urllib.parse import urlparse

import requests

from odoo import api, fields, models

# Keys für ir.config_parameter
NETBOX_BASE_URL_KEY = "nt_serviceman.netbox_base_url"
NETBOX_API_TOKEN_KEY = "nt_serviceman.netbox_api_token"


class NTServiceManConfig(models.Model):
    """Globale Konfiguration für NT:ServiceMan (NetBox-Anbindung).
    URL und Token werden in ir.config_parameter gespeichert.
    """

    _name = "nt_serviceman.config"
    _description = "NT:ServiceMan Konfiguration"

    netbox_base_url = fields.Char(
        string="NetBox-URL",
        compute="_compute_netbox_params",
        inverse="_inverse_netbox_base_url",
        store=False,
        help="Basis-URL der NetBox-Instanz (z.B. https://netbox.example.com)",
    )
    netbox_api_token = fields.Char(
        string="NetBox API-Token",
        compute="_compute_netbox_params",
        inverse="_inverse_netbox_api_token",
        store=False,
        help="API-Token für NetBox-Authentifizierung. In NetBox: My Account → API Tokens",
    )
    netbox_test_result = fields.Text(
        string="Test-Ergebnis",
        readonly=True,
        help="Ergebnis des NetBox-URL-Tests.",
    )

    def name_get(self):
        return [(r.id, "Einstellungen NT:ServiceMan") for r in self]

    @api.depends()
    def _compute_netbox_params(self):
        """Liest URL und Token aus ir.config_parameter."""
        icp = self.env["ir.config_parameter"].sudo()
        url = icp.get_param(NETBOX_BASE_URL_KEY, "") or ""
        token = icp.get_param(NETBOX_API_TOKEN_KEY, "") or ""
        for rec in self:
            rec.netbox_base_url = url
            rec.netbox_api_token = token

    def _inverse_netbox_base_url(self):
        """Speichert URL in ir.config_parameter."""
        icp = self.env["ir.config_parameter"].sudo()
        for rec in self:
            icp.set_param(NETBOX_BASE_URL_KEY, (rec.netbox_base_url or "").strip())

    def _inverse_netbox_api_token(self):
        """Speichert Token in ir.config_parameter."""
        icp = self.env["ir.config_parameter"].sudo()
        for rec in self:
            icp.set_param(NETBOX_API_TOKEN_KEY, (rec.netbox_api_token or "").strip())

    @api.model
    def _get_netbox_params(self):
        """Liefert (base_url, token) aus ir.config_parameter. Für interne Nutzung."""
        icp = self.env["ir.config_parameter"].sudo()
        url = (icp.get_param(NETBOX_BASE_URL_KEY, "") or "").strip().rstrip("/")
        token = (icp.get_param(NETBOX_API_TOKEN_KEY, "") or "").strip()
        return url, token

    def _validate_netbox_url(self, url):
        """Prüft URL gegen SSRF: nur http(s), gültiger Host."""
        raw = (url or '').strip()
        if not raw:
            return False, "Keine URL angegeben."
        parsed = urlparse(raw)
        if parsed.scheme not in ('http', 'https'):
            return False, "Nur http:// und https:// URLs erlaubt."
        if not parsed.netloc:
            return False, "Ungültige URL (kein Host)."
        return True, None

    def action_test_netbox_url(self):
        """Prüft NetBox-URL: (1) Server erreichbar, (2) NetBox erkannt, (3) REST-API."""
        self.ensure_one()
        base_url = (self.netbox_base_url or '').strip().rstrip('/')
        lines = []

        if not base_url:
            self.netbox_test_result = "❌ Keine NetBox-URL konfiguriert."
            return

        valid, err = self._validate_netbox_url(base_url)
        if not valid:
            self.netbox_test_result = f"❌ {err}"
            return

        kwargs = {"timeout": 10, "verify": False}
        token = (self.netbox_api_token or "").strip()
        if token:
            kwargs["headers"] = {"Authorization": f"Token {token}"}
        try:
            requests.get(base_url, **kwargs)
        except requests.ConnectionError:
            self.netbox_test_result = (
                "❌ 1. Server nicht erreichbar (Verbindung fehlgeschlagen). "
                "Prüfen Sie: https (nicht http)? Odoo-Server im gleichen Netz?"
            )
            return
        except requests.exceptions.SSLError as e:
            self.netbox_test_result = (
                f"❌ 1. SSL-Fehler (z.B. selbstsigniertes Zertifikat): {e}"
            )
            return
        except requests.Timeout:
            self.netbox_test_result = "❌ 1. Server nicht erreichbar (Timeout)."
            return
        except requests.RequestException as e:
            self.netbox_test_result = f"❌ 1. Server-Fehler: {type(e).__name__}: {e}"
            return

        lines.append("✅ 1. Server erreichbar.")

        api_url = f"{base_url}/api/"
        try:
            r_api = requests.get(api_url, **kwargs)
        except requests.RequestException as e:
            msg = f"❌ 2. REST-API nicht erreichbar: {type(e).__name__}: {e}"
            self.netbox_test_result = f"{lines[0]}\n{msg}"
            return

        if r_api.status_code not in (200, 401, 403):
            self.netbox_test_result = (
                f"{lines[0]}\n❌ 2. REST-API antwortet mit {r_api.status_code} – "
                "kein NetBox-/api/-Endpoint oder Fehler."
            )
            return

        lines.append("✅ 2. REST-API antwortet.")

        try:
            data = r_api.json()
        except ValueError:
            self.netbox_test_result = (
                f"{lines[0]}\n{lines[1]}\n❌ 3. Antwort ist kein JSON – "
                "vermutlich kein NetBox."
            )
            return

        if not isinstance(data, dict):
            self.netbox_test_result = (
                f"{lines[0]}\n{lines[1]}\n⚠️ 3. Unerwartetes Format – "
                "möglicherweise kein NetBox."
            )
            return

        if any(k in data for k in ('apps', 'routers', 'schema', 'types')):
            lines.append("✅ 3. NetBox-API-Struktur erkannt.")
        else:
            lines.append(
                "⚠️ 3. API-Struktur nicht eindeutig NetBox-typisch "
                "(aber JSON vorhanden)."
            )

        if not token:
            lines.append("⚠️ 4. Kein API-Token konfiguriert – Device-Abfragen werden fehlschlagen.")
        elif r_api.status_code == 200:
            lines.append("✅ 4. API-Token gültig.")
        elif r_api.status_code == 401:
            lines.append("❌ 4. API-Token ungültig oder abgelaufen.")
        elif r_api.status_code == 403:
            lines.append("❌ 4. API-Token hat keine Berechtigung.")
        else:
            lines.append(f"⚠️ 4. API-Token: unerwarteter Status {r_api.status_code}.")

        self.netbox_test_result = "\n".join(lines)

    def action_fetch_device_roles_from_netbox(self):
        """Ruft alle Device Roles von NetBox ab."""
        self.ensure_one()
        return self.env["nt_serviceman.netbox_device_role"].action_fetch_from_netbox()
