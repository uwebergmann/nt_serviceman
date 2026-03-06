# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Manifest für das NT:ServiceMan-Modul (CI-Abbildung, NetBox)
# Letzte Änderung: $LastChanged$
# Commit: $CommitId$
# Autor: $Author$
# -----------------------------------------------------------------------------

{
    "name": "NT:ServiceMan",
    "version": "1.0.1",
    "author": "NETHINKS GmbH",
    "summary": "Abbildung von Configuration Items (CI) aus NetBox, Vertragszuordnung",
    "category": "Services",
    "license": "Other proprietary",
    "depends": ["base", "mail", "intero_net"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menu_views.xml",
        "data/ci_class_data.xml",
        "data/service_data.xml",
        "data/ir_actions_server_data.xml",
        "views/config_views.xml",
        "views/service_views.xml",
        "views/ci_class_views.xml",
        "views/netbox_device_role_views.xml",
        "views/configuration_item_views.xml",
        "views/contract_recurrent_views.xml",
        "views/product_template_views.xml",
        "wizard/ci_class_device_role_assign_views.xml",
        "wizard/contract_configuration_item_assign_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "nt_serviceman/static/src/css/ci_class_services.css",
        ],
    },
    "installable": True,
    "application": True,
}
