# NT:ServiceMan – Benutzerdokumentation

## Was ist NT:ServiceMan?

NT:ServiceMan ist ein Odoo-Modul, das **Configuration Items (CI)** – also technische Geräte wie Firewalls, Switches, Router oder Access Points – aus **NetBox** in Odoo abbildet und mit **wiederkehrenden Verträgen** verknüpft.

**Kernidee:** Die technische Inventardaten bleiben in NetBox („Source of Truth“). Odoo übernimmt sie lesend, reichert sie mit kaufmännischen Daten an und ordnet sie Verträgen zu.

---

## Wofür ist NT:ServiceMan gedacht?

- **Verbindung zwischen Vertrieb und Technik:** Verträge enthalten geplante Gerätemengen (Plan) und reale CI (Ist). So sieht man, ob Plan und Ist übereinstimmen.
- **Leistungszuordnung:** Pro Vertrag wird definiert, welche Leistungen (z. B. Dokumentation, Update-Service, Backup) für welche Geräteklassen gebucht werden.
- **NetBox-Anbindung:** Geräte werden nicht in Odoo angelegt, sondern aus NetBox übernommen. Änderungen an technischen Daten erfolgen in NetBox.
- **Keine Vollautomatik:** Der Abruf aus NetBox erfolgt manuell pro CI (Button „Hole von NetBox“). Spätere Automatisierung ist vorgesehen.

---

## Rollen und Zugriff

| Rolle | Zugriff |
|-------|---------|
| **NT:ServiceMan Admin** | Vollzugriff inkl. Konfiguration (NetBox, Leistungen, CI-Klassen, Device Roles) |
| **NT:ServiceMan Nutzer** | CI-Einträge verwalten, „Hole von NetBox“ ausführen – **kein** Zugriff auf Konfiguration |
| **Alle anderen** | Kein Zugriff auf NT:ServiceMan |

---

# Einrichtung (nur NT:ServiceMan Admin)

## 1. NetBox-Anbindung

Unter **NT:ServiceMan > Konfiguration > Einstellungen**:

- **NetBox-URL:** Basis-URL der NetBox-Instanz (z. B. `https://netbox.example.com`)
- **API-Token:** Token für die NetBox-REST-API
- **Test URL:** Klicken, um die Verbindung zu prüfen – Server, REST-API und NetBox-Struktur werden geprüft

Ohne gültige Konfiguration ist kein Abruf von Geräten möglich.

## 2. Device Roles von NetBox abrufen

Unter **NT:ServiceMan > Konfiguration** den Menüpunkt **„Device Roles von NetBox abrufen“** ausführen. Damit werden die NetBox-Geräterollen in Odoo gespiegelt.

## 3. CI-Klassen und Device Roles zuordnen

- **CI-Klassen** (Firewall, Switch, Router, Access Point) sind bereits vordefiniert und können angepasst werden.
- Jede **Device Role** aus NetBox muss einer **CI-Klasse** zugeordnet werden.
- Ort: **Konfiguration > CI-Klassen** – im Formular der CI-Klasse den Bereich „Device Roles“ bzw. den Button „Device Roles zuordnen“ nutzen.
- Alternativ: **Konfiguration > Device Roles** – dort pro Rolle die CI-Klasse auswählen.

Ohne Zuordnung bleiben CI „unklassifiziert“ und können ggf. nicht korrekt Verträgen zugeordnet werden.

## 4. Leistungen und Verfügbarkeit

- **Leistungen** (z. B. Dokumentation, Update-Service) unter **Konfiguration > Leistungen** pflegen.
- Pro **CI-Klasse** festlegen, welche Leistungen für diese Geräteklasse **verfügbar** sind (im CI-Klasse-Formular: „Verfügbare Leistungen“).

Diese Matrix bestimmt, welche Leistungen später im Vertrag pro Geräteklasse buchbar sind.

## 5. Optional: Leistungsmatrix am Produkt

Bei wiederkehrenden Produkten kann unter **Produkt > Tab „Leistungsmatrix“** vordefiniert werden, welche Leistungen und Mengen pro CI-Klasse in Verträge übernommen werden sollen. Ohne Vorbefüllung starten Verträge mit leerer Matrix.

---

# Nutzung

## CI anlegen und aus NetBox holen

1. **NT:ServiceMan > CI-Einträge > Neu**
2. **NetBox-ID** eintragen (die Device-ID aus NetBox).
3. Button **„Hole von NetBox“** klicken.
4. Odoo ruft die Gerätedaten ab und zeigt Name, Rolle, Tenant, Serial usw. (readonly). Der NetBox-Link öffnet das Gerät in NetBox in einem neuen Tab.

**Hinweis:** Ohne NetBox-ID ist kein Abruf möglich. Änderungen an Geräten in NetBox werden erst nach erneutem Klick auf „Hole von NetBox“ übernommen (kein automatischer Sync in v1.0).

## CI einem Vertrag zuordnen

**Variante A – im Vertrag:**
- Vertrag öffnen → Tab **„CMDB“**
- Button **„CI zuordnen“** → Wizard öffnet sich
- Unzugeordnete CI auswählen → **Zuordnen**

**Variante B – im CI:**
- CI öffnen → Feld **„Vertrag“** auswählen

**Einschränkung:** Ein CI kann nur einem Vertrag zugeordnet werden, wenn seine **CI-Klasse in der Leistungsmatrix** des Vertrags vorkommt.

## Vertrag: Leistungsmatrix und Plan/Ist

- Tab **„Leistungsmatrix“** im Vertrag: Pro CI-Klasse **Planmenge** eintragen und **Leistungen** per Checkbox buchen.
- Tab **„CMDB“**: Zeigt die zugeordneten **realen CI** und die **Ist-Menge** je CI-Klasse.
- **Plan/Ist-Vergleich:** In der Leistungsmatrix wird die Ist-Menge berechnet und angezeigt. Abweichungen (Plan ≠ Ist) sind sichtbar.
- **Filter in Vertragsliste:** „Plan-Ist-Abweichung“ und „Abweichung Service-Felder“ helfen, Verträge mit Abweichungen zu finden.

## Gebuchte Leistungen am CI

Sobald ein CI einem Vertrag zugeordnet ist, werden die für seine CI-Klasse gebuchten Leistungen automatisch am CI angezeigt (Bereich „Gebuchte Leistungen“). Diese Anzeige ist read-only – Änderungen erfolgen in der Vertrags-Leistungsmatrix.

## Service-Voraussetzungen (NetBox-Felder)

Manche Leistungen erfordern ausgefüllte NetBox-Felder am Gerät (z. B. Hersteller). Fehlende Felder werden:
- im CMDB-Tab des Vertrags (Indikator)
- im CI-Formular (Liste fehlender Felder + NetBox-Link)

angezeigt. Die Nachpflege erfolgt in NetBox.

---

# Wichtige Hinweise

- **NetBox bleibt Master:** Alle technischen Daten (Name, Rolle, Tenant, …) werden aus NetBox gelesen und sind in Odoo nicht editierbar.
- **Keine automatische Preisänderung:** Plan/Ist-Abweichungen führen nicht zu automatischen Vertragsanpassungen. Preisänderungen erfolgen manuell.
- **Soft Delete bei Leistungen:** Leistungen werden nicht gelöscht, sondern archiviert. In bestehenden Verträgen bleiben sie erhalten; bei neuen Verträgen sind sie nicht mehr auswählbar.
- **Produktmatrix:** Enthält ein Produkt archivierte Leistungen in seiner Matrix, werden diese bei neuen Verträgen nicht übernommen.

---

# Fehlerbehandlung

| Situation | Verhalten |
|-----------|-----------|
| NetBox-ID fehlt | „Hole von NetBox“ nicht ausführbar |
| Gerät in NetBox nicht gefunden | Sync-Status = Fehler, Fehlermeldung wird gespeichert |
| API-Fehler (z. B. Token ungültig) | Fehlermeldung im Sync-Ergebnis |

Bestehende Daten werden bei Fehlern nicht gelöscht. Nach Behebung des Problems (z. B. korrekter API-Token) den Abruf erneut ausführen.
