# NT:ServiceMan – Themenübersicht

Stand aus Pflichtenheft, Konzept und FEATURE-LIST (nur nt_serviceman).

---

## Erledigt (Kernfunktionen)

| Bereich | Thema |
|---------|-------|
| **NetBox** | Config (URL, Token, Test-URL), manueller Abruf pro CI („Hole NetBox-Item“), Alle CI holen, Vollabgleich, Delta-Sync, VM-Support |
| **NetBox** | Device Roles abrufen, Mapping Device Role ↔ CI-Klasse |
| **NetBox** | Felder: Hersteller, Modell, Hardware-Typ, Plattform, CPE; Roh-JSON für Debug (nur Admin); Cron Vollabgleich |
| **CI** | Anlage, Vertragszuordnung, Wizard „CI zuordnen“, Archivierung (active) |
| **CI-Klassen** | Modell, Firewall/Switch/Router/Access Point vordefiniert |
| **Leistungen** | Modell, Matrix Leistung × CI-Klasse, Soft Delete |
| **Leistungsmatrix** | Am Produkt (Vorbelegung), am Vertrag, Übertrag Produkt → Vertrag |
| **Vertrag** | Plan/Ist (Menge, Abweichung), gebuchte Leistungen am CI, Service-Voraussetzungen |
| **Vertrieb** | Leistungsmatrix in Angebotsphase – Vertrag vom Angebot aus erreichbar und bearbeitbar |

---

## Bewusst nicht umgesetzt / Ausgelagert

| Thema | Begründung |
|-------|------------|
| Tab „Leistungsmatrix“ auf Angebotsformular | Vertrag ist vom Angebot aus bereits erreichbar; Bearbeitung der Matrix am Vertrag ausreichend |
| Plan/Ist-Chatter-Benachrichtigung | Filter „Plan-Ist-Abweichung“ reicht – Verträge mit Abweichungen gut einsehbar |
| Portal | Eigenes Projekt mit erweitertem Umfang – siehe `projekte/PROJEKTLISTE.md` |

---

## Kurz: Aktueller Stand

- **NetBox-Integration:** Vollständig (manuell, Sync, Vollabgleich, Cron, VM)
- **Leistungsmatrix:** Produkt → Vertrag, Angebotsphase abgedeckt
- **Vertrag/CI:** Zuordnung, Plan/Ist (Filter), Service-Voraussetzungen
- **NT:ServiceMan:** Keine offenen Pflicht-Features
