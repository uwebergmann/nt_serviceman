# NT:ServiceMan – Deploy & Update

## Deploy (Dateien auf Staging kopieren)

```bash
scp -r nt_serviceman root@odoo16.nethinks-intern.com:/root/service/custom_modules/
```

## Modul-Update (Odoo)

```bash
docker-compose exec -T odoo odoo -d 20250327 --no-http --stop-after-init -u nt_serviceman
```

*(Auf dem Zielsystem ausführen bzw. via SSH.)*

---
- **Ziel:** `odoo16.nethinks-intern.com`
- **Datenbank:** `20250327`
