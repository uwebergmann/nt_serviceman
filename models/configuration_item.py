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

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .config import NETBOX_LAST_SYNC_ALL_KEY


class ConfigurationItem(models.Model):
    """Configuration Item – technisches Gerät aus NetBox."""

    _name = "nt_serviceman.configuration_item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Configuration Item (CI)"

    active = fields.Boolean(
        default=True,
        string="Aktiv",
        help="Archivierte CIs (in NetBox gelöscht) werden nicht gelöscht, nur deaktiviert.",
    )

    _sql_constraints = [
        (
            "netbox_id_unique",
            "UNIQUE(netbox_id)",
            "Die NetBox-ID muss eindeutig sein. Jedes NetBox-Gerät darf nur einmal in Odoo existieren.",
        ),
    ]

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
        string="NetBox-Link",
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
        string="Partner",
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
    cmdb_id = fields.Integer(
        string="CMDB-ID",
        help="Legacy CMDB-ID (Abwärtskompatibilität); optional.",
    )
    contract_id = fields.Many2one(
        "contract.recurrent",
        string="Vertrag",
        ondelete="set null",
        help="Wiederkehrender Vertrag, dem dieses CI zugeordnet ist.",
    )
    contract_service_ids = fields.Many2many(
        "nt_serviceman.service",
        "nt_serviceman_ci_contract_service_rel",
        "configuration_item_id",
        "service_id",
        string="Gebuchte Leistungen",
        context={"active_test": False},
        help="Kopie aus der Vertrags-Leistungsmatrix (Kap. 11.3); inkl. archivierte Leistungen.",
    )
    gebuchte_leistungen_html = fields.Html(
        string="Gebuchte Leistungen (Anzeige)",
        compute="_compute_gebuchte_leistungen_html",
        sanitize=False,
        help="Punkt-Liste der gebuchten Leistungen (nur Bezeichnung) zur Anzeige im Formular.",
    )
    service_fields_status = fields.Selection(
        [
            ("ok", "Vollständig"),
            ("warning", "Fehlende Felder"),
            ("na", "Nicht prüfbar"),
        ],
        string="Service-Felder-Status",
        compute="_compute_service_fields_status",
        help="Kap. 8.11.2: Sind alle erforderlichen NetBox-Felder für die gebuchten Leistungen ausgefüllt?",
    )
    service_fields_status_icon = fields.Char(
        string="Status",
        compute="_compute_service_fields_status",
        help="Symbol: ✓ = vollständig, ⚠ = fehlende Felder (Kap. 8.11.2). Zeilenfarbe verstärkt.",
    )
    fehlende_felder_html = fields.Html(
        string="Fehlende Felder",
        compute="_compute_service_fields_status",
        sanitize=False,
        help="Kap. 8.11.3: Pro Leistung die fehlenden NetBox-Felder – bitte in NetBox nachpflegen.",
    )
    show_debug_json = fields.Boolean(
        string="Debug-JSON anzeigen",
        compute="_compute_show_debug_json",
        help="True wenn ?debug=1 in der URL steht – blendet Roh-JSON ein.",
    )

    def _compute_show_debug_json(self):
        """True wenn ?debug=1 in der URL steht (oder in der Session)."""
        show = False
        try:
            from odoo.http import request

            if request:
                show = (
                    getattr(request, "session", None)
                    and request.session.get("debug") == "1"
                ) or (
                    getattr(request, "httprequest", None)
                    and request.httprequest.args.get("debug") == "1"
                )
        except (RuntimeError, AttributeError):
            pass
        for rec in self:
            rec.show_debug_json = show

    @api.depends(
        "contract_id",
        "contract_service_ids",
        "contract_service_ids.required_device_field_ids",
        "netbox_raw_response",
        "netbox_display_url",
        "netbox_display",
    )
    def _compute_service_fields_status(self):
        """Prüft pro gebuchter Leistung ob alle erforderlichen Felder gefüllt sind (Kap. 8.11.2/8.11.3)."""
        config = self.env["nt_serviceman.config"]
        for rec in self:
            status = "na"
            icon_char = ""
            fehlende_html = markupsafe.Markup("")
            if not rec.contract_id or not rec.contract_service_ids:
                rec.service_fields_status = status
                rec.service_fields_status_icon = icon_char
                rec.fehlende_felder_html = fehlende_html
                continue
            data = {}
            if rec.netbox_raw_response:
                try:
                    data = json.loads(rec.netbox_raw_response)
                except (json.JSONDecodeError, TypeError):
                    pass
            if not isinstance(data, dict):
                status = "warning"
                icon_char = "⚠"
                fehlende_html = markupsafe.Markup(
                    "<p class='text-warning'>NetBox-Daten nicht verfügbar. "
                    "Bitte „Hole NetBox-Item“ ausführen.</p>"
                )
            else:
                missing_per_service = []
                for service in rec.contract_service_ids:
                    required = service.required_device_field_ids.filtered(
                        lambda f: f.is_required
                    )
                    fields_missing = []
                    for field_line in required:
                        val = config._get_value_by_path(data, field_line.field_path)
                        if not config._format_field_value(val):
                            fields_missing.append(field_line.field_path)
                    if fields_missing:
                        missing_per_service.append(
                            (service.name or service.code, fields_missing)
                        )
                if missing_per_service:
                    status = "warning"
                    icon_char = "⚠"
                    parts = []
                    for svc_name, field_paths in missing_per_service:
                        escaped_name = markupsafe.escape(svc_name)
                        field_list = ", ".join(
                            markupsafe.escape(p) for p in field_paths
                        )
                        parts.append(
                            f"<li><strong>{escaped_name}:</strong> {field_list}</li>"
                        )
                    netbox_link = ""
                    if rec.netbox_display_url:
                        url = markupsafe.escape(rec.netbox_display_url)
                        text = markupsafe.escape(
                            rec.netbox_display or "In NetBox öffnen"
                        )
                        netbox_link = (
                            f"<p class='mb-2'><a href='{url}' target='_blank' rel='noopener noreferrer' "
                            f"class='btn btn-sm btn-link'>🔗 {text}</a> – dort Felder pflegen, "
                            "dann „Hole NetBox-Item“ erneut ausführen.</p>"
                        )
                    fehlende_html = markupsafe.Markup(
                        netbox_link
                        + "<p class='text-warning mb-1'><strong>Fehlende Felder pro Leistung:</strong></p>"
                        + f"<ul class='mb-0'>{''.join(parts)}</ul>"
                    )
                else:
                    status = "ok"
                    icon_char = "✓"
                    fehlende_html = markupsafe.Markup(
                        "<p class='text-success mb-0'>✓ Alle erforderlichen Felder sind ausgefüllt.</p>"
                    )
            rec.service_fields_status = status
            rec.service_fields_status_icon = icon_char
            rec.fehlende_felder_html = fehlende_html

    @api.depends("contract_id", "contract_service_ids", "contract_service_ids.name", "contract_service_ids.active")
    def _compute_gebuchte_leistungen_html(self):
        """Erzeugt read-only Punkt-Listen: aktive Leistungen und separat archivierte (nicht mehr angeboten)."""
        for rec in self:
            if not rec.contract_id or not rec.contract_service_ids:
                rec.gebuchte_leistungen_html = False
                continue
            services = rec.contract_service_ids.sorted(key=lambda x: (x.sequence, x.name))
            active = services.filtered(lambda s: s.active)
            archived = services.filtered(lambda s: not s.active)
            parts = []
            if active:
                items = "".join(
                    f"<li>{markupsafe.escape(s.name or '')}</li>"
                    for s in active
                )
                parts.append(f"<ul class='mb-0'>{items}</ul>")
            if archived:
                items = "".join(
                    f"<li class='text-muted'>{markupsafe.escape(s.name or '')}</li>"
                    for s in archived
                )
                parts.append(
                    "<p class='text-muted small mb-1 mt-2'><strong>Nicht mehr angeboten:</strong></p>"
                    f"<ul class='mb-0 text-muted'>{items}</ul>"
                )
            rec.gebuchte_leistungen_html = markupsafe.Markup("".join(parts)) if parts else False

    @api.constrains("contract_id", "ci_class_id")
    def _check_contract_ci_class_in_matrix(self):
        """CI darf nur zugeordnet werden, wenn seine CI-Klasse in der Leistungsmatrix vorkommt."""
        for rec in self:
            if not rec.contract_id:
                continue
            if not rec.ci_class_id:
                raise ValidationError(
                    _(
                        "Das CI „%s“ hat keine CI-Klasse (kein Mapping Device Role → CI-Klasse). "
                        "Es kann keinem Vertrag zugeordnet werden."
                    )
                    % (rec.name or rec.netbox_display or rec.id)
                )
            allowed = rec.contract_id.ci_class_matrix_line_ids.mapped("ci_class_id")
            if rec.ci_class_id not in allowed:
                raise ValidationError(
                    _(
                        "Das CI „%s“ hat die CI-Klasse „%s“, "
                        "die in der Leistungsmatrix des Vertrags nicht vorkommt."
                    )
                    % (rec.name or rec.netbox_display or rec.id, rec.ci_class_id.name)
                )

    def _sync_contract_service_ids(self):
        """Kopiert gebuchte Leistungen aus der Vertrags-Leistungsmatrix ins CI (Kap. 11.3)."""
        for rec in self:
            if not rec.contract_id:
                rec.contract_service_ids = False
                continue
            if not rec.ci_class_id:
                rec.contract_service_ids = False
                continue
            line = rec.contract_id.ci_class_matrix_line_ids.filtered(
                lambda l: l.ci_class_id == rec.ci_class_id
            )[:1]
            services = line.with_context(active_test=False).service_ids if line else self.env["nt_serviceman.service"]
            rec.contract_service_ids = services

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        to_sync = records.filtered(lambda r: r.contract_id)
        if to_sync:
            to_sync._sync_contract_service_ids()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "contract_id" in vals:
            self._sync_contract_service_ids()
        return res

    def _netbox_device_exists(self, netbox_id):
        """Prüft, ob ein Device mit der NetBox-ID in NetBox existiert."""
        if not netbox_id or not (netbox_id := str(netbox_id).strip()):
            return True  # Leer = keine Prüfung
        base_url, token = self.env["nt_serviceman.config"]._get_netbox_params()
        if not base_url:
            return True  # Keine Config = Prüfung überspringen
        url = f"{base_url}/api/dcim/devices/{netbox_id}/"
        headers = {}
        if token:
            headers["Authorization"] = f"Token {token}"
        try:
            r = requests.get(url, headers=headers, timeout=15, verify=False)
            return r.status_code == 200
        except requests.RequestException:
            return False

    @api.constrains("netbox_id")
    def _check_netbox_id_exists(self):
        """NetBox-ID darf nur gespeichert werden, wenn das Gerät in NetBox existiert."""
        for rec in self:
            if not rec.netbox_id or not str(rec.netbox_id).strip():
                continue
            if not rec._netbox_device_exists(rec.netbox_id):
                raise ValidationError(
                    _(
                        "Die NetBox-ID '%s' existiert nicht in NetBox. "
                        "Das CI kann nicht gespeichert werden. "
                        "Bitte prüfen Sie die ID oder entfernen Sie sie."
                    )
                    % rec.netbox_id
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

    def action_open_form(self):
        """Öffnet das CI im Formular."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "nt_serviceman.configuration_item",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_unassign_contract(self):
        """Entfernt das CI aus dem Vertrag (setzt contract_id zurück)."""
        self.write({"contract_id": False})

    def action_fetch_from_netbox(self):
        """Ruft das Gerät per REST aus NetBox ab und speichert die Rohdaten."""
        self.ensure_one()
        base_url, token = self.env["nt_serviceman.config"].sudo()._get_netbox_params()
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
        if token:
            headers["Authorization"] = f"Token {token}"

        try:
            r = requests.get(url, headers=headers, timeout=15, verify=False)
            r.raise_for_status()
            data = r.json()

            # Immer aktualisieren bei manuellem Klick – Änderungen an verknüpften
            # Objekten (z.B. device_type.description) ändern device.last_updated nicht.
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

    @api.model
    def _run_sync_all_from_netbox(self, force_full=False):
        """Kernlogik Sync aller CI (Kap. 9.4/9.5). Returns dict or raises.
        Für Button und Cron; beide rufen diese Methode auf."""
        base_url, token = self.env["nt_serviceman.config"].sudo()._get_netbox_params()

        if not base_url:
            raise UserError(_("Keine NetBox-URL konfiguriert."))

        headers = {}
        if token:
            headers["Authorization"] = f"Token {token}"

        icp = self.env["ir.config_parameter"].sudo()
        last_sync_str = icp.get_param(NETBOX_LAST_SYNC_ALL_KEY, "").strip() or None

        do_full_sync = force_full or not last_sync_str
        url = f"{base_url}/api/dcim/devices/"
        if not do_full_sync and last_sync_str:
            netbox_ts = last_sync_str.replace(" ", "T") + "Z"
            url = f"{url}?last_updated__gte={netbox_ts}"

        created = updated = archived = 0
        netbox_ids_seen = set()

        while url:
            r = requests.get(url, headers=headers, timeout=30, verify=False)
            r.raise_for_status()
            data = r.json()

            for item in data.get("results", []):
                nb_id = item.get("id")
                if nb_id is None:
                    continue
                nb_id_str = str(nb_id)
                netbox_ids_seen.add(nb_id_str)
                nb_last_updated = self._parse_netbox_datetime(item.get("last_updated"))

                existing = self.sudo().with_context(active_test=False).search(
                    [("netbox_id", "=", nb_id_str)], limit=1
                )
                if existing:
                    do_update = False
                    if not existing.netbox_last_updated:
                        do_update = True
                    elif nb_last_updated:
                        nb_dt = fields.Datetime.from_string(nb_last_updated)
                        local_dt = fields.Datetime.from_string(
                            existing.netbox_last_updated
                        )
                        if nb_dt > local_dt:
                            do_update = True

                    if do_update:
                        existing._extract_netbox_fields(item)
                        vals = {
                            "netbox_last_sync": fields.Datetime.now(),
                            "netbox_sync_state": "ok",
                            "netbox_sync_error": False,
                        }
                        if not existing.active:
                            vals["active"] = True
                        existing.sudo().write(vals)
                        updated += 1
                else:
                    new_ci = self.sudo().create({"netbox_id": nb_id_str})
                    new_ci._extract_netbox_fields(item)
                    new_ci.sudo().write({
                        "netbox_last_sync": fields.Datetime.now(),
                        "netbox_sync_state": "ok",
                        "netbox_sync_error": False,
                    })
                    created += 1

            url = data.get("next")
            if url and not url.startswith("http"):
                url = f"{base_url}{url}" if url.startswith("/") else None

        if do_full_sync and netbox_ids_seen:
            obsolete = self.sudo().with_context(active_test=False).search([
                ("netbox_id", "not in", list(netbox_ids_seen)),
                ("active", "=", True),
            ])
            if obsolete:
                obsolete.sudo().write({"active": False})
                archived = len(obsolete)

        icp.set_param(NETBOX_LAST_SYNC_ALL_KEY, fields.Datetime.now())
        active_count = self.sudo().search_count([("active", "=", True)])

        return {
            "created": created,
            "updated": updated,
            "archived": archived,
            "active_count": active_count,
        }

    @api.model
    def action_sync_all_from_netbox(self):
        """Holt alle Devices von NetBox (Kap. 9.4). Button: ruft _run_sync_all_from_netbox, zeigt Notification."""
        try:
            result = self.with_context(
                force_full_sync=self.env.context.get("force_full_sync", False)
            )._run_sync_all_from_netbox(
                force_full=self.env.context.get("force_full_sync", False)
            )
        except (UserError, requests.RequestException) as e:
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
