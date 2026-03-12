# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Leistung (Service) – Kap. 8.7 Pflichtenheft
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

import inspect

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Service(models.Model):
    """Leistung – Dienstleistung, die NETHINKS grundsätzlich erbringen kann."""

    _name = "nt_serviceman.service"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Leistung (Service)"
    _order = "sequence, code"

    code = fields.Char(
        string="Kurzcode",
        required=True,
        help="Technischer Kurzcode (z.B. Dokumentation, Update-Service)",
    )
    name = fields.Char(
        string="Bezeichnung",
        required=True,
    )
    description = fields.Text(
        string="Beschreibung",
        help="Ausführliche Beschreibung der Leistung.",
    )
    active = fields.Boolean(
        default=True,
        string="Aktiv",
    )
    sequence = fields.Integer(
        string="Reihenfolge",
        default=10,
        help="Sortierreihenfolge für die Anzeige.",
    )
    color = fields.Integer(
        string="Farbe",
        compute="_compute_color",
        help="Grau (0) wenn archiviert, für Tag-Darstellung in Matrix.",
    )
    ci_class_ids = fields.Many2many(
        "nt_serviceman.ci_class",
        "nt_serviceman_ci_class_service_rel",
        "service_id",
        "ci_class_id",
        string="Verfügbar für CI-Klassen",
        help="Geräteklassen, für die diese Leistung möglich ist (Kap. 8.8).",
        domain=[("active", "=", True)],
    )
    required_device_field_ids = fields.One2many(
        "nt_serviceman.service.required_device_field",
        "service_id",
        string="NetBox-Device-Felder",
        help="Feldliste aus NetBox. Häkchen = für diese Leistung erforderlich (Kap. 8.11.1).",
    )
    required_vm_field_ids = fields.One2many(
        "nt_serviceman.service.required_vm_field",
        "service_id",
        string="NetBox-VM-Felder",
        help="Feldliste für virtuelle Maschinen. Häkchen = für diese Leistung bei VMs erforderlich (Kap. 8.11.1c).",
    )

    def _ensure_required_device_field_lines(self):
        """Synchronisiert Zeilen mit der gecachten Feldliste (beim Create oder Config-Refresh)."""
        config = self.env["nt_serviceman.config"]
        fields_list = config._get_netbox_device_field_names()
        if not fields_list:
            return
        for service in self:
            existing = {line.field_path for line in service.required_device_field_ids}
            for path in fields_list:
                if path not in existing:
                    self.env["nt_serviceman.service.required_device_field"].create({
                        "service_id": service.id,
                        "field_path": path,
                        "is_required": False,
                    })
            # Entfernte Felder bereinigen
            to_remove = service.required_device_field_ids.filtered(
                lambda l: l.field_path not in fields_list
            )
            to_remove.unlink()

    def _ensure_required_vm_field_lines(self):
        """Synchronisiert VM-Feldzeilen mit der gecachten Feldliste (beim Create oder Config-Refresh)."""
        config = self.env["nt_serviceman.config"]
        fields_list = config._get_netbox_vm_field_names()
        if not fields_list:
            return
        for service in self:
            existing = {line.field_path for line in service.required_vm_field_ids}
            for path in fields_list:
                if path not in existing:
                    self.env["nt_serviceman.service.required_vm_field"].create({
                        "service_id": service.id,
                        "field_path": path,
                        "is_required": False,
                    })
            to_remove = service.required_vm_field_ids.filtered(
                lambda l: l.field_path not in fields_list
            )
            to_remove.unlink()

    @api.depends("active")
    def _compute_color(self):
        """Archivierte Leistungen: grau (0). Aktive: Standard (1)."""
        for rec in self:
            rec.color = 0 if not rec.active else 1

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._ensure_required_device_field_lines()
        records._ensure_required_vm_field_lines()
        return records

    def unlink(self):
        """Leistungen werden nicht gelöscht, nur archiviert (Kap. 8.7 Soft Delete).
        Ausnahme: Modul-Update – Odoo muss verwaiste Datensätze bereinigen können."""
        for frame in inspect.stack()[1:]:
            if frame.function == "_process_end_unlink_record":
                return super().unlink()
        raise UserError(
            _(
                "Leistungen werden nicht gelöscht. "
                "Bitte archivieren Sie die Leistung über 'Archivieren'."
            )
        )

    def action_open_form(self):
        """Öffnet die Leistung im Formular."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "nt_serviceman.service",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }


class ServiceRequiredDeviceField(models.Model):
    """Eine Zeile: NetBox-Device-Feld + Häkchen ob erforderlich (Kap. 8.11.1)."""

    _name = "nt_serviceman.service.required_device_field"
    _description = "Erforderliches NetBox-Device-Feld pro Leistung"

    service_id = fields.Many2one(
        "nt_serviceman.service",
        string="Leistung",
        required=True,
        ondelete="cascade",
    )
    field_path = fields.Char(
        string="Feld",
        required=True,
        help="Pfad zum Feld (z.B. custom_fields.license).",
    )
    is_required = fields.Boolean(
        string="Erforderlich",
        default=False,
        help="Wenn gesetzt: Dieses Feld muss am CI ausgefüllt sein, "
        "damit die Leistung erbracht werden kann.",
    )
    example_value = fields.Char(
        string="Beispielwert",
        compute="_compute_example_value",
        help="Beispielwert aus NetBox (zur Orientierung).",
    )

    @api.depends("field_path")
    def _compute_example_value(self):
        config = self.env["nt_serviceman.config"]
        sample = config._get_netbox_device_sample()
        for rec in self:
            val = config._get_value_by_path(sample, rec.field_path) if sample else None
            rec.example_value = config._format_field_value(val) or ""

    def write(self, vals):
        res = super().write(vals)
        if "is_required" in vals or "field_path" in vals:
            services = self.mapped("service_id")
            if services:
                cis = self.env["nt_serviceman.configuration_item"].search(
                    [("contract_service_ids", "in", services.ids)]
                )
                cis.invalidate_recordset(["service_fields_status", "service_fields_status_icon"])
        return res


class ServiceRequiredVmField(models.Model):
    """Eine Zeile: NetBox-VM-Feld + Häkchen ob erforderlich (Kap. 8.11.1c)."""

    _name = "nt_serviceman.service.required_vm_field"
    _description = "Erforderliches NetBox-VM-Feld pro Leistung"

    service_id = fields.Many2one(
        "nt_serviceman.service",
        string="Leistung",
        required=True,
        ondelete="cascade",
    )
    field_path = fields.Char(
        string="Feld",
        required=True,
        help="Pfad zum Feld (z.B. platform.name, cluster.name).",
    )
    is_required = fields.Boolean(
        string="Erforderlich",
        default=False,
        help="Wenn gesetzt: Dieses Feld muss am VM-CI ausgefüllt sein, "
        "damit die Leistung erbracht werden kann.",
    )
    example_value = fields.Char(
        string="Beispielwert",
        compute="_compute_example_value",
        help="Beispielwert aus NetBox (zur Orientierung).",
    )

    @api.depends("field_path")
    def _compute_example_value(self):
        config = self.env["nt_serviceman.config"]
        sample = config._get_netbox_vm_sample()
        for rec in self:
            val = config._get_value_by_path(sample, rec.field_path) if sample else None
            rec.example_value = config._format_field_value(val) or ""

    def write(self, vals):
        res = super().write(vals)
        if "is_required" in vals or "field_path" in vals:
            services = self.mapped("service_id")
            if services:
                cis = self.env["nt_serviceman.configuration_item"].search(
                    [("contract_service_ids", "in", services.ids)]
                )
                cis.invalidate_recordset(["service_fields_status", "service_fields_status_icon"])
        return res
