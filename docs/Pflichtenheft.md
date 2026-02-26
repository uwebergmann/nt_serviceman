# Pflichtenheft  
## NT:ServiceMan v0.9 – CI-Abbildung in Odoo mit NetBox-REST-Anbindung

**Projekt:** NT:ServiceMan  
**Version:** 0.9 / 0.9.1 (Architekturerweiterung)  
**Status:** Pflichtenheft  
**Ziel:** Startfähigkeit herstellen, fachliche/technische Ebenen trennen  
**Nicht-Ziel:** Vollständige Automatisierung

---

## 1. Zielsetzung

Dieses Projekt ist aus den Überlegungen zur konkreten Produktklasse **NT/Care** hervorgegangen. 
Ziel ist die **Abbildung von Services** – insbesondere die Verknüpfung zwischen der vertrieblichen 
bzw. kaufmännischen ERP-Welt und der technischen Welt. Grundsätzlich betreffen jedoch alle 
unsere Verträge diese Lücke. Beide Perspektiven betrachten denselben Vertrag aus unterschiedlichen 
Blickwinkeln. Die technische Sicht ist bislang etwas kurz gekommen, ist für unsere Arbeit 
aber notwendig.

Konkret sollen **Configuration Items (CI)** in **Odoo** abgebildet und mit **wiederkehrenden 
Verträgen** verknüpft werden. Eine frühere Idee war, Service-IDs zu verwenden und vom 
Vertrag ausgehend an alle vertragsrelevanten Elemente weiterzugeben. Das hätte erfordert, 
dass die Service-ID manuell oder automatisiert in jedes Element eingetragen wird – 
inklusive aller Änderungen im Betriebsablauf. Damit verbunden wären große Risiken 
durch Fehleinträge oder vergessene Datenpflege.

Die Abbildung soll so erfolgen: Ein Vertrag erhält beliebig viele CI. Der Vertrag bestimmt 
die **SLA** (Reaktionszeiten, Wiederherstellungszeiten usw.), während in den CI die 
**Leistungen** definiert werden (z.B. CVE-Überwachung, Monitoring, Update-Service). 
Das CI wird nicht in Odoo „aus der Luft“ angelegt, sondern primär in **NetBox**. 
Ein Automatismus legt es in Odoo an und reichert es mit kaufmännischen Daten an. 
Die technische Inventarquelle bleibt **NetBox**; Odoo übernimmt die **lesende Spiegelung** 
ausgewählter Felder sowie die **servicebezogene Anreicherung** und Vertragszuordnung.

Version 0.9 verfolgt ausdrücklich einen **Minimalansatz**, der:

- fachlich korrekt,
- technisch erweiterbar,
- organisatorisch delegierbar

ist.

---

## 2. Grundsatzentscheidungen

Das Pflichtenheft unterscheidet klar zwischen **Vertriebsplanung**, **operativer Geräteverwaltung** 
und **Vertragszuordnung** – ohne Vermischung dieser Ebenen.

### 2.1 CI-Definition

Ein **CI (Configuration Item)** ist ausschließlich ein real existierendes technisches Gerät, 
das in NetBox angelegt wurde.

Ein CI entsteht:
- nicht im Vertrieb
- nicht im Angebot
- nicht als Platzhalter
- nicht als Planposition

Sondern ausschließlich: nach realer Existenz eines Geräts und dessen Anlage in NetBox.

Odoo übernimmt CI lesend aus NetBox und reichert sie um servicebezogene Felder an.  
Im Kundenportal werden ausschließlich reale CI angezeigt.

### 2.2 Trennung von Plan und Realität

Zur Unterstützung des Vertriebs wird eine separate **Planungsebene** eingeführt.  
Diese ersetzt die frühere Idee von „leeren CI“.

Ein Vertrag (z.B. NT/Care) enthält:

**A) Planpositionen (Vertriebsplanung)**
- Geräteklasse (z.B. FW, SW, RTR, AP)
- geplante Menge

Diese Planpositionen:
- sind keine technischen Objekte
- erscheinen nicht im Portal
- dienen nur als Indikator für Plan/Ist-Abweichungen

**B) Reale CI (operative Ebene)**
- stammen aus NetBox
- sind dem Vertrag zugeordnet
- sind portal-sichtbar
- sind abrechnungsrelevant

### 2.3 Geräteklassen

Geräteklassen werden **nicht hart im Code** definiert.

Stattdessen:
- eigenes konfigurierbares Modell **„CI-Klasse“** (vgl. Kap. 8.4)
- frei anlegbar
- aktiv/inaktiv schaltbar

Für den Start werden vordefiniert:
- FW (Firewall)
- SW (Switch)
- RTR (Router)
- AP (Access Point)

Keine Server-, Storage- oder generischen IT-Klassen.

**Architekturentscheidung (v0.9.1):** CI-Klassen sind vollständig unabhängig von NetBox. Sie bilden die fachliche Steuergröße für Abrechnung, SLA-Logik, Plan/Ist-Vergleich und Portal-Darstellung.

### 2.4 Plan/Ist-Logik

Pro Vertrag:
- Planmenge je Geräteklasse
- Ist-Menge = Anzahl aktiver CI je Klasse

Bei Abweichung:
- Hinweis an Vertrieb (Aktivität / Chatter)
- keine automatische Preisänderung
- Preisänderungen erfolgen ausschließlich manuell

**Ziel:** Transparenz ohne automatische Vertragsmutation.

### 2.5 Dynamisches Vertragsmodell

Verträge (z.B. NT/Care) sind dynamisch:
- Geräte können hinzukommen
- Geräte können entfallen
- Preis kann angepasst werden
- Anpassungen erfolgen bewusst durch Menschen

Keine automatische Verbrauchsabrechnung.

### 2.6 Architekturprinzipien

- NetBox bleibt technische Source of Truth.
- Odoo speichert keine veränderbaren technischen Daten.
- Keine Platzhalter-CI.
- Keine automatische Synchronisation in v0.9.
- Keine automatische Preislogik.
- Fokus auf einfache, stabile Grundstruktur.

---

## 3. Abgrenzung / Nicht-Ziele (v0.9)

In v0.9 erfolgt der NetBox-Abruf **nur manuell** per Button „Hole von NetBox“. Später sollen Änderungen an CI in NetBox automatisch nach Odoo übernommen werden, sodass die in Odoo angezeigten Daten mit NetBox übereinstimmen.

Nicht Bestandteil dieser Version sind:

- Platzhalter-CI oder „leere CI“
- automatische Synchronisation (Webhooks, periodische Vollabgleiche/Cronjobs)
- Rückschreiben von Daten nach NetBox
- automatische Preislogik oder Verbrauchsabrechnung
- Paketlogik (NT/Care Silber / Gold / …)
- CVE-, Backup- oder Health-Automatisierung
- Portal- oder Reporting-Funktionen

Diese Themen sind bewusst ausgeklammert, um einen schnellen und sauberen Start zu ermöglichen.

---

## 4. Fachlicher Zielzustand (Definition of Done)

Die Version gilt als erfolgreich umgesetzt, wenn:

1. Das Modell **CI-Klasse** existiert (FW, SW, RTR, AP vordefiniert, konfigurierbar).
2. **Planpositionen** (Geräteklasse + Planmenge) sind am Vertrag abbildbar.
3. Ein **reales CI** kann in Odoo angelegt werden.
4. Das CI hat ein editierbares Feld **NetBox-ID**. Ohne gültige NetBox-ID ist kein Abruf möglich.
5. Per Button **„Hole von NetBox“** wird der REST-Abruf ausgelöst (nur wenn NetBox-ID ausgefüllt).
6. Mindestens folgende Felder werden aus NetBox übernommen und **readonly** angezeigt:
   - NetBox-ID
   - Geräte-Name
   - Rollen-Name
   - Tenant-Name
7. Mehrere CI können **einem wiederkehrenden Vertrag** zugeordnet werden.
8. Die zugeordneten **reale CI** sind als Liste im Vertrag sichtbar.
9. **Plan/Ist-Vergleich** (Planmenge vs. Anzahl CI je Geräteklasse) ist möglich; bei Abweichung Hinweis an Vertrieb (Aktivität/Chatter).

---

## 5. Systemlandschaft

| System  | Rolle |
|--------|------|
| NetBox | Source of Truth für technische Inventardaten |
| Odoo  | Abbildung von CI, Verträgen und Services |
| NT/Care | Produktlogik auf Basis von CI-Zuordnungen |

---

## 6. Grundprinzipien

Vgl. Abschnitt 2.6. Ergänzend:

- Alle aus NetBox übernommenen Felder sind **readonly**.
- Änderungen an NetBox-Daten erfolgen ausschließlich in NetBox.
- Die Architektur muss spätere Automatisierung **ohne Bruch** erlauben.

---
## 7. Systemkonfiguration

Zur Anbindung von NetBox wird in Odoo eine zentrale Systemkonfiguration eingeführt.
Diese Konfiguration ist **nicht CI-spezifisch**, sondern gilt systemweit.

### 7.0 Benutzeroberfläche (Einstellungen)

Unter **NT:ServiceMan > Konfiguration > Einstellungen** wird ein Formular bereitgestellt mit:

| Feld             | Typ    | Beschreibung                                      |
|------------------|--------|---------------------------------------------------|
| **NetBox-URL**   | Text   | Basis-URL der NetBox-Instanz (z.B. https://netbox.example.com) |
| **Test URL**     | Button | Prüft die Verbindung: (1) Server erreichbar, (2) REST-API antwortet, (3) NetBox-API-Struktur erkannt |
| **Test-Ergebnis**| Text   | Ausgabe des URL-Tests (readonly)                  |

Zugriff nur für Benutzer mit der Gruppe **NT:ServiceMan Admin**.

### 7.0.1 Menüsichtbarkeit und Benutzerzugriff

- **App-Kachel** (NT:ServiceMan auf der Startseite):  
  Für alle Benutzer sichtbar (base.group_user).

- **Konfiguration** (inklusive aller zukünftigen Untermenüpunkte wie Einstellungen):  
  Sichtbar und bedienbar nur für Nutzer, die die Gruppe **NT:ServiceMan Admin** haben (Checkbox beim Benutzer gesetzt).

- **Rest der App** (Daten, CI-Einträge sowie zukünftige operative Menüpunkte):  
  Für alle Benutzer sichtbar und bedienbar.

### 7.1 Konfigurationsparameter NetBox

Folgende Konfigurationsparameter werden benötigt:

| Parameter | Typ | Beschreibung |
|---------|----|--------------|
| netbox_base_url | URL | Basis-URL der NetBox-Instanz (z. B. https://netbox.example.com) |
| netbox_api_token | Secret | API-Token zur Authentifizierung gegen die NetBox-REST-API |

Die vollständige REST-URL für den Abruf eines Devices ergibt sich aus:

`{netbox_base_url}/api/dcim/devices/{netbox_id}/`

### 7.2 Ablageort der Konfiguration

Die Konfigurationsparameter werden als **Systemparameter** in Odoo gespeichert.

Geeigneter technischer Ablageort ist:

- `ir.config_parameter`

Alternativ (bei Mehrmandantenfähigkeit):

- Konfigurationsfelder auf `res.company`

Die konkrete technische Entscheidung ist in der Implementierung festzulegen.

### 7.3 Rechte- und Sicherheitskonzept

Der Zugriff auf die NetBox-Konfigurationsparameter ist **rollenbasiert** zu beschränken.

- Lesender Zugriff:
  - nur für Benutzer mit administrativen Rechten
- Schreibender Zugriff:
  - ausschließlich für Benutzer mit System-Administrator-Rechten

Normale Benutzer und Techniker dürfen:

- die NetBox-URL **nicht sehen**
- das API-Token **nicht einsehen oder verändern**

### 7.4 Änderbarkeit und Betrieb

Änderungen an der NetBox-Konfiguration gelten:

- **global**
- **sofort**
- **ohne Rückwirkung auf bestehende CI**

Die Änderung der Konfiguration darf keinen automatischen Re-Sync aller CI auslösen.

---

## 8. CI-Datenmodell (v0.9 – minimal)

### 8.1 Pflichtfelder

| Feld | Typ | Herkunft | Beschreibung | Status |
|----|----|--------|-------------|--------|
| netbox_id | Integer / Char | manuell | ID des Devices in NetBox | ✓ |
| netbox_name | Char | NetBox | Name des Geräts (über name/netbox_display) | ✓ |
| netbox_role_id | Many2one | NetBox | Relation auf netbox.device_role; ersetzt netbox_role_name (v0.9.1) | v0.9.1 |
| netbox_tenant_name | Char | NetBox | Tenant / Kunde | ✓ |
| netbox_url | Char | NetBox | Link (Anzeigename klickbar → display_url) | ✓ |
| netbox_created | Datetime | NetBox | Erstellungszeitpunkt aus NetBox (readonly) | ✓ |
| netbox_last_updated | Datetime | NetBox | Letzte Änderung aus NetBox (readonly); steuert Sync-Logik | ✓ |
| netbox_last_sync | Datetime | System | Zeitpunkt letzter Abruf | ✓ |
| netbox_sync_state | Selection | System | ok / failed | ✓ |
| netbox_sync_error | Text | System | Fehlermeldung (nur bei Fehler sichtbar) | ✓ |
| ci_class_id | Many2one | Mapping | CI-Klasse (via Role-Mapping, v0.9.1) | v0.9.1 |

### 8.2 Feldregeln

- `netbox_id` ist editierbar
- alle anderen `netbox_*` Felder sind readonly
- **netbox_created / netbox_last_updated:** Gleiche Sync-Logik wie bei NetBox Device Roles (Kap. 8.5): Feld leer oder NetBox jünger → Aktualisierung; sonst keine Änderung.
- **ci_class_id:** Wird aus dem Mapping Device Role → CI-Klasse abgeleitet (readonly). Existiert ein Mapping für die NetBox-Device-Role des Geräts, wird die CI-Klasse angezeigt; sonst bleibt das Feld leer.
- Service-Felder sind in v0.9 nicht Bestandteil
- **v0.9.1:** Anzeige der Rolle ausschließlich über Relation `netbox_role_id`; der Rollenname kommt aus `netbox_device_role.name` (Mapping Role-ID → Role-Name). Das bisherige Textfeld `netbox_role_name` entfällt.

**Anzeige der CI-Klasse im CI-Formular:**

- Die **CI-Klasse** wird im Formular eines Configuration Items angezeigt.
- **Position:** direkt unterhalb der NetBox-ID (linke Spalte).
- **Herkunft:** Die CI-Klasse leitet sich aus dem Mapping NetBox-Device-Role → CI-Klasse ab: Die Device Role des Geräts kommt aus dem NetBox-Abruf; über das Mapping (Kap. 8.6) wird die zugeordnete CI-Klasse ermittelt. Das Feld ist readonly.
- Ohne Mapping oder ohne zugeordnete Device Role bleibt die CI-Klasse leer.

---

### 8.3 CI-Klassen (Geräteklassen)

Vgl. Abschnitt 8.4. Konfigurierbares Modell „CI-Klasse“ mit vordefinierten Werten 
FW, SW, RTR, AP für den Start. Frei anlegbar, aktiv/inaktiv schaltbar.

---

## 8.4 CI-Klassen (v0.9.1 – verbindliche Architektur)

Einführung eines konfigurierbaren Modells **„CI-Klasse“** als fachliche Ebene in Odoo.

**Modell:** `ci_class` (technischer Name in Implementierung festzulegen)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| code | Char | Kurzcode (z.B. FW, SW, RTR, AP) |
| name | Char | Bezeichnung |
| description | Text | Optionale Beschreibung |
| active | Boolean | Aktiv/Inaktiv schaltbar |

**Stellung der CI-Klassen:**

CI-Klassen sind die **fachliche Steuergröße** für:
- Abrechnung
- SLA-Logik
- Plan/Ist-Vergleich
- zukünftige Automatisierung
- Portal-Darstellung

**Wichtig:** CI-Klassen sind vollständig unabhängig von NetBox. Sie werden ausschließlich in Odoo gepflegt und haben keinen Bezug zu NetBox-Device-Rollen, es sei denn, eine explizite Zuordnung wird über das Mapping-Modell (Kap. 8.6) hergestellt.

**Benutzerschnittstelle CI-Klassen-Liste:**

- Die Liste ist **inline bearbeitbar** (Bearbeitung direkt in der Zeile möglich).
- Jede Zeile endet mit einem Button **„→ Formular“**, der die CI-Klasse im Formular öffnet (inkl. zugeordneter Device Roles, Zuordnungsbutton usw.).
- Beide Möglichkeiten (Inline-Bearbeitung und Formularöffnung) stehen parallel zur Verfügung.

---

## 8.5 NetBox Device Roles (v0.9.1 – technische Ebene)

Ein neues Modell wird eingeführt:

**Modell:** `netbox.device_role`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| netbox_id | Integer | Eindeutige ID in NetBox |
| name | Char | Bezeichnung |
| active | Boolean | Aktiv/Archiviert |
| netbox_created | Datetime | Erstellungszeitpunkt aus NetBox (readonly) |
| netbox_last_updated | Datetime | Letzte Änderung aus NetBox (readonly) |
| ci_class_id | Many2one | Zuordnung zur CI-Klasse (editierbar) |

**Eigenschaften:**

- Diese Tabelle ist ein lokaler Spiegel der NetBox Device Roles.
- Sie wird ausschließlich aus NetBox befüllt oder aktualisiert.
- Manuelle Änderungen sind nicht vorgesehen (außer durch Admin im Ausnahmefall).

**Regeln:**

- Rollen dürfen nicht gelöscht werden (nur archiviert über `active=False`).
- Beim CI-Sync muss die Device Role automatisch angelegt oder aktualisiert werden (Upsert-Logik über `netbox_id`).

**NetBox-Timestamps und Sync-Logik (created / last_updated):**

NetBox liefert pro Objekt die Felder `created` und `last_updated`. Diese werden in Odoo gespiegelt:

- **netbox_created:** Wird stets mit dem Wert aus NetBox befüllt (bei Anlage und bei jeder Aktualisierung).

- **netbox_last_updated:** Steuert die Aktualisierungslogik:
  1. **Objekt neu oder Feld leer:** Der Wert wird aus NetBox übernommen; alle anderen Felder werden entsprechend aktualisiert.
  2. **Feld enthält bereits einen Wert:** Es wird mit dem Wert aus NetBox verglichen:
     - **NetBox jünger:** Alle Felder in Odoo werden auf den neuesten Stand gebracht (inkl. `netbox_last_updated`).
     - **NetBox gleich oder älter:** Es erfolgt keine Änderung; lokale Daten bleiben unverändert.

---

## 8.6 Mapping Device Role ↔ CI-Klasse (v0.9.1)

**Kardinalität:**

- Eine **Device Role** kann **genau einer** CI-Klasse angehören (Many2one).
- Eine **CI-Klasse** kann **viele** Device Roles enthalten (One2many).

**Technische Abbildung:**

- Modell `nt_serviceman.netbox_device_role`: Feld `ci_class_id` (Many2one → `nt_serviceman.ci_class`).
- Modell `nt_serviceman.ci_class`: Feld `device_role_ids` (One2many → `nt_serviceman.netbox_device_role`, inverse von `ci_class_id`).

**Benutzerschnittstellen:**

| Ort | Darstellung |
|-----|-------------|
| **Device-Roles-Liste** | Auswahlfeld „CI-Klasse“; Zuordnung direkt in der Liste möglich |
| **CI-Klasse-Formular** | Liste der zugeordneten Device Roles; Button „Device Roles zuordnen“ zum Hinzufügen weiterer Rollen |

**Zuordnungslogik beim Hinzufügen (CI-Klasse-Formular):**

Die Auswahl beim Zuordnen zeigt **nur Device Roles, die noch keiner CI-Klasse zugeordnet sind**. Bereits verknüpfte Rollen erscheinen nicht in der Auswahl (eindeutige 1:1-Zuordnung pro Device Role).

**Beim CI-Sync:**

- Wenn Mapping existiert → `ci_class_id` am CI automatisch setzen (über Device Role).
- Wenn kein Mapping existiert → CI bleibt „unklassifiziert“.
- Kein automatischer Sync-Fehler bei fehlender Klassifizierung.

---

## 8.7 Anzeige im Portal (v0.9.1)

- **Primär sichtbar:** CI-Klasse
- **Device Role** nur als Detailinformation

---

## 9. REST-Integration NetBox → Odoo

### 9.1 Auslöser (v0.9)

- Manuell durch Benutzeraktion: Button **„Hole von NetBox“**
- **Voraussetzung:** Das Feld NetBox-ID muss mit einer gültigen ID ausgefüllt sein; sonst ist kein Abruf möglich.

### 9.2 REST-Aufruf

- Endpoint: `/api/dcim/devices/{netbox_id}/`
- Authentifizierung: NetBox API Token
- Richtung: Odoo → NetBox (read only)

### 9.3 Übernommene Felder

| NetBox-Feld | Odoo-Feld (v0.9) | Odoo-Feld (v0.9.1) |
|-------------|------------------|---------------------|
| id | netbox_id | netbox_id |
| name | netbox_name | netbox_name |
| role | netbox_role_name | netbox_role_id (Upsert in netbox.device_role) |
| tenant.name | netbox_tenant_name | netbox_tenant_name |
| display_url / url | netbox_url | netbox_url |

**v0.9.1:** Die Device Role (`role`) wird in die Tabelle `netbox.device_role` gespiegelt (Upsert über `netbox_id`). Das CI erhält eine Many2one-Referenz `netbox_role_id`. Über das Mapping (Kap. 8.6) wird gegebenenfalls `ci_class_id` am CI gesetzt.

---

## 10. Fehlerbehandlung

| Situation | Verhalten |
|--------|----------|
| NetBox-ID fehlt | Kein Sync möglich |
| Gerät nicht gefunden | Sync-Status = failed |
| API-Fehler | Fehlertext speichern |
| Erfolgreicher Abruf | Sync-Status = ok |

Fehler führen nicht zum Löschen oder Überschreiben bestehender Daten.

---

## 11. Vertragskopplung

Ein Vertrag enthält zwei Ebenen (vgl. Abschnitt 2.2):

**Planpositionen (Vertriebsplanung):**
- Geräteklasse und geplante Menge
- keine technischen Objekte, nicht portal-sichtbar
- Indikator für Plan/Ist-Abweichungen

**Reale CI (operative Ebene):**
- Ein CI gehört **genau zu einem** wiederkehrenden Vertrag.
- Ein Vertrag kann **mehrere CI** enthalten.
- CI stammen aus NetBox, sind portal-sichtbar, abrechnungsrelevant.
- CI werden im Vertrag tabellarisch angezeigt (Name, CI-Klasse, Rolle/Tenant). **v0.9.1:** Primär CI-Klasse, Device Role als Detail.

---

## 12. Erweiterbarkeit

Die Architektur muss spätere Erweiterungen ermöglichen:

- **Automatisierte Synchronisation NetBox → Odoo:** Änderungen an CI in NetBox sollen später automatisch nach Odoo übernommen werden. Die in Odoo angezeigten technischen Daten sollen mit NetBox übereinstimmen. (In v0.9 nur manueller Abruf per Button.)
- zusätzliche NetBox-Felder
- Paketlogik NT/Care
- Portal-Darstellung
- Integration mit NT/RiskMan

Ohne Refactoring der Grundstruktur.

---

## 13. Zusammenfassung

Dieses Pflichtenheft definiert bewusst eine kleine, klare Startversion, die:

- die Service-Abbildung real nutzbar macht,
- technische Blockaden auflöst,
- und zukünftige Automatisierung vorbereitet.

Version 0.9 ist ein Startpunkt – kein Endzustand.

**Architekturerweiterung v0.9.1:** Trennung von fachlicher Ebene (CI-Klassen) und technischer Ebene (NetBox Device Roles). Das konfigurierbare Mapping ermöglicht eine flexible Zuordnung, ohne dass CI-Klassen an NetBox-Strukturen gebunden sind.

---

# Erledigte und offene Punkte: NT:ServiceMan

Diese Liste bildet den Umsetzungsstand ab (Stand: Fortlaufend aktualisiert).

## ✅ Erledigt

| # | Thema | Anmerkung |
|---|-------|-----------|
| 1 | **Config**: NetBox-URL, API-Token, Test-URL | Prüft Server, REST-API, NetBox-Struktur, Token-Gültigkeit |
| 2 | **CI anlegbar** | Modell `nt_serviceman.configuration_item` |
| 3 | **NetBox-ID** editierbar | Pflicht für Abruf |
| 4 | **Button „Hole von NetBox“** | Manueller REST-Abruf |
| 5 | **NetBox-Felder übernommen** | Anzeigename, Serial, Hardware-Typ, Rolle, Tenant (readonly) |
| 6 | **Name** wird aus NetBox übernommen | Name optional, automatisch beim Abruf |
| 7 | **NetBox-Link** | Anzeigename klickbar → öffnet Gerät in NetBox (neuer Tab) |
| 8 | **Roh-JSON** für Debug | Vollständige API-Antwort sichtbar |
| 9 | **Einstellungen-Überschrift** | „Einstellungen NT:ServiceMan“ statt technischem Namen |
| 10 | **Rechte** | Config nur für NT:ServiceMan Admin |
| 11 | **Kap. 8.1 Felder** | netbox_tenant_name, netbox_last_sync, netbox_sync_state, netbox_sync_error |
| 12 | **CI-Klasse** (Kap. 8.4) | Modell nt_serviceman.ci_class, FW/SW/RTR/AP vordefiniert |

## ⏳ Offen (v0.9 / v0.9.1)

| # | Thema | Quelle |
|---|-------|--------|
| 1 | **NetBox Device Roles** – Modell netbox.device_role, Upsert beim Sync | Kap. 8.5 |
| 2 | **Mapping** – netbox.role_ci_class_map, Zuordnung Role → CI-Klasse | Kap. 8.6 |
| 3 | **CI-Feldanpassung** – netbox_role_id (Many2one), netbox_role_name entfällt | Kap. 8.1 |
| 4 | **Planpositionen** am Vertrag | Kap. 2.2, 4.2, 11 |
| 5 | **Vertragskopplung** | Ein Vertrag enthält mehrere CI, CI-Liste im Vertrag (Kap. 4.7 f., 11) |
| 6 | **Plan/Ist-Vergleich** mit Hinweis bei Abweichung (Aktivität/Chatter) | Kap. 4.9 |
| 7 | **Portal** – CI-Klasse primär, Device Role als Detail | Kap. 8.7 |
| 8 | **Config in ir.config_parameter / res.company** (aktuell: eigenes Config-Modell) | Kap. 7.2 |
