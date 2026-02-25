# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Manifest für das NT:ServiceMan-Modul (CI-Abbildung, NetBox)
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

{
    "name": "NT:ServiceMan",
    "version": "0.9",
    "author": "NETHINKS GmbH",
    "summary": "Abbildung von Configuration Items (CI) aus NetBox, Vertragszuordnung",
    "category": "Hidden",
    "license": "Other proprietary",
    "depends": ["base"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/config_views.xml",
        "views/configuration_item_views.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "application": True,
}
