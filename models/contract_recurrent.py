# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Erweiterung contract.recurrent – CI-Zuordnung (CMDB-Tab)
# -----------------------------------------------------------------------------

from odoo import fields, models


class ContractRecurrent(models.Model):
    _inherit = "contract.recurrent"

    configuration_item_ids = fields.One2many(
        "nt_serviceman.configuration_item",
        "contract_id",
        string="Configuration Items",
    )

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
