# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Wizard zum Zuordnen von CI zu einem Vertrag
# -----------------------------------------------------------------------------

from odoo import _, api, fields, models


class ContractConfigurationItemAssign(models.TransientModel):
    """Wizard: CI einem Vertrag zuordnen (nur unzugeordnete CI)."""

    _name = "nt_serviceman.contract_configuration_item_assign"
    _description = "CI zu Vertrag zuordnen"

    contract_id = fields.Many2one(
        "contract.recurrent",
        string="Vertrag",
        required=True,
        readonly=True,
    )
    configuration_item_ids = fields.Many2many(
        "nt_serviceman.configuration_item",
        "contract_ci_assign_rel",
        "wizard_id",
        "configuration_item_id",
        string="Configuration Items",
        domain="[('contract_id', '=', False)]",
        help="Nur unzugeordnete CI werden angezeigt.",
    )

    @api.model
    def default_get(self, fields_list):
        """Setzt contract_id aus dem Context (active_id)."""
        res = super().default_get(fields_list)
        if "contract_id" in fields_list and self.env.context.get("active_model") == "contract.recurrent":
            contract_id = self.env.context.get("active_id")
            if contract_id:
                res["contract_id"] = contract_id
        return res

    def action_assign(self):
        """Ordnet die ausgewählten CI dem Vertrag zu."""
        self.ensure_one()
        if not self.configuration_item_ids:
            return
        self.configuration_item_ids.write({"contract_id": self.contract_id.id})
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Zuordnung gespeichert"),
                "message": _("%s CI dem Vertrag zugeordnet.") % len(self.configuration_item_ids),
                "type": "success",
                "sticky": False,
            },
        }
