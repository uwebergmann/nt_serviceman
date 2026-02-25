# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: CI-Klasse – fachliche Geräteklasse (FW, SW, RTR, AP)
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

from odoo import fields, models


class CIClass(models.Model):
    """CI-Klasse – fachliche Steuergröße für Abrechnung, SLA, Plan/Ist."""

    _name = "nt_serviceman.ci_class"
    _description = "CI-Klasse"
    _order = "code"

    code = fields.Char(
        string="Kurzcode",
        required=True,
        help="z.B. FW, SW, RTR, AP",
    )
    name = fields.Char(
        string="Bezeichnung",
        required=True,
    )
    description = fields.Text(string="Beschreibung")
    active = fields.Boolean(default=True, string="Aktiv")
