# DrewBeFree Wiki

MkDocs Material wiki for the homelab, projects, and workflows. Private — served on
atlas over Tailscale at `http://atlas/wiki/`.

## Local preview

```bash
python3 -m venv .venv                            # first time only
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/gen_catalog.py          # regenerate the projects catalog from local repos
.venv/bin/python -m mkdocs serve                 # http://127.0.0.1:8000
```

## Deploy

Run `./deploy.sh` from the dev machine. It regenerates the catalog, refuses if
`docs/projects/` has uncommitted changes (commit via your branch workflow first),
pushes `infra`, then SSHes to atlas to `git pull` and `mkdocs build` into `/opt/wiki`.

## One-time atlas setup

This machine (and atlas, if Debian/Ubuntu) enforces PEP 668, so a virtualenv is required —
`pip install --user` will fail.

```bash
# on atlas, inside ~/infra/wiki
python3 -m venv .venv
.venv/bin/python -m pip install mkdocs-material
sudo mkdir -p /opt/wiki && sudo chown drew:drew /opt/wiki
```

Add to the existing Nginx server block (the one serving the status dashboard):

```nginx
location /wiki/ {
    alias /opt/wiki/;
    index index.html;
    try_files $uri $uri/ =404;
}
```

Then `sudo nginx -t && sudo systemctl reload nginx`.

## How the catalog stays current

`scripts/gen_catalog.py` scans `apps/`, `sites/`, `agents/` on the dev machine for git
repos (the authoritative project list), enriches each from `repos.json` (GitHub URL) and
the Command Center `index.html` (version/status, via `scripts/card_map.json`), and writes
`docs/projects/`. It prints drift warnings when a repo on disk is missing from `repos.json`.
Generation runs on dev only — atlas just builds the committed output.
