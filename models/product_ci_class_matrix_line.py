# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Produkt-Matrix-Zeile – CI-Klasse mit Menge und buchbaren Leistungen
# (Kap. 8.10 Pflichtenheft)
# -----------------------------------------------------------------------------

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductCIClassMatrixLine(models.Model):
    """Zeile der Leistungsmatrix am Produkt: CI-Klasse, Menge, buchbare Leistungen."""

    _name = "nt_serviceman.product_ci_class_matrix_line"
    _description = "Produkt-Matrix-Zeile (CI-Klasse × Leistungen)"
    _order = "ci_class_id"

    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Produkt",
        required=True,
        ondelete="cascade",
    )
    ci_class_id = fields.Many2one(
        "nt_serviceman.ci_class",
        string="CI-Klasse",
        required=True,
        ondelete="cascade",
    )
    quantity = fields.Integer(
        string="Menge",
        default=0,
        help="Standardmenge pro CI-Klasse.",
    )
    service_ids = fields.Many2many(
        "nt_serviceman.service",
        "nt_serviceman_product_matrix_service_rel",
        "matrix_line_id",
        "service_id",
        string="Buchbare Leistungen",
        help="Leistungen, die für diese Klasse gebucht werden können. "
             "Nur verfügbare Leistungen (laut CI-Klasse) – wird beim Speichern geprüft.",
    )
    available_service_ids = fields.Many2many(
        related="ci_class_id.service_ids",
        readonly=True,
        string="Verfügbare Leistungen",
    )
    has_archived_services = fields.Boolean(
        compute="_compute_has_archived_services",
        string="Enthält archivierte",
    )
    archived_service_names = fields.Char(
        compute="_compute_has_archived_services",
        string="Archivierte Leistungen",
    )

    @api.depends("service_ids", "service_ids.active")
    def _compute_has_archived_services(self):
        for line in self:
            archived = line.service_ids.filtered(lambda s: not s.active)
            line.has_archived_services = bool(archived)
            line.archived_service_names = ", ".join(archived.mapped("name")) if archived else ""

    _sql_constraints = [
        (
            "product_ci_class_unique",
            "UNIQUE(product_tmpl_id, ci_class_id)",
            "Pro Produkt darf jede CI-Klasse nur einmal vorkommen.",
        ),
    ]

    @api.onchange("ci_class_id")
    def _onchange_ci_class_clear_invalid_services(self):
        """Entfernt Leistungen, die für die neue CI-Klasse nicht verfügbar sind."""
        if self.ci_class_id and self.service_ids:
            available = self.ci_class_id.service_ids
            invalid = self.service_ids - available
            if invalid:
                self.service_ids = self.service_ids - invalid

    def action_open_form(self):
        """Öffnet die Matrix-Zeile im Formular zur Bearbeitung."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "nt_serviceman.product_ci_class_matrix_line",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    @api.constrains("service_ids", "ci_class_id")
    def _check_services_available_for_ci_class(self):
        for line in self:
            if not line.ci_class_id:
                continue
            available = line.ci_class_id.service_ids
            invalid = line.service_ids - available
            if invalid:
                raise ValidationError(
                    _(
                        "Die Leistung „%s“ ist für die CI-Klasse „%s“ nicht verfügbar."
                        " Verfügbarkeit wird in der CI-Klasse konfiguriert."
                    )
                    % (invalid[:1].name, line.ci_class_id.name)
                )
