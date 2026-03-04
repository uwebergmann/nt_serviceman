# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Erweiterung product.product – Übertragung Leistungsmatrix in Vertrag
# (Kap. 11.4 Pflichtenheft)
# -----------------------------------------------------------------------------

from odoo import Command, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_contract_values(self, **kwargs):
        """Erweitert contract_values um ci_class_matrix_line_ids aus Produkt (Kap. 11.4)."""
        values_list = super()._prepare_contract_values(**kwargs)
        for i, vals in enumerate(values_list):
            product = self[i] if len(self) > 1 else self
            matrix_commands = product._prepare_contract_ci_class_matrix_values()
            if matrix_commands:
                vals["ci_class_matrix_line_ids"] = matrix_commands
        return values_list

    def _prepare_contract_ci_class_matrix_values(self):
        """
        Bereitet die Leistungsmatrix für den Vertrag vor.
        Nur aktive Leistungen werden übernommen (Kap. 8.7 Soft Delete).
        """
        self.ensure_one()
        if self.detailed_type != "recurrent":
            return []
        lines = self.product_tmpl_id.ci_class_matrix_line_ids
        if not lines:
            return []
        commands = []
        for line in lines:
            # Nur aktive Leistungen übernehmen
            active_services = line.service_ids.filtered(lambda s: s.active)
            commands.append(
                Command.create({
                    "ci_class_id": line.ci_class_id.id,
                    "quantity": line.quantity,
                    "service_ids": [(6, 0, active_services.ids)],
                })
            )
        return commands
