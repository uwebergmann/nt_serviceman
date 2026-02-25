# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Konfigurationsmodell für NT:ServiceMan (NetBox)
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

from urllib.parse import urlparse

import requests

from odoo import fields, models


class NTServiceManConfig(models.Model):
    """Globale Konfiguration für NT:ServiceMan (NetBox-Anbindung)."""

    _name = "nt_serviceman.config"
    _description = "NT:ServiceMan Konfiguration"

    netbox_base_url = fields.Char(
        string="NetBox-URL",
        help="Basis-URL der NetBox-Instanz (z.B. https://netbox.example.com)",
    )
    netbox_api_token = fields.Char(
        string="NetBox API-Token",
        help="API-Token für NetBox-Authentifizierung. In NetBox: My Account → API Tokens",
    )
    netbox_test_result = fields.Text(
        string="Test-Ergebnis",
        readonly=True,
        help="Ergebnis des NetBox-URL-Tests.",
    )

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

        # verify=False für selbstsignierte Zertifikate (interne NetBox)
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

        # Test 2 & 3: NetBox-REST-API (GET /api/)
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

        # NetBox-typische Struktur? (JSON mit z.B. "apps" oder "routers")
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

        # NetBox API-Root: typisch "apps", "routers", "schema" oder "types"
        if any(k in data for k in ('apps', 'routers', 'schema', 'types')):
            lines.append("✅ 3. NetBox-API-Struktur erkannt.")
        else:
            lines.append(
                "⚠️ 3. API-Struktur nicht eindeutig NetBox-typisch "
                "(aber JSON vorhanden)."
            )

        # Test 4: API-Token prüfen
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
