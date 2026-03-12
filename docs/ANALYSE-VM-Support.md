# Analyse: Unterstützung von Virtual Machines (VMs) aus NetBox

**Ziel:** VMs als CI neben physischen Devices laden.  
**NetBox-Endpoint:** `/api/virtualization/virtual-machines/`  
**Status:** Teilweise umgesetzt (v1.2.3)

---

## Erledigt (v1.2.3)

| Punkt | Status |
|-------|--------|
| **netbox_source** (Selection device/vm) | ✓ |
| **netbox_platform** (statt netbox_firmware_version) | ✓ |
| **UNIQUE(netbox_source, netbox_id)** + Migration | ✓ |
| **_extract_netbox_fields** für Device und VM | ✓ |
| **_netbox_item_exists** (Device- und VM-URL) | ✓ |
| **action_fetch_from_netbox** – Pflicht netbox_id + netbox_source, Endpoint je nach Quelle | ✓ |
| **CI-Formular** – netbox_source rechts unter NetBox-Link, readonly nach Abruf | ✓ |
| **Button „Hole NetBox-Item“** – Voraussetzungen, Fehlermeldungen | ✓ |
| **Search-Filter** (Physisches Gerät / Virtuelle Maschine) | ✓ |
| **nt_cve-automatisation** – CPE aus netbox_platform | ✓ |
| **Config: Virtualization-API-Test** (Test-URL-Button) | ✓ |
| **Service-Voraussetzungen für VMs** (8.11.1c) | ✓ |
| **VM-Sync „Alle CI holen“** | ✓ |

---

## Offen (TODO)

| Nr | Aufgabe | Kurzbeschreibung |
|----|---------|------------------|
| 1 | **Tree-View** | Spalte `netbox_source` (optional) |
| 2 | **Dokumentation** | FEATURE-LIST: VM-Sync und VM-Support dokumentieren |

---

## 1. Empfehlung: Ein CI-Modell mit Typ-Diskriminator

**Kein separates VM-CI-Modell.** Stattdessen: bestehendes `nt_serviceman.configuration_item` um Feld `netbox_source` erweitern.

| Option | Beschreibung | Bewertung |
|--------|--------------|-----------|
| **A: Ein Modell** | `netbox_source` = 'device' \| 'vm'; ein Modell, eine Liste | ✓ Empfohlen |
| **B: Zwei Modelle** | `configuration_item_device`, `configuration_item_vm` | ✗ Doppelte Logik (Vertrag, Leistungen, CVE, Views) |
| **C: Vererbung** | abstraktes CI, Device-CI und VM-CI erben | ✗ Aufwand, wenig Mehrwert |

**Begründung für Ein Modell:**
- VMs und Devices sind beide CI für Verträge, Leistungen, CVE-Monitoring
- **Device Roles** werden in NetBox von beiden verwendet – das bestehende Mapping Role → CI-Klasse funktioniert
- Eine gemeinsame CI-Liste (filterbar nach Typ) ist für Nutzer übersichtlicher
- nt_cve-automatisation, Vertragszuordnung, Service-Voraussetzungen bleiben unverändert

---

## 2. NetBox VM vs Device – Datenstruktur und Feldstrategie

**Grundsatz:** Platform (dcim/platform) enthält die OS-/Software-Version bei Devices und VMs. Das Feld wird bei Devices oft nicht gepflegt, existiert aber. Custom Fields für Firmware werden **nicht** verwendet.

### 2.1 Zwei getrennte Felder für „Produkt“

| CI-Feld (Odoo) | Device | VM | Beschreibung |
|----------------|--------|-----|---------------|
| **netbox_model** | `device_type.model` | leer | Hardware-Modell (nur bei physischen Geräten) |
| **netbox_platform** | `platform.name` | `platform.name` | Software/OS (z.B. „FortiOS 7.2“, „Ubuntu 22.04“, „Windows Server“) |

- **netbox_model** = Hardware-Modell (FortiGate 100F, Juniper MX240)
- **netbox_platform** = Plattform/OS (FortiOS 7.2, Ubuntu 22.04) – bei beiden Objekttypen vorhanden

### 2.2 Vollständige Feldzuordnung

| CI-Feld (Odoo) | NetBox Device | NetBox Virtual Machine |
|----------------|---------------|------------------------|
| **display** | `device.display` | `vm.name` oder `vm.display` |
| **display_url** | `device.display_url` | `vm.display_url` |
| **serial** | `device.serial` | `vm.serial` |
| **netbox_device_type** | `device_type.model` bzw. `display` | **leer** (VMs haben kein device_type) |
| **netbox_manufacturer** | `device_type.manufacturer.name` | `platform.manufacturer.name` (falls platform) |
| **netbox_model** | `device_type.model` | **leer** |
| **netbox_platform** | `platform.name` | `platform.name` |
| **role** | `role` | `role` (gleiche device_role) |
| **tenant** | `tenant` | `tenant` |
| **created / last_updated** | gleich | gleich |

**NetBox Platform:** Hat `name`, optional `manufacturer`. Wird für Devices und VMs zur Abbildung von OS/Software genutzt. Das Feld ist bei Devices oft vorhanden, wird aber nicht immer gepflegt.

---

## 3. Technische Änderungen

### 3.1 Neues Feld am CI

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| **netbox_source** | Selection `[('device','Device'),('vm','Virtuelle Maschine')]` | Herkunft: DCIM Device oder Virtualization VM. Default `device` für Abwärtskompatibilität. |

### 3.2 Constraint-Anpassung

**Problem:** Device ID 1 und VM ID 1 sind unterschiedliche Objekte in NetBox, aber `netbox_id` wäre beide Male `1`. Aktuell: `UNIQUE(netbox_id)` → Konflikt.

**Lösung:** `UNIQUE(netbox_source, netbox_id)` (zusammengesetzter UNIQUE-Constraint).

### 3.3 netbox_id Constraint (Ziffern)

Für VMs: `netbox_id` ist ebenfalls numerisch. Bestehende Prüfung „nur Ziffern“ bleibt gültig.

---

## 4. Betroffene Dateien und Änderungen

### 4.1 `models/configuration_item.py`

| Änderung | Details |
|----------|---------|
| Neues Feld | `netbox_source = fields.Selection([('device','Device'),('vm','Virtuelle Maschine')], default='device')` |
| SQL-Constraint | `netbox_id_unique` → `UNIQUE(netbox_source, netbox_id)` (Migration nötig) |
| `_netbox_device_exists` | Umbenennen/erweitern: je nach `netbox_source` URL wählen – `/api/dcim/devices/{id}/` oder `/api/virtualization/virtual-machines/{id}/` |
| `_check_netbox_id_exists` | Nutzt angepasste Existenzprüfung |
| `_extract_netbox_fields` | Parameter oder Erkennung: `data` von Device vs VM. Zwei Varianten: `_extract_netbox_fields_from_device(data)` und `_extract_netbox_fields_from_vm(data)` oder eine Methode mit Branch |
| `action_fetch_from_netbox` | URL abhängig von `netbox_source` |
| `_run_sync_all_from_netbox` | Erweiterung: neben `/api/dcim/devices/` auch `/api/virtualization/virtual-machines/` abrufen; `netbox_source` bei Create/Update setzen; `netbox_ids_seen` pro Source führen (oder Tupel `(source, id)`) |
| Archivierung | Nur VMs/Devices der jeweiligen Quelle archivieren (nicht Device-IDs mit VM-IDs vermischen) |

### 4.2 `config.py`

| Änderung | Details |
|----------|---------|
| `_run_netbox_url_test` | Zusätzlich Virtualization-API testen (z.B. `/api/virtualization/` oder `/api/virtualization/virtual-machines/?limit=1`) |

### 4.3 `views/configuration_item_views.xml`

| Änderung | Details |
|----------|---------|
| Form | Feld `netbox_source` anzeigen (readonly, im Bereich NetBox-Daten) |
| Tree | Optional: Spalte `netbox_source` oder Icon (Filter nach Typ) |
| Search | Filter „Device“, „Virtuelle Maschine“ |

### 4.4 `ir.config_parameter` / Sync-Logik

**Frage:** Ein oder zwei Sync-Zeitstempel für Delta-Sync?

- **Option A:** Ein gemeinsamer `NETBOX_LAST_SYNC_ALL_KEY` – beide Quellen nutzen denselben Zeitstempel (einfacher).
- **Option B:** Separate Keys für Devices und VMs – erlaubt getrenntes Delta-Sync (komplexer).

**Empfehlung:** Option A – ein Zeitstempel für den gesamten CI-Sync. Bei „Alle CI holen“ werden Devices und VMs in einem Lauf aktualisiert.

### 4.5 Migration (PostgreSQL)

```sql
-- Vorher: UNIQUE(netbox_id)
-- Nachher: UNIQUE(netbox_source, netbox_id)

-- 1. Neues Feld netbox_source mit default 'device' hinzufügen
-- 2. Bestehende Zeilen: netbox_source = 'device' (via default)
-- 3. Alter Constraint droppen, neuen anlegen
```

Odoo-Migration: `pre_init_hook` oder `post_init_hook` in `__manifest__.py`, oder Migrationsskript in einem `migrations/`-Verzeichnis.

---

## 5. Feldzuordnung VM – Extraktionslogik

Für `_extract_netbox_fields_from_vm(data)` (oder Branch in `_extract_netbox_fields`):

| Odoo-Feld | NetBox VM JSON |
|-----------|----------------|
| netbox_display | `data.get("display")` oder `data.get("name")` |
| netbox_display_url | `data.get("display_url")` |
| netbox_serial | `data.get("serial")` |
| netbox_device_type | leer (VMs haben kein device_type) |
| netbox_manufacturer | `platform.get("manufacturer", {}).get("name")` |
| netbox_model | – ( leer bei VM) |
| netbox_platform | `platform.get("name")` (z.B. „Ubuntu 22.04“, „Windows Server“) |
| netbox_role_id | `role` → netbox_device_role (gleich wie Device) |
| netbox_tenant_name | `tenant` |
| netbox_created, netbox_last_updated | wie Device |

**Hinweis:** Wenn VM keine `platform` hat: `netbox_manufacturer` und `netbox_platform` leer → CPE-String wird nicht erzeugt (lt. Pflichtenheft: Hersteller oder Produkt leer = kein CPE).

---

## 6. Sync-Ablauf „Alle CI holen“

**Aktuell:** Nur `GET /api/dcim/devices/`.

**Neu:**
1. `GET /api/dcim/devices/` (mit Paginierung) → wie bisher, `netbox_source='device'`
2. `GET /api/virtualization/virtual-machines/` (mit Paginierung) → neu, `netbox_source='vm'`

**Delta-Sync:**  
`last_updated__gte=<timestamp>` wird von beiden Endpoints unterstützt. Ein gemeinsamer Zeitstempel reicht.

**Archivierung:**  
- Geräte, die nur in Devices-Liste vorkamen und jetzt fehlen → archivieren (nur `netbox_source='device'`).  
- VMs, die nur in VM-Liste vorkamen und jetzt fehlen → archivieren (nur `netbox_source='vm'`).  
- Wichtig: Zwei getrennte Mengen `device_ids_seen` und `vm_ids_seen` führen.

---

## 7. Manueller Abruf „Hole NetBox-Item“

Beim manuellen Anlegen muss der Nutzer wählen: Device oder VM? Dann `netbox_id` + `netbox_source` eingeben.

**Alternativ:** Zwei Buttons – „Hole Device“ und „Hole VM“ – oder ein Feld `netbox_source` vorher setzen. Die URL für den Abruf ergibt sich aus `netbox_source`.

---

## 8. Zusammenfassung der Änderungsstellen

| Datei | Änderung |
|-------|----------|
| `models/configuration_item.py` | `netbox_source`; UNIQUE-Constraint; `_extract_netbox_fields` für VM; `_netbox_*_exists`; `action_fetch_from_netbox`; `_run_sync_all_from_netbox` |
| `config.py` | URL-Test optional um Virtualization erweitern |
| `views/configuration_item_views.xml` | `netbox_source` im Formular, ggf. Tree/Search |
| Migration | UNIQUE-Constraint von `netbox_id` auf `(netbox_source, netbox_id)` |
| `docs/Pflichtenheft.md` | Neues Kapitel „8.x Virtuelle Maschinen (VM)“ |
| `docs/FEATURE-LIST.md` | VM-Support ergänzen |

---

## 9. Service-Voraussetzungen (Leistungen) – Erweiterung für VMs

**Aktuell:** „CI-Felder holen“ lädt nur Device-Felder aus dem NetBox-Schema. Die erforderlichen Felder pro Leistung (z.B. Update-Service, Monitoring, CVE) beziehen sich auf Device-Pfade (`device_type.manufacturer`, `device_type.model`). Für VMs existieren diese Pfade nicht – VMs haben `platform.*`, `cluster`, etc.

**Anforderung:** Leistungen wie Update-Service, Monitoring, CVE-Monitoring gelten für Devices **und** VMs. Es muss definierbar sein, welche NetBox-Felder für eine **VM** ausgefüllt sein müssen, damit die Leistung erbracht werden kann.

| Aufgabe | Beschreibung |
|---------|---------------|
| **„CI-Felder holen“ erweitern** | Zusätzlich VM-Felder aus NetBox-Schema laden (`/api/virtualization/virtual-machines/` oder Virtualization-Schema) |
| **Erforderliche Felder pro Quelle** | Modell erweitern: erforderliche Felder pro Leistung entweder getrennt (Device vs. VM) oder mit Typ-Zuordnung |
| **Prüfung _compute_service_fields_status** | Bei VM-CI: VM-Feldpfade prüfen (z.B. `platform.name`, `platform.manufacturer`); bei Device: Device-Pfade |

**Betroffene Dateien:** `config.py` (action_refresh_netbox_device_fields, Schema-Extraktion), `models/service.py` (required_device_field_ids), `models/configuration_item.py` (_compute_service_fields_status).

---

## 10. Keine Änderung nötig

| Bereich | Begründung |
|---------|------------|
| `netbox_device_role` | VMs nutzen dieselben Device Roles |
| CI-Klasse-Mapping | Über `netbox_role_id` → unverändert |
| Vertragszuordnung | `contract_id`, `contract_service_ids` – unverändert |
| nt_cve-automatisation | `netbox_cpe` aus manufacturer, model/platform – siehe Kap. 5; CPE-Logik muss netbox_platform (OS) für VMs berücksichtigen |
| Wizard „CI zuordnen“ | Arbeitet mit `configuration_item` – kein Änderungsbedarf |

---

*Analyse erstellt für Planung der VM-Unterstützung.*
