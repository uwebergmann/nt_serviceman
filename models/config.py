# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Konfigurationsmodell für NT:ServiceMan (NetBox)
# Speicherort: ir.config_parameter (Kap. 7.2 Pflichtenheft)
# -----------------------------------------------------------------------------

import json
from urllib.parse import urlparse

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

# Keys für ir.config_parameter
NETBOX_BASE_URL_KEY = "nt_serviceman.netbox_base_url"
NETBOX_API_TOKEN_KEY = "nt_serviceman.netbox_api_token"
NETBOX_LAST_SYNC_ALL_KEY = "nt_serviceman.netbox_last_sync_all_timestamp"
NETBOX_LAST_FULL_SYNC_AT_KEY = "nt_serviceman.netbox_last_full_sync_at"
NETBOX_LAST_FULL_SYNC_STATE_KEY = "nt_serviceman.netbox_last_full_sync_state"
NETBOX_LAST_FULL_SYNC_ERROR_KEY = "nt_serviceman.netbox_last_full_sync_error"
NETBOX_DEVICE_FIELD_NAMES_KEY = "nt_serviceman.netbox_device_field_names"
NETBOX_DEVICE_SAMPLE_KEY = "nt_serviceman.netbox_device_sample"


class NTServiceManConfig(models.Model):
    """Globale Konfiguration für NT:ServiceMan (NetBox-Anbindung).
    URL und Token werden in ir.config_parameter gespeichert.
    Chatter: Log-Einträge geplanter Vollabgleich (Kap. 9.5).
    """

    _name = "nt_serviceman.config"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
    last_full_sync_at = fields.Datetime(
        string="Letzter Vollabgleich",
        compute="_compute_last_full_sync",
        help="Zeitpunkt des letzten geplanten Vollabgleichs.",
    )
    last_full_sync_state = fields.Char(
        string="Status Vollabgleich",
        compute="_compute_last_full_sync",
        help="ok oder failed.",
    )
    last_full_sync_error = fields.Text(
        string="Fehler Vollabgleich",
        compute="_compute_last_full_sync",
        help="Fehlermeldung falls letzter Lauf fehlgeschlagen.",
    )

    @api.depends()
    def _compute_last_full_sync(self):
        """Liest aus ir.config_parameter (Kap. 9.5)."""
        icp = self.env["ir.config_parameter"].sudo()
        at_val = icp.get_param(NETBOX_LAST_FULL_SYNC_AT_KEY, "")
        state_val = icp.get_param(NETBOX_LAST_FULL_SYNC_STATE_KEY, "")
        error_val = icp.get_param(NETBOX_LAST_FULL_SYNC_ERROR_KEY, "") or ""
        for rec in self:
            rec.last_full_sync_at = at_val if at_val else False
            rec.last_full_sync_state = state_val or ""
            rec.last_full_sync_error = error_val

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

    def action_sync_all_cis_from_netbox(self, force_full=False):
        """Holt alle CI von NetBox (Kap. 9.4). Delta-Sync wenn möglich."""
        self.ensure_one()
        return self.env["nt_serviceman.configuration_item"].with_context(
            force_full_sync=force_full
        ).action_sync_all_from_netbox()

    def action_sync_all_cis_full_from_netbox(self):
        """Vollabgleich: Ruft run_scheduled_full_sync (dieselbe Logik wie Cron),
        schreibt Chatter + Status, zeigt Browser-Notification."""
        self.ensure_one()
        try:
            result = self.run_scheduled_full_sync()
        except Exception as e:
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
        if result["created"]:
            parts.append(_("%s CI neu") % result["created"])
        if result["updated"]:
            parts.append(_("%s aktualisiert") % result["updated"])
        if result["archived"]:
            parts.append(_("%s archiviert") % result["archived"])
        parts.append(_("%s aktive CI in Odoo") % result["active_count"])

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("CI abgerufen"),
                "message": "; ".join(parts),
                "type": "success",
                "sticky": False,
                "next": self.env.ref("nt_serviceman.action_configuration_item").id,
            },
        }

    @api.model
    def run_scheduled_full_sync(self):
        """Vollabgleich (Cron + Button, Kap. 9.5). Sync, speichert Status, postet Chatter.
        Returns result dict on success, raises on error."""
        Config = self.env["nt_serviceman.config"].sudo()
        config = Config.search([], limit=1)
        if not config:
            config = Config.create({})

        ci_model = self.env["nt_serviceman.configuration_item"].sudo()
        icp = self.env["ir.config_parameter"].sudo()
        now_str = fields.Datetime.now()

        try:
            result = ci_model._run_sync_all_from_netbox(force_full=True)
            icp.set_param(NETBOX_LAST_FULL_SYNC_AT_KEY, now_str)
            icp.set_param(NETBOX_LAST_FULL_SYNC_STATE_KEY, "ok")
            icp.set_param(NETBOX_LAST_FULL_SYNC_ERROR_KEY, "")

            msg = _(
                "Vollabgleich abgeschlossen: %s neu, %s aktualisiert, %s archiviert; %s aktive CI in Odoo."
            ) % (
                result["created"],
                result["updated"],
                result["archived"],
                result["active_count"],
            )
            config.message_post(
                body=msg,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            config.invalidate_cache(
                fnames=["last_full_sync_at", "last_full_sync_state", "last_full_sync_error"]
            )
            return result

        except Exception as e:
            icp.set_param(NETBOX_LAST_FULL_SYNC_AT_KEY, now_str)
            icp.set_param(NETBOX_LAST_FULL_SYNC_STATE_KEY, "failed")
            icp.set_param(NETBOX_LAST_FULL_SYNC_ERROR_KEY, str(e))

            config.message_post(
                body=_("Vollabgleich fehlgeschlagen: %s") % str(e),
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            config.invalidate_cache(
                fnames=["last_full_sync_at", "last_full_sync_state", "last_full_sync_error"]
            )
            raise

    @api.model
    def _get_netbox_device_field_names(self):
        """Liefert die gecachten NetBox-Device-Feldnamen (aus Schema)."""
        icp = self.env["ir.config_parameter"].sudo()
        raw = icp.get_param(NETBOX_DEVICE_FIELD_NAMES_KEY, "") or ""
        if not raw.strip():
            return []
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []

    @api.model
    def _get_netbox_device_sample(self):
        """Liefert das gecachte Beispiel-Device (für Anzeige mit Werten)."""
        icp = self.env["ir.config_parameter"].sudo()
        raw = icp.get_param(NETBOX_DEVICE_SAMPLE_KEY, "") or ""
        if not raw.strip():
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    @api.model
    def _get_value_by_path(self, data, path):
        """Liest Wert aus verschachteltem Dict via Pfad (z.B. device_type.manufacturer.name)."""
        if not data or not path:
            return None
        parts = path.split(".")
        obj = data
        for part in parts:
            if not isinstance(obj, dict):
                return None
            obj = obj.get(part)
        return obj

    @api.model
    def _format_field_value(self, val):
        """Formatiert einen Feldwert für die Anzeige (nur wenn gefüllt)."""
        if val is None:
            return None
        if isinstance(val, dict):
            return val.get("display") or val.get("name") or val.get("model") or str(val)
        if isinstance(val, list):
            if not val:
                return None
            first = val[0]
            if isinstance(first, dict):
                d = first.get("display") or first.get("name")
                if d:
                    return f"{d}" + (f" (+{len(val)-1})" if len(val) > 1 else "")
            return str(val) if len(val) <= 2 else f"{val[0]} (+{len(val)-1})"
        if isinstance(val, bool):
            return "Ja" if val else "Nein"
        s = str(val).strip()
        return s if s else None

    def _extract_fields_from_schema_properties(self, props, components, prefix=""):
        """Rekursiv: Feldnamen aus OpenAPI-Schema-Properties extrahieren."""
        if not props or not isinstance(props, dict):
            return []
        result = []
        for key, prop in props.items():
            if not isinstance(prop, dict):
                continue
            path = f"{prefix}.{key}" if prefix else key
            result.append(path)
            ref = prop.get("$ref")
            if ref:
                schema_name = ref.split("/")[-1] if ref.startswith("#/") else ref
                components = components or {}
                comp_schemas = components.get("schemas") or components.get("components", {}).get("schemas", {})
                sub = comp_schemas.get(schema_name)
                if sub and isinstance(sub, dict):
                    sub_props = sub.get("properties") or sub.get("items", {}).get("properties")
                    if sub_props:
                        result.extend(
                            self._extract_fields_from_schema_properties(
                                sub_props, components, path
                            )
                        )
            elif prop.get("type") == "object":
                sub_props = prop.get("properties") or {}
                if sub_props:
                    result.extend(
                        self._extract_fields_from_schema_properties(
                            sub_props, components, path
                        )
                    )
        return result

    def _extract_device_fields_from_schema(self, schema_dict):
        """Extrahiert Device-Felder aus NetBox OpenAPI-Schema."""
        if not schema_dict or not isinstance(schema_dict, dict):
            return []
        paths = schema_dict.get("paths") or {}
        comp_schemas = {}
        comp = schema_dict.get("components")
        if isinstance(comp, dict):
            comp_schemas = comp.get("schemas") or {}
        if not comp_schemas and isinstance(schema_dict.get("schemas"), dict):
            comp_schemas = schema_dict.get("schemas")
        device_schema = None
        for path_key, path_val in sorted(paths.items(), key=lambda x: ("{id}" not in x[0], x[0])):
            if "devices" not in path_key or not isinstance(path_val, dict):
                continue
            get_spec = path_val.get("get")
            if not get_spec or not isinstance(get_spec, dict):
                continue
            responses = (get_spec.get("responses") or {}).get("200") or {}
            content = (responses.get("content") or {}).get("application/json") or {}
            schema = content.get("schema")
            if not schema:
                continue
            ref = schema.get("$ref")
            if ref:
                name = ref.split("/")[-1]
                device_schema = comp_schemas.get(name) or schema
            else:
                device_schema = schema
            if device_schema:
                break
        if not device_schema:
            for name, sch in comp_schemas.items():
                if "device" in name.lower() and name.lower() != "nesteddevice":
                    device_schema = sch
                    break
        if not device_schema:
            return []
        props = device_schema.get("properties") or {}
        fields_raw = self._extract_fields_from_schema_properties(
            props, {"schemas": comp_schemas}
        )
        return sorted(set(fields_raw))

    @api.model
    def _expand_custom_fields_in_field_list(self, fields_list, sample_device=None):
        """Ersetzt 'custom_fields' durch einzelne Felder (custom_fields.license, etc.).
        Benutzer legen in NetBox weitere Custom Fields an – diese sollen einzeln verfügbar sein.
        """
        if not fields_list or not sample_device or not isinstance(sample_device, dict):
            return fields_list
        cf = sample_device.get("custom_fields")
        if not isinstance(cf, dict):
            return fields_list
        out = [f for f in fields_list if f != "custom_fields"]
        for key in sorted(cf.keys()):
            path = f"custom_fields.{key}"
            if path not in out:
                out.append(path)
        return sorted(set(out))

    def _extract_fields_from_dict(self, data, prefix=""):
        """Extrahiert Feldpfade rekursiv aus einem JSON-Dict (Fallback wenn Schema fehlschlägt)."""
        if not isinstance(data, dict):
            return []
        result = []
        for key, val in data.items():
            path = f"{prefix}.{key}" if prefix else key
            result.append(path)
            if isinstance(val, dict) and val:
                result.extend(self._extract_fields_from_dict(val, path))
            elif isinstance(val, list) and val and isinstance(val[0], dict):
                result.extend(self._extract_fields_from_dict(val[0], path))
        return result

    def _fetch_one_device_json(self, base_url, token):
        """Lädt ein beliebiges Device als Beispiel (für Anzeige mit Werten)."""
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Token {token}"
        base_url = base_url.rstrip("/")
        list_url = f"{base_url}/api/dcim/devices/?limit=1"
        try:
            r = requests.get(list_url, headers=headers, timeout=30, verify=False)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, json.JSONDecodeError):
            return None
        results = data.get("results") or []
        if not results:
            return None
        device_id = results[0].get("id")
        if not device_id:
            return None
        detail_url = f"{base_url}/api/dcim/devices/{device_id}/"
        try:
            r2 = requests.get(detail_url, headers=headers, timeout=30, verify=False)
            r2.raise_for_status()
            return r2.json()
        except (requests.RequestException, json.JSONDecodeError):
            return None

    def _fetch_device_fields_from_sample(self, base_url, token):
        """Fallback: Ein Device abrufen und Feldnamen aus dem JSON extrahieren (Option A)."""
        device = self._fetch_one_device_json(base_url, token)
        if not device:
            return [], None
        fields_list = sorted(set(self._extract_fields_from_dict(device)))
        return fields_list, device

    def action_refresh_netbox_device_fields(self):
        """Lädt Device-Felder aus NetBox-Schema und speichert sie (Kap. 8.11.1a)."""
        self.ensure_one()
        base_url, token = self._get_netbox_params()
        if not base_url:
            raise UserError("Keine NetBox-URL konfiguriert.")
        url = f"{base_url.rstrip('/')}/api/schema/"
        if "?" not in url:
            url += "?format=json"
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Token {token}"
        try:
            r = requests.get(url, headers=headers, timeout=90, verify=False)
            r.raise_for_status()
        except requests.RequestException as e:
            raise UserError(
                f"NetBox-Schema konnte nicht geladen werden: {e}"
            ) from e
        try:
            schema_dict = r.json()
        except json.JSONDecodeError:
            schema_dict = None
        fields_list = []
        sample_device = None
        if schema_dict:
            fields_list = self._extract_device_fields_from_schema(schema_dict)
        if not fields_list:
            fields_list, sample_device = self._fetch_device_fields_from_sample(
                base_url, token
            )
        if not fields_list:
            raise UserError(
                "NetBox-Device-Felder konnten nicht ermittelt werden. "
                "Schema-Abruf lieferte kein gültiges JSON oder keine Felder; "
                "Fallback (Device-Abruf) ebenfalls fehlgeschlagen. "
                "Prüfen Sie NetBox-URL, API-Token und ob unter /api/dcim/devices/ Geräte existieren."
            )
        if not sample_device:
            sample_device = self._fetch_one_device_json(base_url, token)
        # custom_fields in separate Felder aufteilen (Kap. 8.11; Benutzer legen weitere an)
        fields_list = self._expand_custom_fields_in_field_list(fields_list, sample_device)
        icp = self.env["ir.config_parameter"].sudo()
        icp.set_param(NETBOX_DEVICE_FIELD_NAMES_KEY, json.dumps(fields_list))
        icp.set_param(
            NETBOX_DEVICE_SAMPLE_KEY,
            json.dumps(sample_device) if sample_device else "",
        )
        # Feldlisten aller Leistungen mit neuer Konfiguration synchronisieren
        self.env["nt_serviceman.service"].search([])._ensure_required_device_field_lines()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Device-Felder geladen",
                "message": f"{len(fields_list)} Felder aus NetBox-Schema extrahiert.",
                "type": "success",
                "sticky": False,
            },
        }
