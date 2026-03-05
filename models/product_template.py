# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Erweiterung product.template – Leistungsmatrix (Kap. 8.10 Pflichtenheft)
# -----------------------------------------------------------------------------

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ci_class_matrix_line_ids = fields.One2many(
        "nt_serviceman.product_ci_class_matrix_line",
        "product_tmpl_id",
        string="Leistungsmatrix",
        copy=True,
        help="CI-Klassen mit Menge und buchbaren Leistungen für wiederkehrende Produkte (Kap. 8.10).",
    )
    ci_class_matrix_has_archived = fields.Boolean(
        compute="_compute_ci_class_matrix_archived_banner",
        string="Matrix enthält archivierte",
    )
    ci_class_matrix_archived_banner = fields.Html(
        compute="_compute_ci_class_matrix_archived_banner",
        string="Archivierte Leistungen Hinweis",
    )

    @api.depends("ci_class_matrix_line_ids.service_ids", "ci_class_matrix_line_ids.service_ids.active")
    def _compute_ci_class_matrix_archived_banner(self):
        for product in self:
            archived = product.ci_class_matrix_line_ids.mapped("service_ids").filtered(
                lambda s: not s.active
            )
            product.ci_class_matrix_has_archived = bool(archived)
            if archived:
                names = ", ".join(archived.mapped("name"))
                product.ci_class_matrix_archived_banner = (
                    f'<div class="alert alert-info mb-0" role="alert">'
                    f'<strong>Diese Matrix enthält archivierte Leistung(en):</strong> {names}. '
                    "Sie bleiben in der Matrix, werden aber nicht mehr in neue Verträge übernommen."
                    "</div>"
                )
            else:
                product.ci_class_matrix_archived_banner = False

    def action_init_ci_class_matrix_lines(self):
        """Erstellt fehlende Matrix-Zeilen für alle aktiven CI-Klassen."""
        self.ensure_one()
        existing = self.ci_class_matrix_line_ids.mapped("ci_class_id")
        to_create = self.env["nt_serviceman.ci_class"].search([
            ("active", "=", True),
            ("id", "not in", existing.ids),
        ])
        for ci_class in to_create:
            self.env["nt_serviceman.product_ci_class_matrix_line"].create({
                "product_tmpl_id": self.id,
                "ci_class_id": ci_class.id,
            })
