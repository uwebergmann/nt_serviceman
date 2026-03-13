# Feature-Liste NT:ServiceMan

Mögliche Erweiterungen und Ideen – **außerhalb des Pflichtenhefts** gepflegt.  
Neue Ideen werden hier gesammelt; bei geplanter Umsetzung wird Punkt für Punkt ins Pflichtenheft übernommen.

---

## Übersicht

| # | Feature | Aufwand | Priorität |
|---|---------|---------|-----------|
| ~~1~~ | ~~Plan/Ist-Benachrichtigung~~ | – | **Erledigt** – Filter „Plan-Ist-Abweichung“ reicht für Verträge mit Abweichungen |
| ~~2~~ | ~~Portal~~ | – | **Ausgelagert** – eigenes Projekt, siehe übergeordnete Projektliste |
| ~~3~~ | ~~NetBox Initial-Import~~ | ~~1–2 Tage~~ | **Erledigt** – Kap. 9.4 (Alle CI holen, Vollabgleich, Delta-Sync) |
| ~~4~~ | ~~NetBox Update bei Änderungen~~ | ~~2–5 Tage~~ | **Erledigt** – Cron-Struktur (ir.cron Vollabgleich täglich, Kap. 9.5) |

---

## Detailbeschreibungen

### 1. Plan/Ist – Erledigt

Der Filter „Plan-Ist-Abweichung“ in der Vertragsliste ermöglicht die Übersicht über Verträge mit Mengenabweichungen. Zusätzliche Chatter-Benachrichtigungen werden nicht benötigt.

---

### 2. Portal – Ausgelagert

Portal-Entwicklung ist eigenes Projekt mit deutlich erweitertem Umfang. Siehe übergeordnete Projektliste (z.B. `../PROJEKTLISTE.md` oder Workspace-Root).

---

### 3. NetBox Initial-Import ✅ (erledigt v1.1)

**Umsetzung:** Pflichtenheft Kap. 9.4 – „Alle CI holen“ und „Vollabgleich“ im Config-Formular. Delta-Sync mit `last_updated__gte` für schnellere Folgesyncs.

---

### 4. NetBox Update bei Änderungen ✅ (erledigt)

**Umsetzung:** Cron-Struktur gemäß Kap. 9.5 – ir.cron für täglichen Vollabgleich (NT:ServiceMan – Vollabgleich NetBox CI). Button „Vollabgleich“ und Cron nutzen dieselbe Sync-Funktion. In Stage nicht testbar; Struktur ist vorhanden.

---

## Kontext NetBox (bereits vorhanden)

- NetBox-Schnittstelle: manueller Abruf pro CI (Button „Hole von NetBox“)
- **Alle CI holen** und **Vollabgleich** (Kap. 9.4): alle Devices von `/api/dcim/devices/`, Delta-Sync, Archivierung
- REST-API-Anbindung, Felderübernahme (Name, Rolle, Tenant, Serial, Hardware-Typ, …)
- CI-Anlage mit NetBox-ID; Device-Role-Mapping → CI-Klasse
