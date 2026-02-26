# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: CI-Klasse – fachliche Geräteklasse (FW, SW, RTR, AP)
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

from odoo import fields, models


class CIClass(models.Model):
    """CI-Klasse – fachliche Steuergröße für Abrechnung, SLA, Plan/Ist."""

    _name = "nt_serviceman.ci_class"
    _description = "CI-Klasse"
    _order = "code"

    code = fields.Char(
        string="Kurzcode",
        required=True,
        help="z.B. FW, SW, RTR, AP",
    )
    name = fields.Char(
        string="Bezeichnung",
        required=True,
    )
    description = fields.Text(string="Beschreibung")
    active = fields.Boolean(default=True, string="Aktiv")
    device_role_ids = fields.One2many(
        "nt_serviceman.netbox_device_role",
        "ci_class_id",
        string="Device Roles",
        help="NetBox Device Roles, die dieser CI-Klasse zugeordnet sind.",
    )

    def action_open_form(self):
        """Öffnet die CI-Klasse im Formular."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "nt_serviceman.ci_class",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_assign_device_roles(self):
        """Öffnet den Wizard zum Zuordnen von Device Roles (nur unverknüpfte)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Device Roles zuordnen",
            "res_model": "nt_serviceman.ci_class_device_role_assign",
            "view_mode": "form",
            "target": "new",
            "context": {"default_ci_class_id": self.id},
        }
