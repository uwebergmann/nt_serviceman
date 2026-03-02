# Rollback: Von Option 3 auf Option 2

Dieses Dokument beschreibt, wie man von **Option 3** (Config-Formular mit eingebetteter Device-Roles-Liste) auf **Option 2** (zwei Menüpunkte) zurückwechselt.

## Kontext

- **Option 3 (aktuell):** Button „Device Roles von NetBox abrufen“ im Config-Formular; Device-Roles-Liste als Tab im selben Formular.
- **Option 2 (Fallback):** „Device Roles“ als Liste; separater Menüpunkt „Device Roles von NetBox abrufen“, der den Abruf ohne Zeilenauswahl startet.

## Änderungen für Rollback

### 1. Config-Modell (`models/config.py`)

- **Entfernen:** Feld `device_role_ids` (Zeilen 38–43).

### 2. NetBox Device Role (`models/netbox_device_role.py`)

- **Entfernen:** Feld `config_id` (Zeilen 55–61).
- **Entfernen:** In `action_fetch_from_netbox`:
  - `"config_id": config.id` aus allen `vals` und `create()`-Aufrufen.
  - Den Block „Bestehende Device Roles ohne config_id …“ (Zeilen 170–173).

### 3. Config-View (`views/config_views.xml`)

- **Entfernen:** Den kompletten Abschnitt `<notebook>` mit der Device-Roles-Seite (das `<page string="Device Roles">` inkl. `device_role_ids`).

### 4. Option 2: Neuer Menüpunkt

In `views/menu_views.xml` oder in `views/netbox_device_role_views.xml` einen zweiten Menüpunkt ergänzen:

```xml
<menuitem id="menu_fetch_device_roles_from_netbox"
          name="Device Roles von NetBox abrufen"
          parent="menu_nt_serviceman_data"
          action="action_server_fetch_device_roles"
          sequence="14"
          groups="nt_serviceman.group_nt_serviceman_admin,nt_serviceman.group_nt_serviceman_user"/>
```

**Hinweis:** Die Server-Aktion `action_server_fetch_device_roles` ist in `data/ir_actions_server_data.xml` definiert und muss in der Modul-`data`-Liste vor den View-Dateien geladen werden (ist bereits der Fall).

### 5. Button im Config-Formular (optional)

- **Behalten:** Der Button „Device Roles von NetBox abrufen“ kann weiter im Config-Formular stehen; er funktioniert unabhängig von Option 2/3.
- **Oder entfernen:** Falls der Abruf ausschließlich über den neuen Menüpunkt erfolgen soll, den Button aus `config_views.xml` entfernen.

## Server-Aktion

Die Server-Aktion in `data/ir_actions_server_data.xml` bleibt unverändert. Sie ist für Option 2 und Option 3 nutzbar.

## Migration / Datenbank

- `config_id` hat `ondelete="set null"`; beim Entfernen des Feldes wird die Spalte in der Migration ignoriert bzw. zurückgebaut.
- Device Roles ohne `config_id` bleiben funktionsfähig; sie werden nur nicht mehr im Config-Formular angezeigt.

## Reihenfolge der Schritte

1. Neuen Menüpunkt hinzufügen (damit der Abruf weiter verfügbar ist).
2. Änderungen in Config und NetBox Device Role vornehmen.
3. Modul aktualisieren: `odoo-bin -u nt_serviceman` oder über die Odoo-Oberfläche.
