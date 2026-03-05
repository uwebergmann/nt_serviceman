# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Wizard zum Zuordnen von CI zu einem Vertrag
# -----------------------------------------------------------------------------

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ContractConfigurationItemAssign(models.TransientModel):
    """Wizard: CI einem Vertrag zuordnen (nur unzugeordnete CI mit passender CI-Klasse)."""

    _name = "nt_serviceman.contract_configuration_item_assign"
    _description = "CI zu Vertrag zuordnen"

    contract_id = fields.Many2one(
        "contract.recurrent",
        string="Vertrag",
        required=True,
        readonly=True,
    )
    allowed_ci_class_ids = fields.Many2many(
        "nt_serviceman.ci_class",
        compute="_compute_allowed_ci_class_ids",
        string="Erlaubte CI-Klassen",
        help="CI-Klassen aus der Leistungsmatrix des Vertrags.",
    )
    configuration_item_ids = fields.Many2many(
        "nt_serviceman.configuration_item",
        "contract_ci_assign_rel",
        "wizard_id",
        "configuration_item_id",
        string="Configuration Items",
        domain="[('contract_id', '=', False)]",
        help="Nur unzugeordnete CI mit einer in der Leistungsmatrix vorkommenden CI-Klasse.",
    )

    @api.depends("contract_id", "contract_id.ci_class_matrix_line_ids", "contract_id.ci_class_matrix_line_ids.ci_class_id")
    def _compute_allowed_ci_class_ids(self):
        for wizard in self:
            if wizard.contract_id:
                wizard.allowed_ci_class_ids = wizard.contract_id.ci_class_matrix_line_ids.mapped("ci_class_id")
            else:
                wizard.allowed_ci_class_ids = False

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
        allowed = self.contract_id.ci_class_matrix_line_ids.mapped("ci_class_id")
        invalid = self.configuration_item_ids.filtered(
            lambda c: not c.ci_class_id or c.ci_class_id not in allowed
        )
        if invalid:
            names = ", ".join(invalid[:3].mapped("name"))
            if len(invalid) > 3:
                names += _(" … und weitere")
            raise ValidationError(
                _(
                    "Folgende CI können nicht zugeordnet werden, "
                    "da ihre CI-Klasse nicht in der Leistungsmatrix des Vertrags vorkommt: %s"
                )
                % names
            )
        self.configuration_item_ids.write({"contract_id": self.contract_id.id})
        return {"type": "ir.actions.act_window_close"}
