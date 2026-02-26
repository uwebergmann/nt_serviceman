# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Manifest für das NT:ServiceMan-Modul (CI-Abbildung, NetBox)
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

{
    "name": "NT:ServiceMan",
    "version": "0.9.6",
    "author": "NETHINKS GmbH",
    "summary": "Abbildung von Configuration Items (CI) aus NetBox, Vertragszuordnung",
    "category": "Services",
    "license": "Other proprietary",
    "depends": ["base"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menu_views.xml",
        "data/ci_class_data.xml",
        "views/config_views.xml",
        "views/ci_class_views.xml",
        "views/netbox_device_role_views.xml",
        "views/configuration_item_views.xml",
        "wizard/ci_class_device_role_assign_views.xml",
    ],
    "installable": True,
    "application": True,
}
