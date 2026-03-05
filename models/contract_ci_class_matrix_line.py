# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Vertrags-Matrix-Zeile – CI-Klasse mit Menge und buchbaren Leistungen
# (Kap. 11.2 Pflichtenheft)
# -----------------------------------------------------------------------------

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ContractCIClassMatrixLine(models.Model):
    """Zeile der Leistungsmatrix am Vertrag: CI-Klasse, Menge, buchbare Leistungen."""

    _name = "nt_serviceman.contract_ci_class_matrix_line"
    _description = "Vertrags-Matrix-Zeile (CI-Klasse × Leistungen)"
    _order = "ci_class_id"

    contract_id = fields.Many2one(
        "contract.recurrent",
        string="Vertrag",
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
        help="Anzahl Geräte dieser Klasse im Vertrag.",
    )
    actual_quantity = fields.Integer(
        string="Ist-Menge",
        compute="_compute_actual_quantity",
        help="Anzahl CIs dieser Klasse im CMDB-Tab des Vertrags (wird automatisch berechnet).",
    )
    quantity_deviation = fields.Integer(
        string="Abweichung",
        compute="_compute_quantity_deviation",
        help="Ist-Menge minus Plan-Menge: positiv = mehr als geplant, negativ = weniger als geplant.",
    )

    @api.depends("quantity", "actual_quantity")
    def _compute_quantity_deviation(self):
        for line in self:
            line.quantity_deviation = line.actual_quantity - line.quantity
    service_ids = fields.Many2many(
        "nt_serviceman.service",
        "nt_serviceman_contract_matrix_service_rel",
        "matrix_line_id",
        "service_id",
        string="Buchbare Leistungen",
        context={"active_test": False},
        help="Leistungen, die für diese Klasse gebucht werden können. "
             "Archivierte bleiben sichtbar, sind aber nicht mehr neu buchbar.",
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

    @api.depends(
        "contract_id",
        "contract_id.configuration_item_ids",
        "contract_id.configuration_item_ids.ci_class_id",
        "ci_class_id",
    )
    def _compute_actual_quantity(self):
        """Ist-Menge = Anzahl CIs dieser CI-Klasse im CMDB-Tab des Vertrags."""
        for line in self:
            if not line.contract_id or not line.ci_class_id:
                line.actual_quantity = 0
                continue
            cis = line.contract_id.configuration_item_ids.filtered(
                lambda c: c.ci_class_id == line.ci_class_id
            )
            line.actual_quantity = len(cis)

    @api.depends("service_ids", "service_ids.active")
    def _compute_has_archived_services(self):
        for line in self:
            archived = line.service_ids.filtered(lambda s: not s.active)
            line.has_archived_services = bool(archived)
            line.archived_service_names = ", ".join(archived.mapped("name")) if archived else ""

    _sql_constraints = [
        (
            "contract_ci_class_unique",
            "UNIQUE(contract_id, ci_class_id)",
            "Pro Vertrag darf jede CI-Klasse nur einmal vorkommen.",
        ),
    ]

    @api.onchange("ci_class_id")
    def _onchange_ci_class_clear_invalid_services(self):
        """Entfernt nur aktive Leistungen, die für die neue CI-Klasse nicht verfügbar sind.
        Archivierte Leistungen bleiben erhalten."""
        if self.ci_class_id and self.service_ids:
            available = self.ci_class_id.service_ids
            active_services = self.service_ids.filtered(lambda s: s.active)
            invalid = active_services - available
            if invalid:
                self.service_ids = self.service_ids - invalid

    @api.constrains("service_ids", "ci_class_id")
    def _check_services_available_for_ci_class(self):
        """Prüft, dass neue (aktive) Leistungen verfügbar sind. Archivierte bleiben erlaubt."""
        for line in self:
            if not line.ci_class_id:
                continue
            available = line.ci_class_id.service_ids
            # Nur aktive Leistungen prüfen; archivierte (bereits im Vertrag) bleiben erlaubt
            active_in_matrix = line.service_ids.filtered(lambda s: s.active)
            invalid = active_in_matrix - available
            if invalid:
                raise ValidationError(
                    _(
                        "Die Leistung „%s“ ist für die CI-Klasse „%s“ nicht verfügbar."
                        " Verfügbarkeit wird in der CI-Klasse konfiguriert."
                    )
                    % (invalid[:1].name, line.ci_class_id.name)
                )
