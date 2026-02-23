# Pflichtenheft  
## NT:ServiceMan v0.9 – CI-Abbildung in Odoo mit NetBox-REST-Anbindung

**Projekt:** NT:ServiceMan  
**Version:** 0.9 (Startversion)  
**Status:** Pflichtenheft  
**Ziel:** Startfähigkeit herstellen  
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
- eigenes konfigurierbares Modell **„CI-Klasse“**
- frei anlegbar
- aktiv/inaktiv schaltbar

Für den Start werden vordefiniert:
- FW (Firewall)
- SW (Switch)
- RTR (Router)
- AP (Access Point)

Keine Server-, Storage- oder generischen IT-Klassen.

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

| Feld           | Typ    | Beschreibung                                      |
|----------------|--------|---------------------------------------------------|
| **NetBox-URL** | Text   | Basis-URL der NetBox-Instanz (z.B. https://netbox.example.com) |

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

| Feld | Typ | Herkunft | Beschreibung |
|----|----|--------|-------------|
| netbox_id | Integer / Char | manuell | ID des Devices in NetBox |
| netbox_name | Char | NetBox | Name des Geräts |
| netbox_role_name | Char | NetBox | Rolle des Geräts |
| netbox_tenant_name | Char | NetBox | Tenant / Kunde |
| netbox_url | Char | NetBox | Link zum Objekt |
| netbox_last_sync | Datetime | System | Zeitpunkt letzter Abruf |
| netbox_sync_state | Selection | System | ok / failed |
| netbox_sync_error | Text | System | Fehlermeldung |

### 8.2 Feldregeln

- `netbox_id` ist editierbar
- alle anderen `netbox_*` Felder sind readonly
- Service-Felder sind in v0.9 nicht Bestandteil

### 8.3 CI-Klassen (Geräteklassen)

Vgl. Abschnitt 2.3. Konfigurierbares Modell „CI-Klasse“ mit vordefinierten Werten 
FW, SW, RTR, AP für den Start. Frei anlegbar, aktiv/inaktiv schaltbar.

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

| NetBox-Feld | Odoo-Feld |
|-----------|----------|
| id | netbox_id |
| name | netbox_name |
| role.name | netbox_role_name |
| tenant.name | netbox_tenant_name |
| display_url / url | netbox_url |

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
- CI werden im Vertrag tabellarisch angezeigt (Name, Rolle, Tenant).

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
