# Feature-Liste NT:ServiceMan

Mögliche Erweiterungen und Ideen – **außerhalb des Pflichtenhefts** gepflegt.  
Neue Ideen werden hier gesammelt; bei geplanter Umsetzung wird Punkt für Punkt ins Pflichtenheft übernommen.

---

## Übersicht

| # | Feature | Aufwand | Priorität |
|---|---------|---------|-----------|
| 1 | Plan/Ist-Benachrichtigung (Chatter) | – | Optional |
| 2 | Portal – CI-Klasse primär, Device Role als Detail | 4 h – 2 Tage | – |
| ~~3~~ | ~~NetBox Initial-Import~~ | ~~1–2 Tage~~ | **Erledigt** – Kap. 9.4 (Alle CI holen, Vollabgleich, Delta-Sync) |
| 4 | NetBox Update bei Änderungen | 2–5 Tage | – |

---

## Detailbeschreibungen

### 1. Plan/Ist-Benachrichtigung (Chatter)

Bei Abweichung zwischen Plan- und Ist-Menge (Vertrag/Leistungsmatrix): Hinweis an Vertrieb als Aktivität im Chatter. Der Filter „Plan-Ist-Abweichung“ in der Vertragsliste bietet bereits Transparenz; dieses Feature würde zusätzlich aktiv informieren.

---

### 2. Portal – CI-Klasse primär, Device Role als Detail

**Quelle:** Pflichtenheft Kap. 8.9

- **Primär sichtbar:** CI-Klasse
- **Device Role** nur als Detailinformation

**Technisch:** intero_net_portal zeigt aktuell keine CIs; Aufwand abhängig davon, ob nur View-Anpassung oder neues Portal-Feature nötig (4 h bis 2 Tage).

---

### 3. NetBox Initial-Import ✅ (erledigt v1.1)

**Umsetzung:** Pflichtenheft Kap. 9.4 – „Alle CI holen“ und „Vollabgleich“ im Config-Formular. Delta-Sync mit `last_updated__gte` für schnellere Folgesyncs.

---

### 4. NetBox Update bei Änderungen

**Quelle:** Pflichtenheft – Erledigte und offene Punkte

Mechanismus (Webhook oder periodischer Abgleich/Cron), der bei NetBox-Änderungen Odoo aktualisiert. Bei Änderung in NetBox → Update des betroffenen CI in Odoo.

**Aufwand:** 2–5 Tage

---

## Kontext NetBox (bereits vorhanden)

- NetBox-Schnittstelle: manueller Abruf pro CI (Button „Hole von NetBox“)
- **Alle CI holen** und **Vollabgleich** (Kap. 9.4): alle Devices von `/api/dcim/devices/`, Delta-Sync, Archivierung
- REST-API-Anbindung, Felderübernahme (Name, Rolle, Tenant, Serial, Hardware-Typ, …)
- CI-Anlage mit NetBox-ID; Device-Role-Mapping → CI-Klasse
