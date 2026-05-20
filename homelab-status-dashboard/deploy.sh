#!/bin/bash
# Deploy homelab-status-dashboard to atlas
set -e

echo "Deploying homelab-status-dashboard to atlas..."
ssh atlas "cd ~/infra && git pull"
echo "Done. Refresh http://atlas to see changes."
