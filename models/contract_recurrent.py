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
    ci_class_matrix_has_archived = fields.Boolean(
        compute="_compute_ci_class_matrix_archived_banner",
        string="Matrix enthält archivierte",
    )
    vertragsabweichung = fields.Boolean(
        compute="_compute_vertragsabweichung",
        string="Vertragsabweichung",
        store=True,
        help="True, wenn in mindestens einer CI-Klasse-Zeile Plan- und Ist-Menge abweichen.",
    )

    @api.depends(
        "ci_class_matrix_line_ids.quantity",
        "ci_class_matrix_line_ids.actual_quantity",
        "configuration_item_ids",
        "configuration_item_ids.ci_class_id",
    )
    def _compute_vertragsabweichung(self):
        for contract in self:
            lines = contract.ci_class_matrix_line_ids
            contract.vertragsabweichung = any(l.quantity_deviation != 0 for l in lines)
    ci_class_matrix_archived_banner = fields.Html(
        compute="_compute_ci_class_matrix_archived_banner",
        string="Archivierte Leistungen Hinweis",
    )

    @api.depends("ci_class_matrix_line_ids.service_ids", "ci_class_matrix_line_ids.service_ids.active")
    def _compute_ci_class_matrix_archived_banner(self):
        for contract in self:
            archived = contract.ci_class_matrix_line_ids.mapped("service_ids").filtered(
                lambda s: not s.active
            )
            contract.ci_class_matrix_has_archived = bool(archived)
            if archived:
                names = ", ".join(archived.mapped("name"))
                contract.ci_class_matrix_archived_banner = (
                    f'<div class="alert alert-info mb-0" role="alert">'
                    f'<strong>Diese Matrix enthält archivierte Leistung(en):</strong> {names}. '
                    "Sie bleiben im Vertrag vereinbart, sind aber nicht mehr neu buchbar."
                    "</div>"
                )
            else:
                contract.ci_class_matrix_archived_banner = False

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
