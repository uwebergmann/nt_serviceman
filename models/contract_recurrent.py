# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Erweiterung contract.recurrent – CI-Zuordnung (CMDB-Tab)
# -----------------------------------------------------------------------------

from odoo import api, fields, models


class ContractRecurrent(models.Model):
    _inherit = "contract.recurrent"

    ci_class_matrix_line_ids = fields.One2many(
        "nt_serviceman.contract_ci_class_matrix_line",
        "contract_id",
        string="Leistungsmatrix",
        help="CI-Klassen mit Menge und buchbaren Leistungen (Kap. 11.2).",
    )
    configuration_item_ids = fields.One2many(
        "nt_serviceman.configuration_item",
        "contract_id",
        string="Configuration Items",
    )

    @api.model_create_multi
    def create(self, vals_list):
        contracts = super().create(vals_list)
        for contract in contracts:
            contract.action_init_ci_class_matrix_lines()
        return contracts

    def action_init_ci_class_matrix_lines(self):
        """Erstellt fehlende Matrix-Zeilen für alle aktiven CI-Klassen."""
        self.ensure_one()
        existing = self.ci_class_matrix_line_ids.mapped("ci_class_id")
        to_create = self.env["nt_serviceman.ci_class"].search([
            ("active", "=", True),
            ("id", "not in", existing.ids),
        ])
        for ci_class in to_create:
            self.env["nt_serviceman.contract_ci_class_matrix_line"].create({
                "contract_id": self.id,
                "ci_class_id": ci_class.id,
            })

    def action_assign_configuration_items(self):
        """Öffnet den Wizard zum Zuordnen von CI (nur unzugeordnete)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "CI zuordnen",
            "res_model": "nt_serviceman.contract_configuration_item_assign",
            "view_mode": "form",
            "target": "new",
            "context": {"active_model": "contract.recurrent", "active_id": self.id},
        }
