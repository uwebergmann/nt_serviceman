# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Wizard zum Zuordnen von Device Roles zu einer CI-Klasse
# -----------------------------------------------------------------------------

from odoo import _, fields, models


class CIClassDeviceRoleAssign(models.TransientModel):
    """Wizard: Device Roles zu einer CI-Klasse zuordnen (nur unverknüpfte)."""

    _name = "nt_serviceman.ci_class_device_role_assign"
    _description = "Device Roles zu CI-Klasse zuordnen"

    ci_class_id = fields.Many2one(
        "nt_serviceman.ci_class",
        string="CI-Klasse",
        required=True,
        readonly=True,
    )
    device_role_ids = fields.Many2many(
        "nt_serviceman.netbox_device_role",
        "ci_class_assign_device_role_rel",
        "wizard_id",
        "device_role_id",
        string="Device Roles",
        domain="[('ci_class_id', '=', False), ('active', '=', True)]",
        help="Nur Device Roles ohne Zuordnung werden angezeigt.",
    )

    def action_assign(self):
        """Ordnet die ausgewählten Device Roles der CI-Klasse zu."""
        self.ensure_one()
        if not self.device_role_ids:
            return
        self.device_role_ids.write({"ci_class_id": self.ci_class_id.id})
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Zuordnung gespeichert"),
                "message": _("%s Device Role(s) zugeordnet.") % len(self.device_role_ids),
                "type": "success",
                "sticky": False,
            },
        }
