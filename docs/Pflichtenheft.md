# Pflichtenheft  
## NT:ServiceMan v1.0 – CI-Abbildung in Odoo mit NetBox-REST-Anbindung

**Projekt:** NT:ServiceMan  
**Version:** 1.0 (erreicht)  
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
- Geräteklasse (z.B. Firewall, Switch, Router, Access Point)
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
- Firewall
- Switch
- Router
- Access Point

Keine Server-, Storage- oder generischen IT-Klassen.

**Architekturentscheidung (v0.9.1):** CI-Klassen sind vollständig unabhängig von NetBox. Sie bilden die fachliche Steuergröße für Abrechnung, SLA-Logik, Plan/Ist-Vergleich und Portal-Darstellung.

### 2.4 Plan/Ist-Logik

Pro Vertrag:
- Planmenge je Geräteklasse
- Ist-Menge = Anzahl aktiver CI je Klasse

Bei Abweichung:
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

1. Das Modell **CI-Klasse** existiert (Firewall, Switch, Router, Access Point vordefiniert, konfigurierbar).
2. **Planpositionen** (Geräteklasse + Planmenge) sind am Vertrag abbildbar.
3. Ein **reales CI** kann in Odoo angelegt werden.
4. Das CI hat ein editierbares Feld **NetBox-ID**. Ohne gültige NetBox-ID ist kein Abruf möglich.
5. Per Button **„Hole von NetBox“** wird der REST-Abruf ausgelöst (nur wenn NetBox-ID ausgefüllt). Der Button ist für **NT:ServiceMan Admin** und **NT:ServiceMan Nutzer** bedienbar.
6. Mindestens folgende Felder werden aus NetBox übernommen und **readonly** angezeigt:
   - NetBox-ID
   - Geräte-Name
   - Rollen-Name
   - Tenant-Name
7. Mehrere CI können **einem wiederkehrenden Vertrag** zugeordnet werden.
8. Die zugeordneten **reale CI** sind als Liste im Vertrag sichtbar.
9. **Plan/Ist-Vergleich** (Planmenge vs. Anzahl CI je Geräteklasse) ist möglich.

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

### 7.0 Benutzeroberfläche (Konfiguration)

Unter **NT:ServiceMan > Konfiguration** werden folgende Bereiche bereitgestellt (alle nur für NT:ServiceMan Admin):

**Einstellungen** (NetBox-Anbindung):

| Feld             | Typ    | Beschreibung                                      |
|------------------|--------|---------------------------------------------------|
| **NetBox-URL**   | Text   | Basis-URL der NetBox-Instanz (z.B. https://netbox.example.com) |
| **Test URL**     | Button | Prüft die Verbindung: (1) Server erreichbar, (2) REST-API antwortet, (3) NetBox-API-Struktur erkannt |
| **Test-Ergebnis**| Text   | Ausgabe des URL-Tests (readonly)                  |

**Leistungen** (v0.9.2): Editierbare Liste der erbringbaren Leistungen; vgl. Kap. 8.7.

**Leistung pro Geräteklasse** (v0.9.2): Konfiguration, welche Leistung für welche CI-Klasse verfügbar ist; vgl. Kap. 8.8. Die Zuordnung erfolgt im CI-Klasse-Formular.

**CI-Klassen** (Kap. 8.4): Geräteklassen (Firewall, Switch, Router, Access Point) konfigurieren und mit Device Roles verknüpfen.

**Device Roles** (Kap. 8.5): NetBox Device Roles anzeigen; Menüpunkt „Device Roles von NetBox abrufen" zum Abruf aus NetBox.

**Hinweis:** Das frühere Untermenü „Daten" wurde entfernt; CI-Klassen und Device Roles sind vollständig in die Konfiguration verschoben. Änderungen sollen nur von Administratoren (NT:ServiceMan Admin) vorgenommen werden.

Zugriff auf alle Konfigurationsbereiche nur für **NT:ServiceMan Admin**.

### 7.0.1 Menüsichtbarkeit und Benutzerzugriff

Es gelten genau drei Rollen:

- **NT:ServiceMan Admin**
- **NT:ServiceMan Nutzer**
- **alle anderen Benutzer** (keine der beiden Gruppen)

**Berechtigungsmatrix:**

- **NT:ServiceMan Admin:**  
  Vollzugriff auf die komplette App (inkl. Konfiguration und aller Buttons/Aktionen).

- **NT:ServiceMan Nutzer:**  
  Zugriff auf operative Menüs und Formulare (z.B. **CI-Einträge**), inklusive Bedienung der Buttons in den Formularen (z.B. **„Hole von NetBox"** am CI).  
  **Kein Zugriff** auf das Menü **Konfiguration** und dessen Unterpunkte (Einstellungen, Leistungen, CI-Klassen, Device Roles).

- **alle anderen Benutzer:**  
  **Kein Zugriff** auf NT:ServiceMan (keine App-Kachel, keine Menüs, keine Modelle).

### 7.1 Konfigurationsparameter NetBox

Folgende Konfigurationsparameter werden benötigt:

| Parameter | Typ | Beschreibung |
|---------|----|--------------|
| netbox_base_url | URL | Basis-URL der NetBox-Instanz (z. B. https://netbox.example.com) |
| netbox_api_token | Secret | API-Token zur Authentifizierung gegen die NetBox-REST-API |

Die vollständige REST-URL für den Abruf eines Devices ergibt sich aus:

`{netbox_base_url}/api/dcim/devices/{netbox_id}/`

### 7.2 Ablageort der Konfiguration (v0.9.10 umgesetzt)

Die Konfigurationsparameter (NetBox-URL, API-Token) werden als **Systemparameter** in `ir.config_parameter` gespeichert (Keys: `nt_serviceman.netbox_base_url`, `nt_serviceman.netbox_api_token`).

Die Bedienoberfläche (NT:ServiceMan > Konfiguration > Einstellungen) bleibt unverändert; das Formular liest und schreibt transparent in `ir.config_parameter`.

### 7.3 Rechte- und Sicherheitskonzept

Der Zugriff auf NT:ServiceMan erfolgt **rollenbasiert** über die Gruppen:

- `nt_serviceman.group_nt_serviceman_admin` (NT:ServiceMan Admin)
- `nt_serviceman.group_nt_serviceman_user` (NT:ServiceMan Nutzer)

Die Berechtigungen sind wie folgt umzusetzen:

- **NT:ServiceMan Admin**
  - Vollzugriff auf alle NT:ServiceMan-Modelle und Menüs
  - exklusiver Zugriff auf **Konfiguration** (Einstellungen, Leistungen, CI-Klassen, Device Roles)
  - darf NetBox-URL/API-Token sehen und ändern

- **NT:ServiceMan Nutzer**
  - Vollzugriff auf operative NT:ServiceMan-Funktionen (**CI-Einträge** inkl. Formularaktionen wie „Hole von NetBox")
  - kein Zugriff auf Konfigurationsmenü und keine Einsicht in NetBox-URL/API-Token

- **alle anderen**
  - kein Zugriff auf die NT:ServiceMan-App

### 7.4 Änderbarkeit und Betrieb

Änderungen an der NetBox-Konfiguration gelten:

- **global**
- **sofort**
- **ohne Rückwirkung auf bestehende CI**

Die Änderung der Konfiguration darf keinen automatischen Re-Sync aller CI auslösen.

### 7.5 Chatter (Odoo mail.thread)

Der Chatter (Nachrichten, Aktivitäten, Änderungshistorie) wird nur für ausgewählte Modelle aktiviert:

| Objekt | Typ | Chatter vorhanden? |
|--------|-----|--------------------|
| nt_serviceman.configuration_item | Modell | Ja |
| nt_serviceman.ci_class | Modell | Ja |
| nt_serviceman.service | Modell | Ja |
| nt_serviceman.config | Modell | Nein |
| nt_serviceman.netbox_device_role | Modell | Nein |
| nt_serviceman.contract_ci_class_matrix_line | Modell | Nein |
| nt_serviceman.product_ci_class_matrix_line | Modell | Nein |
| nt_serviceman.contract_configuration_item_assign | Wizard (Transient) | – |
| nt_serviceman.ci_class_device_role_assign | Wizard (Transient) | – |

**Technik:** Chatter wird über `_inherit = ['mail.thread']` (und ggf. `mail.activity.mixin`) realisiert. Das Modul `mail` muss in der Abhängigkeit (`depends`) stehen.

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
| cmdb_id | Integer | manuell | Legacy CMDB-ID (Abwärtskompatibilität); optional | v0.9.1 |
| contract_id | Many2one | Zuordnung | Vertrag (contract.recurrent); CI gehört genau einem Vertrag | v0.9.1 |
| contract_service_ids | Many2many | Kopie | Gebuchte Leistungen – Kopie aus Vertrags-Leistungsmatrix (Kap. 11.3); keine Verlinkung | v0.9.3 |

### 8.2 Feldregeln

- `netbox_id` ist editierbar
- alle anderen `netbox_*` Felder sind readonly
- **netbox_created / netbox_last_updated:** Gleiche Sync-Logik wie bei NetBox Device Roles (Kap. 8.5): Feld leer oder NetBox jünger → Aktualisierung; sonst keine Änderung.
- **ci_class_id:** Wird aus dem Mapping Device Role → CI-Klasse abgeleitet (readonly). Existiert ein Mapping für die NetBox-Device-Role des Geräts, wird die CI-Klasse angezeigt; sonst bleibt das Feld leer.
- **cmdb_id:** Optional, editierbar; erhält das bisherige CMDB-ID-Feld für Abwärtskompatibilität.
- **contract_id:** Editierbar; Zuordnung zum wiederkehrenden Vertrag. Ein CI gehört höchstens einem Vertrag.
- **contract_service_ids:** Kopie der gebuchten Leistungen aus der Vertrags-Leistungsmatrix; wird automatisch befüllt bei Vertragszuordnung (Kap. 11.3). Keine Relation – ermöglicht Filter, Sortierung und Gruppierung am CI.
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
Firewall, Switch, Router, Access Point für den Start. Frei anlegbar, aktiv/inaktiv schaltbar.

---

## 8.4 CI-Klassen (v0.9.1 – verbindliche Architektur)

Einführung eines konfigurierbaren Modells **„CI-Klasse“** als fachliche Ebene in Odoo.

**Modell:** `ci_class` (technischer Name in Implementierung festzulegen)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| code | Char | Kurzcode (z.B. Firewall, Switch, Router, Access Point) |
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

## 8.7 Leistungen (Services) – v0.9.2

Es wird eine **editierbare Liste der Leistungen** eingeführt, die NETHINKS grundsätzlich erbringen kann.
Diese Liste bildet die Grundlage für spätere Paketlogik, Vertriebsberechnung und CI-Anreicherung.

**Modell:** `nt_serviceman.service` (Leistung)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| code | Char | Kurzcode (z.B. Dokumentation, Update-Service) |
| name | Char | Bezeichnung |
| description | Text | Ausführliche Beschreibung der Leistung |
| active | Boolean | Aktiv/Inaktiv schaltbar |
| sequence | Integer | Sortierreihenfolge (für Anzeige) |

**Vorbefüllung bei Installation:** Die folgenden sieben Leistungen werden als Stammdaten angelegt:

| Code | Name | Beschreibung |
|------|------|--------------|
| Dokumentation | Dokumentation | Managementeinheit in Doku erfasst |
| Konfigurations-Service | Konfigurations-Service | Unterstützung bei Konfiguration und Betrieb der Managementeinheit |
| Proaktiver Sicherheits-Service (CVE) | Proaktiver Sicherheits-Service (CVE) | E-Mail zu CVE/Sicherheitslücken + Maßnahmen |
| Update-Service | Update-Service | Service-Updates gemäß Basisvertrag |
| Backup-Service | Backup-Service | Regelmäßige Konfig-Speicherung, Wiederherstellung auf Anfrage |
| 2nd-Level-Support | 2nd Level Support | Eskalation an Gerätehersteller/Drittanbieter |
| 2nd-Level-Management | 2nd Level Management | Zusätzliche Supportleistung bei Bedarf (vgl. 2nd Level Support) |

**Benutzerschnittstelle:**
- Menü **NT:ServiceMan > Konfiguration > Leistungen**
- Liste mit inline Bearbeitung (code, name, description)
- Formular-View für Leistungen (erforderlich für Zuordnung CI-Klassen; vgl. Kap. 8.8)
- Zugriff nur für **NT:ServiceMan Admin**
- Neue Leistungen können ergänzt, bestehende archiviert (active=False) werden

**Soft Delete (v0.9.4):** Leistungen werden nie physisch gelöscht, sondern nur „gelöscht markiert“ (active=False). Damit gilt:

| Kontext | Verhalten |
|---------|-----------|
| **Neue Prozesse** | Gelöscht markierte Leistungen sind nicht auswählbar (Verfügbarkeit 8.8, Produktmatrix 8.10, Vertragsmatrix 11.2) |
| **Bestehende Verträge** | Leistung bleibt in Vertrag und CIs erhalten – kein automatisches Entfernen (Verträge sind Vereinbarungen; Änderung bedarf Kundenabsprache bzw. interner Entscheidung) |
| **Anzeige in Bestand** | Optional: Bei Anzeige in Vertrag/CI dezent „(nicht mehr angeboten)“ anzeigen – rein informativ |

---

## 8.8 Matrix: Leistung × CI-Klasse (Verfügbarkeit) – v0.9.2

Es wird festgelegt, welche Leistung für welche Geräteklasse **grundsätzlich möglich** ist.
Diese Zuordnung ist unabhängig von Paketen und Preisen; sie definiert nur die technisch/fachliche Machbarkeit.

**Beispiel:** Für einen WLAN-AP (der über einen Controller gemanaged wird) ist „Konfig-Sicherung“ in der Regel nicht sinnvoll → nicht verfügbar.

**Technische Abbildung:**

- Modell `nt_serviceman.ci_class`: zusätzliches Feld `service_ids` (Many2many → `nt_serviceman.service`, relation optional benannt)
- Modell `nt_serviceman.service`: zusätzliches Feld `ci_class_ids` (Many2many → `nt_serviceman.ci_class`, gleiche Relation – inverse Sicht)
- Bedeutet: Pro CI-Klasse werden die **verfügbaren Leistungen** ausgewählt; pro Leistung die **CI-Klassen, für die sie verfügbar ist**
- Keine Zuordnung = Leistung ist für diese Geräteklasse **nicht verfügbar**

**Benutzerschnittstelle (bidirektional):**

- Im **CI-Klasse-Formular** (unter Konfiguration > CI-Klassen): Bereich „Verfügbare Leistungen" – welche Leistungen sind für diese Geräteklasse möglich?
- Im **Leistung-Formular** (unter Konfiguration > Leistungen): Bereich „Verfügbar für CI-Klassen" – für welche Geräteklassen ist diese Leistung verfügbar?
- Beide Sichten zeigen dieselbe Many2many-Relation; Änderungen an einer Seite wirken sofort auf die andere
- Darstellung: Liste/Checkboxen bzw. Auswahlliste; z.B. Firewall: alle sieben Leistungen; WLAN-AP: nur Dokumentation, Beratung, Update-Service (ohne CVE, Backup, 2nd Level)

**Alternativ (falls gewünscht):** Matrix-Ansicht unter Konfiguration: Geräteklassen als Zeilen, Leistungen als Spalten, Haken = verfügbar. Die konkrete Darstellung kann in der Implementierung gewählt werden.

**Regeln:**
- Die Matrix wird ausschließlich in Odoo gepflegt
- Änderungen haben keine Auswirkung auf bestehende CI; sie dienen der Konfiguration für künftige Zuordnungen und Vertriebslogik
- Ohne Eintrag in der Matrix gilt: Leistung für diese Geräteklasse nicht verfügbar
- **v0.9.4:** In der Verfügbarkeits-Auswahl (ci_class.service_ids) werden nur **aktive** Leistungen angezeigt und zuordenbar

---

## 8.9 Anzeige im Portal (nicht v1.0)

*Siehe [FEATURE-LIST.md](FEATURE-LIST.md) – wird bei geplanter Umsetzung hier ausformuliert.*

- **Primär sichtbar:** CI-Klasse
- **Device Role** nur als Detailinformation

---

## 8.10 Leistungsmatrix am Produkt (Vorbefüllung) – v0.9.4

Für wiederkehrende Produkte (`product.template` mit `detailed_type = "recurrent"`) kann eine **Leistungsmatrix** am Produkt definiert und vorbelegt werden. Diese Vorbefüllung übernimmt dieselbe Struktur wie die Vertrags-Leistungsmatrix (Kap. 11.2) und wird beim Erstellen des Vertrags aus der Angebotszeile in den Vertrag übertragen.

**Fachlicher Use Case:** Unterschiedliche Produktvarianten (z.B. „NT/Care Basis“ vs. „NT/Care Premium“) können unterschiedliche Leistungsbündel vorbelegen. Das Produkt definiert damit, welche Leistungen pro CI-Klasse in Verträgen dieses Typs buchbar sind.

**Modell:** `nt_serviceman.product_ci_class_matrix_line`

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| product_tmpl_id | Many2one | product.template (required, ondelete=cascade) |
| ci_class_id | Many2one | nt_serviceman.ci_class |
| quantity | Integer | default 0, ≥ 0 (Standardmenge pro CI-Klasse) |
| service_ids | Many2many | nt_serviceman.service – Leistungen, die für diese Klasse gebucht werden können |

**Constraints:**
- `UNIQUE(product_tmpl_id, ci_class_id)` – pro Produkt jede CI-Klasse nur einmal
- `service_ids` dürfen nur Leistungen enthalten, die in `ci_class_id.service_ids` (Kap. 8.8) stehen

**Erweiterung product.template:**
- Feld `ci_class_matrix_line_ids` (One2many → nt_serviceman.product_ci_class_matrix_line, inverse_name=product_tmpl_id)
- **Sichtbarkeit:** Tab/Bereich „Leistungsmatrix“ nur anzeigen, wenn `detailed_type == "recurrent"` (attrs/invisible)

**Benutzerschnittstelle:**
- Tab oder Bereich **„Leistungsmatrix“** im Produktformular (Artikel/Varianten)
- Matrix-Struktur analog zu Kap. 11.2: Zeilen = CI-Klassen, Spalten = Menge + Leistungen (Checkboxen)
- Zugriff nur bei Produkttyp „Wiederkehrend“
- Ohne Einträge am Produkt: Vertrag startet wie bisher mit leeren Matrix-Zeilen (Kap. 11.2, action_init_ci_class_matrix_lines)

**Leistung „gelöscht markiert“ (v0.9.4):** Enthält die Produktmatrix eine Leistung, die active=False ist (Kap. 8.7), wird diese mit einer Markierung angezeigt (z.B. „… nicht mehr angeboten“). Der Nutzer kann die Leistung aus der Matrix entfernen; eine einfache Möglichkeit dazu ist bereitzustellen.

**Übertragung in Vertrag:** Bei `_prepare_contract_values()` werden **nur aktive Leistungen** in die Vertragswerte übernommen. Enthält die Produktmatrix noch „gelöscht markierte“ Leistungen (weil nicht bereinigt), werden diese nicht an neue Verträge weitergegeben – auch nicht bei duplizierten Angeboten.

**Vorbild:** `contingent_ids` – wird am Produkt in intero_net gepflegt und in `_prepare_contract_values()` per Command in die Vertragswerte übernommen.

---

## 8.11 Service-Voraussetzungen aus NetBox (v0.9.11)

**Kontext:** NT:ServiceMan soll die Automatisierung der definierten Leistungen vorbereiten und später initialisieren. Die Leistungen werden im Wesentlichen mit Daten aus NetBox gesteuert. Damit eine Leistung (z. B. OpenCVE-Service, Konfig-Backup) erbracht werden kann, müssen bestimmte NetBox-Felder am CI ausgefüllt sein – z. B. Hersteller, Gerätebezeichnung oder Geräteklasse, damit externe Werkzeuge die Abfrage eingrenzen können.

**Ziel:** Der Benutzer definiert pro Leistung, welche NetBox-Felder erforderlich sind. Das System prüft die Vollständigkeit am CI und signalisiert fehlende Felder – im Vertrag, am CI und mit Verweis auf die Nachpflege in NetBox.

Die Umsetzung erfolgt in **drei aufeinander aufbauenden Teilen**, die nacheinander angegangen werden:

### 8.11.1 Teil 1: Feldliste pro Leistung (Konfiguration)

**Anforderung:** Zu jeder Leistung existiert eine Liste der aus NetBox bereitgestellten Felder. Der Benutzer markiert per Häkchen: *Dieses Feld muss für die aktuell ausgewählte Leistung ausgefüllt sein.*

**Methode zur Ermittlung der Feldstruktur:** NetBox-Schema-API (Option B) – keine halben Sachen. Der Katalog der verfügbaren Felder wird aus dem offiziellen OpenAPI-Schema von NetBox abgeleitet, nicht aus einem Beispiel-CI.

**Teilschritte (Reihenfolge):**

#### 8.11.1a Teilschritt: Device-Struktur ermitteln und anzeigen

**Ziel:** Die Struktur eines NetBox-Devices aus dem Schema ermitteln und als einfache Liste darstellen.

**Technik:**
- Endpoint: `GET /api/schema/` – NetBox liefert das OpenAPI-Schema (JSON)
- Device-Modell: Schema für `/api/dcim/devices/` auswerten, alle Felder (inkl. Pfade für verschachtelte Objekte wie `device_type.manufacturer`) extrahieren
- **Hinweis:** Schema-Abruf kann langsam sein (NetBox: 7–8 s); ggf. cachen
- **Darstellung:** Im Leistung-Formular (Konfiguration > Leistungen), unter dem Bereich „Verfügbare CI-Klassen“, ein neuer Bereich „NetBox-Device-Felder“ mit einer einfachen Liste der Feldnamen (noch ohne Häkchen)

**Abnahme:** Beim Öffnen einer Leistung werden die ermittelten NetBox-Device-Felder als Liste angezeigt.

#### 8.11.1b Teilschritt: Häkchen „erforderlich“ pro Feld (folgt auf 8.11.1a)

**Ziel:** Pro Feld ein Häkchen „Für diese Leistung erforderlich“. Auswahl wird gespeichert.

**Technik:**
- Pro Leistung: Many2many oder Relationstabelle zu den erforderlichen Feldern
- Benutzerschnittstelle: Checkboxen in der Feldliste (8.11.1a)

**Abnahme:** Pro Leistung können erforderliche Felder per Häkchen markiert und gespeichert werden.

---

**Beispiel (nach 8.11.1b):** Leistung „Proaktiver Sicherheits-Service (CVE)“ – erforderlich: Hersteller (device_type.manufacturer), Gerätebezeichnung/Modell (device_type), ggf. weitere Felder je nach Abfrage-Logik des CVE-Werkzeugs

---

### 8.11.2 Teil 2: Indikator in Verträgen (Grün/Rot)

**Anforderung:** Wird ein CI einem Vertrag zugeordnet (CMDB-Tab, Wizard „CI zuordnen“), soll optisch erkennbar sein:
- **Grün:** Für alle gebuchten Leistungen sind die erforderlichen Felder vorhanden und ausgefüllt
- **Rot:** Mindestens ein Feld für mindestens eine gebuchte Leistung fehlt am CI

**Gewählte Darstellung (Option A – Icon-Spalte):**
- **Vollständig:** Grünes Häkchen (`fa-check-circle` + `text-success`)
- **Fehlende Felder:** Gelbes Dreieck mit Ausrufezeichen (`fa-exclamation-triangle` + `text-warning`)

**Weitere Optionen (nicht gewählt):**

| Option | Beschreibung | Vor-/Nachteile |
|--------|--------------|----------------|
| **A: Icon-Spalte** | Eigene Spalte mit farbigem Icon (z. B. ✓ / ⚠ oder fa-check-circle / fa-exclamation-circle) | Kompakt, eindeutig; benötigt eine Spalte Platz |
| **B: Badge/Text** | Kurzer Badge neben dem CI-Namen: „Vollständig“ (grün) oder „Fehlende Felder“ (rot) | Selbsterklärend; mehr Platzbedarf |
| **C: Zeilenfärbung** | Ganze Zeile grün oder rot hinterlegt (`decoration-success` / `decoration-danger`) | Sehr auffällig, schnell erfassbar; kann bei vielen CIs optisch überladen wirken |
| **D: Farbiger Punkt** | Kleiner farbiger Punkt/Circle in einer Spalte (über Icon oder Custom-CSS) | Sehr kompakt; weniger selbsterklärend |
| **E: Status-Spalte (Text)** | Eigene Spalte „Status“ mit Werten wie „OK“ / „Fehlende Felder“ | Explizit, barrierefreundlich; keine Farbsemantik nötig |
| **F: Kombination** | z. B. Icon + Tooltip mit Details („Leistung X: Feld Y fehlt“) | Höchste Informationsdichte; mehr Implementierungsaufwand |

**Betroffene Stellen:**
- **CMDB-Tab** (Vertragsformular): CI-Liste des Vertrags – hier ist der Indikator laut Anforderung zentral
- **Wizard „CI zuordnen“**: Optional; Nutzer könnte vor der Zuordnung sehen, welche CI bereits vollständig sind

**Technische Idee:**
- Beim CI-Abruf aus NetBox: Werte der erforderlichen Felder mitlesen und in Odoo halten (oder bei jedem Abruf prüfen)
- Berechnung: Pro CI, pro gebuchter Leistung prüfen, ob alle erforderlichen Felder gefüllt sind
- Darstellung: Icon-Spalte am CI – grünes Häkchen (vollständig) / gelbes Dreieck (fehlende Felder)

**Abnahme:** In der CI-Liste des Vertrags ist bei jedem CI der Status (vollständig/unvollständig) sichtbar.

---

### 8.11.3 Teil 3: Hinweise im CI-Formular

**Anforderung:** Im CI-Formular soll klar benannt werden: *Leistung X: fehlende Felder [Liste]*. Der Nutzer trägt die Felder in NetBox nach – der Link zum CI in NetBox ist vorhanden und führt direkt dorthin.

**Technische Idee:**
- Bereich „Service-Voraussetzungen“ oder „Fehlende Felder“ im CI-Formular
- Pro gebuchter Leistung: wenn Felder fehlen → Liste der fehlenden Felder anzeigen
- Link zu NetBox (netbox_url) prominent – Nutzer öffnet NetBox und pflegt dort nach
- Nach NetBox-Aktualisierung: Button „Hole von NetBox“ am CI → erneuter Abruf, Status aktualisiert sich

**Abnahme:** Im CI-Formular sind fehlende Felder pro Leistung benannt; NetBox-Link ist verfügbar.

---

**Reihenfolge:** Teil 1 → Teil 2 → Teil 3 (jeweils baut auf dem Vorherigen auf).

---

## 9. REST-Integration NetBox → Odoo

### 9.1 Auslöser (v0.9)

- Manuell durch Benutzeraktion: Button **„Hole von NetBox“**
- Bedienbar für **NT:ServiceMan Admin** und **NT:ServiceMan Nutzer**
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

### 11.1 CMDB-Tab Wiederverwendung (v0.9.1)

**Abhängigkeit:** NT:ServiceMan hängt von `intero_net` ab (Modell `contract.recurrent`).

Der bestehende **CMDB-Tab** am Vertragsformular (`contract.recurrent`) wird wiederverwendet und mit der CI-Verlinkung belegt.

**Vorgehen:**
- Der Tab „CMDB“ bleibt erhalten.
- Die bisherige Tabelle (cmdb.line) wird durch die **CI-Liste** ersetzt.
- Die Anzeige zeigt die dem Vertrag zugeordneten Configuration Items.

**Das Feld CMDB-ID bleibt erhalten:**
- Das CI-Modell erhält ein optionales Feld `cmdb_id` (Integer) für Abwärtskompatibilität.
- Die Spalte CMDB-ID wird in der neuen CI-Tabelle im Vertrag angezeigt.

**Tab-Spalten (Mindestumfang):**
| Spalte | Beschreibung |
|--------|--------------|
| CMDB-ID | cmdb_id (optional, Legacy) |
| Name | CI-Name / Anzeigename |
| CI-Klasse | Firewall, Switch, Router, Access Point etc. |
| Device Role | NetBox Device Role |
| NetBox-Link | Klickbarer Link zum Gerät in NetBox |

**Zuordnungswege (beide möglich):**
1. **Im Vertrag:** Button „CI zuordnen“ im CMDB-Tab → Wizard zum Auswählen unzugeordneter CI; nach „Zuordnen“ schließt der Dialog automatisch.
2. **Im CI:** Feld „Vertrag“ (contract_id) setzen.

**Einschränkung CI-Zuordnung (v0.9.11):** Es dürfen nur CI zugeordnet werden, deren **CI-Klasse in der Leistungsmatrix** des Vertrags enthalten ist (Kap. 11.2). CI mit unbekannter oder nicht vorkommender CI-Klasse werden bei der Zuordnung ausgeschlossen. Gilt für Wizard „CI zuordnen“ und für direkte Zuordnung im CI-Formular.

**Hinweis zu bestehenden cmdb.line-Daten:** Die bisherige cmdb.line-Tabelle wird im Tab durch die CI-Liste ersetzt. Bestehende cmdb.line-Einträge bleiben in der Datenbank erhalten; eine spätere Migration in CI (inkl. cmdb_id) kann separat geplant werden.

**Ausblick Partner/Kunde:** Eine kaufmännische Zuordnung (z.B. partner_id) am CI ist für v0.9 nicht vorgesehen. Dies kann später ergänzt werden, wenn die NetBox-Felder (z.B. Tenant, Kundennummer) genauer betrachtet wurden.

### 11.2 Leistungsmatrix am Vertrag (v0.9.3)

Im Vertragsformular wird eine **Matrix** eingeführt, die pro Vertrag festlegt (v0.9.4: kann aus dem Produkt vorbelegt werden, vgl. Kap. 11.4):
- welche Leistungen für welche CI-Klasse **gebucht werden können** (Checkbox = „kann gebucht werden")
- welche **Menge** pro CI-Klasse vorgesehen ist (Ganzzahl ≥ 0)

**Darstellung:**

| CI-Klasse   | Menge | Dienstleistung 1 | Dienstleistung 2 | … |
|-------------|:-----:|:----------------:|:----------------:|:-:|
| Firewall    |  5    | ☐                | ☐                | … |
| Switch      |  3    | ☐                | ☐                | … |
| Access Point| 12    | ☐                | —                | … |

- **Zeilen:** CI-Klassen (aktive Geräteklassen)
- **Spalte Menge:** Ganzzahl ≥ 0 (Anzahl Geräte dieser Klasse im Vertrag)
- **Checkbox-Spalten:** Eine pro Leistung; unbeschriftete Checkbox = diese Leistung kann für diese Klasse gebucht werden
- **Leere Zelle (—):** Kein Feld, wenn die Leistung für diese CI-Klasse global nicht verfügbar ist (Konfiguration Kap. 8.8)

**Datenmodell:**

- Modell `nt_serviceman.contract_ci_class_matrix_line`:
  - `contract_id` (Many2one → contract.recurrent)
  - `ci_class_id` (Many2one → nt_serviceman.ci_class)
  - `quantity` (Integer, default 0, ≥ 0)
  - `service_ids` (Many2many → nt_serviceman.service) – Leistungen, die für diese Klasse gebucht werden können

- Einschränkung: `service_ids` dürfen nur Leistungen enthalten, die in `ci_class_id.service_ids` (Kap. 8.8) stehen.
- **v0.9.4:** In der Vertragsmatrix werden nur **aktive** Leistungen (active=True) auswählbar angezeigt; gelöscht markierte bleiben in bestehenden Verträgen erhalten, sind aber für neue Auswahlen nicht mehr verfügbar.

**Benutzerschnittstelle:**

- Neuer Tab **„Leistungsmatrix"** im Vertragsformular
- Matrix als Tabelle: Zeilen = CI-Klassen, Spalten = Menge + Leistungen
- Checkboxen und Mengen direkt editierbar
- Nur sichtbar, wenn Vertrag nicht im Status „Verkauf" (analog CMDB-Tab)

### 11.3 Gebuchte Leistungen am CI (Kopie) – v0.9.3 / v0.9.11

**Kontext:** Die Verkettung Vertrag → Leistungsmatrix (CI-Klasse + gebuchte Leistungen) → CI (mit CI-Klasse) bedeutet: Zu jedem CI, das einem Vertrag zugeordnet ist, gehören die **gebuchten Leistungen** – die für seine CI-Klasse im Vertrag vereinbarten Leistungen.

**Anforderung:** Sobald ein CI einem Vertrag zugeordnet wird (`contract_id` gesetzt), werden die gebuchten Leistungen aus der Vertrags-Leistungsmatrix auf das CI übernommen – als **Kopie**, nicht als Verlinkung.

**Zweck:** Eine Kopie am CI ermöglicht Filter, Sortierung und Gruppierung in Listen und Berichten direkt am CI. Eine Verlinkung würde diese Nutzung erschweren. Der Nachteil: Änderungen an der Leistungsmatrix des Vertrags werden nicht automatisch ans CI weitergereicht; ein Update erfordert ggf. manuelle Nachpflege oder einen Aktualisierungs-Button (spätere Erweiterung).

**Technische Abbildung:**

- Modell `nt_serviceman.configuration_item`: Feld `contract_service_ids` (Many2many → `nt_serviceman.service`, eigene Relation)
- **Trigger:** Beim Setzen oder Ändern von `contract_id` (einschl. Zuordnung über Wizard „CI zuordnen") wird die passende Zeile der Leistungsmatrix des Vertrags ermittelt (über `ci_class_id` des CI) und deren `service_ids` in `contract_service_ids` am CI kopiert
- **Kein Vertrag:** Ist `contract_id` leer, bleibt `contract_service_ids` leer; der Bereich „Gebuchte Leistungen" wird nicht angezeigt
- **Keine passende Matrix-Zeile:** Existiert für die CI-Klasse des CI keine Zeile in der Vertrags-Leistungsmatrix, bleibt `contract_service_ids` leer

**Darstellung im CI-Formular (v0.9.11):**

- Bereich **„Gebuchte Leistungen"** nur sichtbar, wenn ein Vertrag zugeordnet ist
- Anzeige als **read-only Punkt-Liste** (nur Bezeichnungen, ohne Beschreibungen)

### 11.4 Übertragung Leistungsmatrix: Produkt → Vertrag (v0.9.4)

**Kontext:** Bei wiederkehrenden Produkten wird der Vertrag in der Angebotszeile bereits beim Hinzufügen des Produkts erstellt (intero_net: `sale.order.line` → `_onchange_create_services` ruft `product._prepare_contract_values()` auf). Analog zu `contingent_ids` und `term` soll die Leistungsmatrix vom Produkt in den Vertrag übernommen werden.

**Datenfluss:**

| Phase | Wo definiert? | Übertragung |
|-------|----------------|-------------|
| Produktdefinition | product.template (ci_class_matrix_line_ids) | – |
| Angebot | Vertrag wird erstellt (onchange) | Produkt → Vertrag bei Erstellung |
| Vertrag | contract.recurrent | Matrix bei create() übergeben |

**Schritt 1 – Produkttemplate (Kap. 8.10):**
- Modell `product_ci_class_matrix_line`, Feld `ci_class_matrix_line_ids` am product.template
- Matrix am Produkt pflegen (nur bei `detailed_type = "recurrent"`)

**Schritt 2 – Verhalten in der Angebotszeile:**
- NT:ServiceMan erbt `product.product` und erweitert `_prepare_contract_values()`
- Wenn `product.detailed_type == "recurrent"` und das Produkttemplate Matrix-Zeilen hat: `ci_class_matrix_line_ids` als Command-Liste in die contract_values aufnehmen (analog `contingent_ids`)
- `contract.recurrent.create()` erhält die Matrix-Werte; `action_init_ci_class_matrix_lines()` nur für fehlende CI-Klassen ergänzen (bestehende Zeilen nicht überschreiben)
- Vertrag ist damit beim ersten Anzeigen bereits mit der Produkt-Matrix vorbelegt; Anpassung im Vertrag weiterhin möglich

**Regeln:**
- Keine Matrix am Produkt → Vertrag startet wie bisher mit leeren Zeilen (nur action_init_ci_class_matrix_lines)
- Matrix am Produkt vorhanden → Vertrag erhält die vordefinierten Werte; Nutzer kann im Vertrag anpassen (Mengen, Leistungs-Checkboxen)
- Der Übergang erfolgt zum Zeitpunkt der Vertragserstellung (Produkthinzufügen in der Angebotszeile)
- Bei der Übertragung werden nur **aktive** Leistungen übernommen (Kap. 8.7, 8.10)

**Duplizierte Angebote:** Beim Duplizieren eines Angebots werden neue Verträge aus den aktuellen Produktdefinitionen erzeugt. Enthält ein Produkt noch „gelöscht markierte“ Leistungen in seiner Matrix, werden diese nicht in die neuen Verträge übernommen. Optional: Hinweis beim Öffnen eines duplizierten Angebots, wenn Produkte Matrix-Einträge mit nicht mehr angebotenen Leistungen enthalten.

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

**Erweiterung v0.9.2:** Einführung einer editierbaren Leistungsliste (Services) und einer Matrix, die festlegt, welche Leistung für welche Geräteklasse grundsätzlich verfügbar ist. Basis für spätere Paketlogik und Vertriebsberechnung.

**Erweiterung v0.9.4:** Leistungsmatrix am Produkt – wiederkehrende Produkte können eine Matrix (CI-Klasse × Menge × Leistungen) vordefinieren; beim Hinzufügen des Produkts in eine Angebotszeile wird die Matrix in den erzeugten Vertrag übernommen (analog contingent_ids, term). Umsetzung Schritt 1: Produkttemplate; Schritt 2: Verhalten in der Angebotszeile.

**Ergänzung v0.9.4 – Soft Delete bei Leistungen:** Leistungen werden nie physisch gelöscht, nur „gelöscht markiert“ (active=False). Gelöscht markierte sind aus neuen Prozessen (Verfügbarkeit, Produktmatrix, Vertragsmatrix) ausgeschlossen, bleiben in bestehenden Verträgen erhalten. In der Produktmatrix: Markierung für nicht mehr angebotene Leistungen, einfaches Entfernen; bei Vertragsübertragung werden nur aktive Leistungen übernommen (auch bei duplizierten Angeboten).

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
| 12 | **CI-Klasse** (Kap. 8.4) | Modell nt_serviceman.ci_class, Firewall/Switch/Router/Access Point vordefiniert |
| 13 | **Vertragskopplung** (Kap. 11.1) | CMDB-Tab mit CI-Liste; cmdb_id, contract_id am CI; Wizard „CI zuordnen“; Zuordnung auch im CI-Formular |
| 14 | **NetBox Device Roles** (Kap. 8.5) | Modell nt_serviceman.netbox_device_role; Abruf aus /api/dcim/device-roles/; Upsert-Logik mit netbox_created/netbox_last_updated; Sync-Regeln (NetBox jünger → Update) |
| 15 | **Mapping Device Role ↔ CI-Klasse** (Kap. 8.6) | ci_class_id am netbox_device_role (Many2one); Zuordnung in Device-Roles-Liste und CI-Klasse-Formular; Wizard „Device Roles zuordnen“ |
| 16 | **CI netbox_role_id** (Kap. 8.1) | Many2one auf netbox_device_role; netbox_role_name entfällt; ci_class_id über Relation |
| 17 | **Device Roles von NetBox abrufen** | Menüpunkt unter Konfiguration; Button im Config-Formular; Auto-Refresh: Liste wird nach Abruf angezeigt |
| 18 | **Leistungen** (Kap. 8.7) | Modell service, Liste mit 7 Vorbefüllungen, Menü Konfiguration > Leistungen | v0.9.2 |
| 19 | **Matrix Leistung × CI-Klasse** (Kap. 8.8) | service_ids an CI-Klasse, Bereich „Verfügbare Leistungen" – im Formular | v0.9.2 |
| 20 | **Leistung ↔ CI-Klasse bidirektional** (Kap. 8.8) | ci_class_ids am service; Bereich „Verfügbar für CI-Klassen" im Leistung-Formular | v0.9.2 |
| 21 | **Soft Delete Leistungen** (Kap. 8.7) | unlink() verhindert physisches Löschen; domain active=True in 8.8, 8.10, 11.2; Archivieren + Filter „Archivierte einblenden"; tree delete="false" | v0.9.4 |
| 22 | **Leistungsmatrix am Produkt** (Kap. 8.10) | Modell product_ci_class_matrix_line, Feld ci_class_matrix_line_ids am product.template; Tab „Leistungsmatrix" nur bei detailed_type=recurrent; action_init_ci_class_matrix_lines | v0.9.4 |
| 23 | **Leistungsmatrix am Vertrag** (Kap. 11.2) | Tab „Leistungsmatrix" im Vertragsformular; Sichtbarkeit auch bei state=sale (Angebotsphase) | v0.9.3 |
| 24 | **Gebuchte Leistungen am CI** (Kap. 11.3) | contract_service_ids am configuration_item; _sync_contract_service_ids bei contract_id-Änderung; Kopie aus Vertrags-Leistungsmatrix; Anzeige als read-only Punkt-Liste | v0.9.3 / v0.9.11 |
| 25 | **Übertragung Produkt → Vertrag** (Kap. 11.4) | _prepare_contract_values erweitert, _prepare_contract_ci_class_matrix_values; Matrix bei Vertragserstellung aus Angebotszeile übernommen; nur aktive Leistungen | v0.9.4 |
| 26 | **Planpositionen** (Kap. 2.2, 4.2, 11) | Geräteklasse + Planmenge über Leistungsmatrix (ci_class_id + quantity); am Produkt, Vertrag und via Angebot; Zeilen = Planpositionen | v0.9.4 |
| 27 | **Menü Konfiguration** | Untermenü „Daten" entfernt; CI-Klassen, Device Roles, „Device Roles von NetBox abrufen" komplett nach Konfiguration verschoben; nur NT:ServiceMan Admin | v0.9.9 |
| 28 | **Config in ir.config_parameter** (Kap. 7.2) | NetBox-URL und API-Token in ir.config_parameter; Einstellungsformular unverändert; Lesestellen angepasst; keine Migration (Werte neu eingeben) | v0.9.10 |
| 29 | **Markierung „nicht mehr angeboten"** (Kap. 8.10) | Banner + graue Tags für archivierte Leistungen in Produkt- und Vertragsmatrix; color-Feld am Service; decoration-muted auf Zeilen mit Archiv-Leistungen | v0.9.10 |

| 30 | **Ist-Menge** (Plan/Ist) | actual_quantity an contract_ci_class_matrix_line; berechnet aus Anzahl CI je CI-Klasse im CMDB-Tab | v0.9.11 |
| 31 | **CI-Zuordnung nur Matrix-CI-Klassen** (Kap. 11.1) | Nur CI zuordenbar, deren CI-Klasse in der Leistungsmatrix vorkommt; Wizard Domain + Validierung; Constraint am CI | v0.9.11 |
| 32 | **Gebuchte Leistungen am CI – Darstellung** (Kap. 11.3) | „Buchbar"→„Gebucht"; nur bei Vertrag sichtbar; read-only Punkt-Liste mit Bezeichnungen | v0.9.11 |
| 33 | **Archivierte Leistungen am CI** (Kap. 11.3) | contract_service_ids inkl. archivierter Leistungen; separate Liste „Nicht mehr angeboten" im CI-Formular | v0.9.11 |
| 34 | **Plan/Ist-Mengenabweichung** (Kap. 4.9) | quantity_deviation in Leistungsmatrix; Filter „Plan-Ist-Abweichung" in Vertragsliste | v0.9.11 |
| 35 | **Service-Voraussetzungen aus NetBox** (Kap. 8.11) | (1) Feldliste pro Leistung mit Häkchen, custom_fields expandiert; (2) Grün/Gelb-Indikator im CMDB-Tab; (3) Fehlende Felder im CI-Formular + NetBox-Link; Sync bei Matrix-Änderung | v0.9.11 |
| 36 | **Chatter sichtbar** (Bug) | Chatter-Darstellung in Formularen (Leistungen, CI-Klassen, CIs): Felder in oe_chatter mit Widgets mail_followers/mail_thread | v0.9.11 |
| 37 | **Anzeige „Tenant" → „Partner"** (Kap. 8.1) | Feld-Label netbox_tenant_name von „Tenant" auf „Partner" geändert; Verknüpfung CI–Partner zurückgestellt (Kundennummer in NetBox nicht hinterlegt) | v0.9.11 |
| 38 | **Vertrags-Filter: Plan-Ist + Service-Felder** | Filter umbenannt: „Plan-Ist-Abweichung"; neu: „Abweichung Service-Felder" + Gruppierung nach beiden | v0.9.11 |
| 39 | **Filter und Gruppierungen** | Erweiterte Filter und Gruppierungen in CI-, Vertrags- und Service-Listen | v1.0 |

### Status NetBox (bereits vorhanden)

**Bereits vorhanden:**
- NetBox-Schnittstelle: manueller Abruf pro CI (Button „Hole von NetBox“)
- REST-API-Anbindung, Felderübernahme (Name, Rolle, Tenant, Serial, Hardware-Typ, …)
- CI-Anlage mit NetBox-ID; Device-Role-Mapping → CI-Klasse

**Weitere NetBox-Ideen:** siehe [FEATURE-LIST.md](FEATURE-LIST.md)

### Lösungsvorschlag: CI-Zuordnung nur für Matrix-CI-Klassen (umgesetzt v0.9.11)

**Ziel:** Pro Vertrag dürfen nur CI zugeordnet werden, deren CI-Klasse in der Leistungsmatrix des Vertrags enthalten ist.

**Betroffene Stellen:**
1. **Wizard „CI zuordnen"** (`nt_serviceman.contract_configuration_item_assign`)
2. **Direkte Zuordnung im CI-Formular** (`configuration_item.contract_id`)

**Vorgehen:**

| Maßnahme | Ort | Beschreibung |
|----------|-----|--------------|
| **1. Domain im Wizard** | `contract_configuration_item_assign.py` | Feld `configuration_item_ids`: zusätzlich `('ci_class_id', 'in', erlaubte_ci_class_ids)`. Erlaubte Klassen = `contract_id.ci_class_matrix_line_ids.mapped('ci_class_id')`. Domain dynamisch via computed Feld `allowed_ci_class_ids` oder im `domain` des Many2many. |
| **2. Validierung im Wizard** | `action_assign()` | Vor dem `write`: Prüfen, dass alle ausgewählten CI eine `ci_class_id` haben, die in der Matrix vorkommt. Bei Verstoß `ValidationError` mit klarer Meldung (z. B. „Das CI ‚xyz‘ hat die CI-Klasse ‚Server‘, die in der Leistungsmatrix dieses Vertrags nicht vorkommt."). |
| **3. Constraint am CI** | `configuration_item.py` | `@api.constrains('contract_id', 'ci_class_id')`: Beim Setzen von `contract_id` prüfen, dass `ci_class_id` in `contract.ci_class_matrix_line_ids.ci_class_id` enthalten ist. Falls `ci_class_id` leer (kein Mapping), Zuordnung verbieten. |

**Randfälle:**
- **Vertrag ohne Matrix-Zeilen:** Keine CI zuordenbar (korrekt).
- **CI ohne CI-Klasse (ci_class_id leer):** Nicht zuordenbar (kein Mapping Device Role → CI-Klasse).
- **Bestehende Zuordnungen:** Bereits zugeordnete CI mit „fremder" CI-Klasse bleiben bestehen; Constraint verhindert nur neue Zuordnungen. Optional: manuelle Bereinigung oder Migrations-Hinweis.

**Nächste Ideen:** siehe [FEATURE-LIST.md](FEATURE-LIST.md).
