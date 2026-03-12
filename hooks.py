# -----------------------------------------------------------------------------
# © NETHINKS GmbH – Alle Rechte vorbehalten
# Beschreibung: Pre/Post-Init-Hooks für Migrationen (z.B. VM-Support)
# -----------------------------------------------------------------------------


def pre_init_hook(cr):
    """Migration 1.2.2 → 1.2.3: netbox_source, UNIQUE(netbox_source, netbox_id).

    - Spalte netbox_source hinzufügen (default 'device')
    - Bestehenden UNIQUE(netbox_id) Constraint entfernen
    - Der neue UNIQUE(netbox_source, netbox_id) wird von Odoo beim Modell-Laden erstellt
    """
    table = "nt_serviceman_configuration_item"
    cr.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_name = %s",
        (table,),
    )
    if not cr.fetchone():
        return  # Erstinstallation – Tabelle wird mit neuem Schema angelegt
    cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s AND column_name = 'netbox_source'
        """,
        (table,),
    )
    if not cr.fetchone():
        cr.execute(
            f"""
            ALTER TABLE {table}
            ADD COLUMN netbox_source VARCHAR
            """
        )
        cr.execute(
            f"""
            UPDATE {table}
            SET netbox_source = 'device'
            WHERE netbox_source IS NULL
            """
        )
    cr.execute(
        """
        SELECT conname
        FROM pg_constraint
        WHERE conrelid = %s::regclass
          AND contype = 'u'
          AND conname LIKE '%%netbox_id%%'
        """,
        (table,),
    )
    for row in cr.fetchall():
        conname = row[0]
        cr.execute(f'ALTER TABLE {table} DROP CONSTRAINT IF EXISTS "{conname}"')
