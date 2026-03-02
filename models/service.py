# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Leistung (Service) – Kap. 8.7 Pflichtenheft
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

from odoo import fields, models


class Service(models.Model):
    """Leistung – Dienstleistung, die NETHINKS grundsätzlich erbringen kann."""

    _name = "nt_serviceman.service"
    _description = "Leistung (Service)"
    _order = "sequence, code"

    code = fields.Char(
        string="Kurzcode",
        required=True,
        help="Technischer Kurzcode (z.B. Dokumentation, Update-Service)",
    )
    name = fields.Char(
        string="Bezeichnung",
        required=True,
    )
    description = fields.Text(
        string="Beschreibung",
        help="Ausführliche Beschreibung der Leistung.",
    )
    active = fields.Boolean(
        default=True,
        string="Aktiv",
    )
    sequence = fields.Integer(
        string="Reihenfolge",
        default=10,
        help="Sortierreihenfolge für die Anzeige.",
    )
