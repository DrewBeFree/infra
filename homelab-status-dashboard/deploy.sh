#!/bin/bash
# Deploy homelab-status-dashboard to atlas
set -e

echo "Deploying homelab-status-dashboard to atlas..."
ssh atlas "cd ~/infra && git pull && rsync -a --exclude=config.js ~/infra/homelab-status-dashboard/ /opt/homelab-status-dashboard/ && cp ~/infra/homelab-status-dashboard/config.js /opt/homelab-status-dashboard/config.js"
echo "Done. Refresh http://atlas to see changes."
