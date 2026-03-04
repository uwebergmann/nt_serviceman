# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Leistung (Service) – Kap. 8.7 Pflichtenheft
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

from odoo import _, fields, models
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
    ci_class_ids = fields.Many2many(
        "nt_serviceman.ci_class",
        "nt_serviceman_ci_class_service_rel",
        "service_id",
        "ci_class_id",
        string="Verfügbar für CI-Klassen",
        help="Geräteklassen, für die diese Leistung möglich ist (Kap. 8.8).",
        domain=[("active", "=", True)],
    )

    def unlink(self):
        """Leistungen werden nicht gelöscht, nur archiviert (Kap. 8.7 Soft Delete)."""
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
