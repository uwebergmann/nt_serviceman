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
