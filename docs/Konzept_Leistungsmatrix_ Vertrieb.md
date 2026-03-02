# Konzept: Leistungsmatrix über den gesamten Lebenszyklus

## Phasen

1. **Produktdefinition** – Bei Produkttyp „Wiederkehrend“ (`detailed_type = "recurrent"`): Matrix anlegen und pflegen
2. **Vertrieb/Angebot** – Produkt in Angebotszeile → Vertrag wird erzeugt, Matrix wird übernommen
3. **Vertrag** – Vertrag aktiv, Matrix steuert buchbare Leistungen pro CI-Klasse

---

## Aktueller technischer Ablauf (Stand)

### Produktdefinition (product.template / product.product)

- `detailed_type = "recurrent"` für wiederkehrende Produkte
- `_prepare_contract_values()` bereitet Vertragswerte vor:
  - `_prepare_contract_default_values()` → Basisdaten (name, term, invoice_period, …)
  - `_prepare_contract_contingent_values()` → Contingents aus `product.contingent_ids` werden kopiert
  - `_prepare_consumption_values()` → Verbrauchsdaten (falls vorhanden)
- **Leistungsmatrix:** aktuell nicht vorgesehen → Vertrag startet mit leerer Matrix

### Angebot → Vertrag

- **sale.order.line** `_onchange_create_services`: Bei `product.detailed_type == "recurrent"` wird
  `product._prepare_contract_values(order_id=…, partner_id=…)` aufgerufen und der Vertrag erstellt.
- Vertrag wird unmittelbar angelegt und an `order_line.contract_id` gebunden.
- Vertrag bekommt alle Werte aus `_prepare_contract_values`; `nt_serviceman` ergänzt per `create()` die `ci_class_matrix_line_ids` (nur leere Zeilen für alle CI-Klassen).

### Vertrag

- Matrix auf `contract.recurrent` (Tab „Leistungsmatrix“), sichtbar für `state in ('new', 'draft')`.

---

## Gewünschter Ablauf (Produkt → Angebot → Vertrag)

1. **Produktdefinition:** Matrix (CI-Klasse × Menge × Leistungen) am Produkt definieren und vorbelegen – **nur bei `detailed_type = "recurrent"`**.
2. **Angebot:** Wenn wiederkehrendes Produkt in eine Zeile kommt, Matrix vom Produkt mitnehmen.
3. **Vertrag:** Matrix vom Angebot/Produkt übernehmen und optional im Vertrag anpassen.

### Fachlicher Use Case: NT/Care-Varianten

Bestimmte NT/Care-Verträge sollen nur „Basisleistungen“ umfassen. Der Proaktive Sicherheits-Service (CVE) z.B. gehört dann nicht dazu. Über die Matrix am Produkt können unterschiedliche Leistungsbündel definiert werden:

- **Produkt „NT/Care Basis“:** Nur Basisleistungen in der Matrix vorbelegt (z.B. Dokumentation, Konfigurations-Service, Update-Service) – CVE nicht ausgewählt.
- **Produkt „NT/Care Premium“:** Zusätzlich CVE und ggf. weitere Leistungen ausgewählt.

Die Matrix auf Produktebene definiert damit, welche Leistungen für dieses spezifische Produkt überhaupt buchbar sind – abhängig von der CI-Klasse.

---

## Technische Umsetzung: Matrix auf Produkt

### 1. Neues Modell: product.template.ci_class_matrix_line

Analog zu `contract_ci_class_matrix_line`:

| Feld           | Typ        | Beschreibung                                  |
|----------------|------------|-----------------------------------------------|
| product_tmpl_id | Many2one   | product.template (required, ondelete=cascade) |
| ci_class_id   | Many2one   | nt_serviceman.ci_class                        |
| quantity      | Integer    | default 0                                     |
| service_ids   | Many2many  | nt_serviceman.service                         |

- Constraint: `UNIQUE(product_tmpl_id, ci_class_id)`
- Constraint: `service_ids` nur aus `ci_class_id.service_ids`

### 2. product.template erweitern

- `ci_class_matrix_line_ids` (One2many)
- **Leistungsmatrix nur bei Produkttyp „Wiederkehrend“:** Tab/Bereich zur Matrix-Anlage und -Pflege ausschließlich anzeigen, wenn `detailed_type == "recurrent"` (attrs/readonly/invisible).

### 3. Übertragung in _prepare_contract_values

NT:ServiceMan erbt `product.product` und erweitert `_prepare_contract_values()`:

```python
def _prepare_contract_values(self, **kwargs):
    result = super()._prepare_contract_values(**kwargs)
    for i, vals in enumerate(result):
        product = self[i] if len(self) > 1 else self
        if product.detailed_type == "recurrent" and product.product_tmpl_id.ci_class_matrix_line_ids:
            matrix_cmds = [
                (0, 0, {
                    "ci_class_id": line.ci_class_id.id,
                    "quantity": line.quantity,
                    "service_ids": [(6, 0, line.service_ids.ids)],
                })
                for line in product.product_tmpl_id.ci_class_matrix_line_ids
            ]
            vals["ci_class_matrix_line_ids"] = matrix_cmds
    return result
```

### 4. contract.recurrent create anpassen

- Wenn `ci_class_matrix_line_ids` in `vals` vorhanden und nicht leer, dann `action_init_ci_class_matrix_lines()` nicht aufrufen (oder nur für fehlende CI-Klassen ergänzen).
- Aktuell erstellt `action_init_ci_class_matrix_lines()` nur Zeilen für CI-Klassen ohne bestehende Zeile; bei Übertrag vom Produkt passen die Daten bereits.

---

## Optionen für die Vertriebsphase (unverändert)

### Option A: Direkter Zugang vom Angebot (Empfohlen)

**Idee:** Tab „Leistungsmatrix“ auf dem Angebotsformular mit Button „Leistungsmatrix bearbeiten“, der den zugehörigen Vertrag öffnet.

**Vorteile:**
- Vertrieb bleibt gedanklich auf dem Angebot.
- Klarer Einstieg, ohne im Vertrag suchen zu müssen.
- Bei mehreren Verträgen: Button öffnet Liste bzw. ersten Vertrag.

**Umsetzung:**
1. Sale Order erweitern: computed field `recurring_contract_ids` = Verträge aus `order_line.contract_id`.
2. Tab „Leistungsmatrix“ auf dem Angebotsformular (sichtbar wenn `recurring_contract_ids`).
3. Button „Leistungsmatrix bearbeiten“ → öffnet ersten Vertrag (oder Liste) im Formular.
4. Matrix bleibt wie bisher auf dem Vertrag; nur der Zugriff wird vereinfacht.

### Option B: Matrix direkt auf dem Angebot (Integriert)

**Idee:** Die Matrix liegt auf dem Angebot, wird beim Übergang in den Vertrag übernommen.

**Herausforderung:**
- Der Vertrag wird im onchange erzeugt, also schon beim Produkthinzufügen.
- Zu diesem Zeitpunkt hat der Nutzer die Matrix noch nicht ausgefüllt.
- Matrix müsste entweder:
  - auf dem Angebot gepflegt und später in den Vertrag kopiert werden, oder
  - bidirektional zwischen Angebot und Vertrag synchronisiert werden.

**Umsetzung (wenn gewünscht):**
1. Modell `sale.order.ci_class_matrix_line` analog zu `contract_ci_class_matrix_line` mit Verknüpfung zu `sale.order`.
2. Tab auf dem Angebot mit identischer Matrix-UI.
3. Bei Vertragserstellung bzw. beim Übergang von Angebot zu Auftrag: Matrix vom Angebot in den Vertrag kopieren.
4. Einschränkung: Vertrag entsteht vor dem ersten Speichern des Angebots; Kopierzeitpunkt muss fest definiert werden (z.B. erstes Speichern oder Bestätigen).

### Option C: Matrix auf der Angebotszeile

**Idee:** Pro wiederkehrender Zeile eine eigene Matrix.

**Nachteile:**
- Eine Matrix enthält viele Zeilen (CI-Klassen); das passt nicht gut in eine Tabellenzeile.
- Mehrere Zeilen mit je eigener Matrix erhöhen die Komplexität.

**Bewertung:** Eher ungeeignet.

## Empfehlung: Option A

- Geringer Implementierungsaufwand.
- Keine Änderung der Vertragslogik.
- Nutzer bekommt einen klaren Einstieg zur Matrix, ohne den Vertrag manuell zu suchen.

## Geplante technische Schritte (Option A)

1. **Modelle:** `sale.order` um computed field `recurring_contract_ids` erweitern (falls nicht vorhanden).
2. **View:** Angebotsformular erben und Tab „Leistungsmatrix“ ergänzen.
3. **Action:** Methode `action_open_ci_class_matrix()` auf `sale.order`, die den ersten wiederkehrenden Vertrag öffnet (oder eine Auswahl, wenn mehrere).
4. **Sichtbarkeit:** Tab nur anzeigen, wenn `recurring_contract_ids` nicht leer ist.

---

## Zusammenfassung: Datenfluss Matrix

| Phase              | Wo definiert?              | Übertragung                                |
|--------------------|----------------------------|--------------------------------------------|
| Produktdefinition  | product.template           | –                                          |
| Angebot            | Vertrag (vom Produkt)      | onchange: Produkt → Vertrag                |
| Vertrag            | contract.recurrent         | Matrix beim contract.create mit übergeben  |

**Vorbild:** `contingent_ids` – wird am Produkt gepflegt und in `_prepare_contract_contingent_values()` per Command.create in die contract_values übernommen.
