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
    service_ids = fields.Many2many(
        "nt_serviceman.service",
        "nt_serviceman_contract_matrix_service_rel",
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

    _sql_constraints = [
        (
            "contract_ci_class_unique",
            "UNIQUE(contract_id, ci_class_id)",
            "Pro Vertrag darf jede CI-Klasse nur einmal vorkommen.",
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
