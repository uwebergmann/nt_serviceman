#!/bin/bash
# Deploy nt_serviceman nach Odoo-Server (ohne .git, __pycache__, etc.)
# Verwendung: ./deploy.sh [user@host]
# Beispiel:   ./deploy.sh root@odoo16.nethinks-intern.com

HOST="${1:-root@odoo16.nethinks-intern.com}"
DEST="${HOST}:~/service/custom_modules/"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

echo "Deploy nt_serviceman -> $DEST"
rsync -avz --delete \
  --exclude='.git/' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='.DS_Store' \
  --exclude='docs/' \
  --exclude='*.docx' \
  nt_serviceman/ "$DEST/nt_serviceman/"

echo "Fertig. Modul-Upgrade auf dem Server:"
echo "  docker-compose exec -T odoo odoo -d <DB> --no-http --stop-after-init -u nt_serviceman"
