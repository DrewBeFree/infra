#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run with sudo: sudo bash $0" >&2
  exit 1
fi

stamp="$(date +%Y%m%d-%H%M%S)"

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y apcupsd usbutils

mkdir -p /root/apcupsd-backups-${stamp}
for f in /etc/apcupsd/apcupsd.conf /etc/default/apcupsd; do
  if [[ -f "$f" ]]; then
    cp -a "$f" "/root/apcupsd-backups-${stamp}/$(basename "$f")"
  fi
done

cat >/etc/apcupsd/apcupsd.conf <<'EOF'
UPSNAME atlas-apc
UPSCABLE usb
UPSTYPE usb
DEVICE
POLLTIME 60

# Safe shutdown thresholds. Tune after we see real runtime/load.
BATTERYLEVEL 15
MINUTES 5
TIMEOUT 0
ANNOY 300
ANNOYDELAY 60
NOLOGON disable
KILLDELAY 0

NETSERVER on
NISIP 127.0.0.1
NISPORT 3551
EVENTSFILE /var/log/apcupsd.events
EVENTSFILEMAX 10

UPSCLASS standalone
UPSMODE disable
STATTIME 0
STATFILE /var/log/apcupsd.status
LOGSTATS off
DATATIME 0
EOF

sed -i 's/^ISCONFIGURED=.*/ISCONFIGURED=yes/' /etc/default/apcupsd
if ! grep -q '^ISCONFIGURED=' /etc/default/apcupsd; then
  echo 'ISCONFIGURED=yes' >>/etc/default/apcupsd
fi

systemctl enable --now apcupsd
systemctl restart apcupsd
sleep 3

systemctl --no-pager --full status apcupsd || true
printf '\nUSB APC devices:\n'
lsusb | grep -Ei 'apc|american power|schneider|ups' || true
printf '\napcaccess status:\n'
apcaccess status || true
