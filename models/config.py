# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Konfigurationsmodell für NT:ServiceMan (NetBox)
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

from odoo import fields, models


class NTServiceManConfig(models.Model):
    """Globale Konfiguration für NT:ServiceMan (NetBox-Anbindung)."""

    _name = "nt_serviceman.config"
    _description = "NT:ServiceMan Konfiguration"

    netbox_base_url = fields.Char(
        string="NetBox-URL",
        help="Basis-URL der NetBox-Instanz (z.B. https://netbox.example.com)",
    )
