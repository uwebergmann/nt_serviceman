# NT:ServiceMan

<!--
© NETHINKS GmbH – Alle Rechte vorbehalten
Beschreibung: NT:ServiceMan – CI-Abbildung in Odoo mit NetBox-REST-Anbindung
-->

NT:ServiceMan ist ein **Odoo 16 Modul** von NETHINKS GmbH. Es bildet **Configuration Items (CI)** aus **NetBox** in Odoo ab und verknüpft sie mit wiederkehrenden Verträgen (z. B. NT/Care).

**Kernidee:** NetBox ist die **technische Source of Truth**; Odoo übernimmt eine **lesende Spiegelung** und reichert sie um servicebezogene Daten sowie Vertragszuordnung an.

## Wichtige Begriffe

| Begriff | Bedeutung |
|--------|-----------|
| **CI** | Configuration Item – ein reales Gerät aus NetBox |
| **CI-Klasse** | Fachliche Geräteklasse (Firewall, Switch, Router, Access Point); unabhängig von NetBox |
| **Device Role** | Technische Rolle aus NetBox; wird per Mapping einer CI-Klasse zugeordnet |
| **Leistungsmatrix** | Definiert pro CI-Klasse: Menge + gebuchte Leistungen (Services) |
| **Planpositionen** | Planmenge je Geräteklasse im Vertrag (Vertriebsplanung, keine echten Objekte) |
| **Plan/Ist** | Vergleich: geplante vs. tatsächlich zugeordnete CI je Klasse |

## Architektur-Entscheidungen

- **Keine Platzhalter-CI** – CI entstehen nur nach Anlage in NetBox
- **Kein automatischer Sync** – NetBox-Abruf nur manuell per Button
- **CI-Klassen ≠ Device Roles** – fachliche Ebene (Odoo) und technische Ebene (NetBox) getrennt, Mapping konfigurierbar
- **Leistungen** – soft-delete (archivieren statt löschen); bleiben in bestehenden Verträgen erhalten

## Abhängigkeiten

- **Odoo:** 16
- **Python:** `requests` für NetBox REST-API
- **intero_net** – enthält `contract.recurrent` (wiederkehrende Verträge)
- **mail** – Chatter für CI, Service, CI-Klasse
- **base**

Installation und Deployment: siehe [DEPLOY.md](DEPLOY.md).

## Modulstruktur

```
nt_serviceman/
├── models/
│   ├── config.py              # NetBox-URL, API-Token (ir.config_parameter)
│   ├── ci_class.py            # CI-Klassen
│   ├── netbox_device_role.py  # Spiegel der NetBox Device Roles
│   ├── configuration_item.py  # CI (aus NetBox, Vertragszuordnung)
│   ├── service.py             # Leistungen
│   ├── contract_recurrent.py  # Erweiterung Vertrag (intero_net)
│   ├── contract_ci_class_matrix_line.py  # Leistungsmatrix am Vertrag
│   ├── product_template.py    # Erweiterung Produkt
│   ├── product_ci_class_matrix_line.py   # Leistungsmatrix am Produkt
│   └── product_product.py     # _prepare_contract_values
├── wizard/
│   ├── contract_configuration_item_assign.py  # CI zuordnen
│   └── ci_class_device_role_assign.py        # Device Role ↔ CI-Klasse
├── views/
├── security/
├── data/
└── docs/
    └── Pflichtenheft.md       # Quelle der Wahrheit
```

## Datenfluss (Kurz)

1. **NetBox** → Device mit Device Role
2. **Odoo CI** – manueller Abruf (Button „Hole von NetBox“); netbox_role_id → Mapping → ci_class_id
3. **Vertrag** – Leistungsmatrix (CI-Klasse × Menge × Leistungen); CI werden zugeordnet
4. **CI** – contract_service_ids = Kopie der gebuchten Leistungen aus Vertragsmatrix

## Rollen

- **NT:ServiceMan Admin** – Vollzugriff inkl. Konfiguration
- **NT:ServiceMan Nutzer** – operative Nutzung, kein Konfigurations-Menü
- **andere** – kein Zugriff

---

*Stand: v1.0*
