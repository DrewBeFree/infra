#!/usr/bin/env python3
"""PIN-gated static gateway for the DrewBeFree ecosystem world page.

Intended deployment:
  world.drewbefree.com -> Cloudflare Tunnel -> http://127.0.0.1:8137

Secrets are read from a local env file / systemd EnvironmentFile and must not be
committed. The gateway serves only the static ecosystem portal files after a
valid PIN creates a signed session cookie.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import html
import http.server
import mimetypes
import os
import posixpath
import secrets
import time
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, unquote, urlparse

COOKIE_NAME = "drew_world_session"
DEFAULT_SESSION_TTL_SECONDS = 60 * 60 * 12
DEFAULT_INDEX = "world.html"
ALLOWED_SUFFIXES = {
    ".html",
    ".json",
    ".css",
    ".js",
    ".mjs",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".ico",
    ".webp",
    ".gif",
    ".txt",
    ".map",
}

LOGIN_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DrewBeFree Ecosystem World</title>
<style>
:root { color-scheme: light; --ink:#172033; --muted:#64748b; --blue:#4f46e5; --violet:#7c3aed; --line:#dbe5f5; }
* { box-sizing: border-box; }
body { margin:0; min-height:100vh; display:grid; place-items:center; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: radial-gradient(circle at 20% 10%, rgba(79,70,229,.18), transparent 28%), radial-gradient(circle at 80% 70%, rgba(124,58,237,.16), transparent 30%), linear-gradient(135deg,#eef4ff,#f8fbff); color:var(--ink); }
main { width:min(440px, calc(100vw - 32px)); padding:32px; border:1px solid rgba(255,255,255,.8); border-radius:28px; background:rgba(255,255,255,.82); box-shadow:0 30px 90px rgba(15,23,42,.18); backdrop-filter:blur(18px); }
.badge { display:inline-flex; gap:8px; align-items:center; padding:7px 11px; border-radius:999px; color:#fff; background:linear-gradient(135deg,var(--blue),var(--violet)); font-size:.72rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }
h1 { margin:18px 0 8px; font-size:1.75rem; line-height:1.05; }
p { margin:0 0 18px; color:var(--muted); line-height:1.45; }
label { display:block; margin:0 0 8px; font-size:.78rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; color:#475569; }
input { width:100%; padding:14px 15px; border:1px solid var(--line); border-radius:16px; font-size:1.2rem; letter-spacing:.18em; text-align:center; }
button { width:100%; margin-top:14px; padding:14px 18px; border:0; border-radius:16px; color:#fff; background:linear-gradient(135deg,var(--blue),var(--violet)); font-weight:900; cursor:pointer; }
.error { margin-top:14px; padding:10px 12px; border-radius:14px; background:#fff1f2; color:#be123c; font-weight:800; font-size:.88rem; }
small { display:block; margin-top:16px; color:#64748b; line-height:1.4; }
</style>
</head>
<body>
<main>
  <span class="badge">PIN protected</span>
  <h1>Drew’s Ecosystem World</h1>
  <p>This private Atlas map is exposed through Cloudflare Tunnel and requires a local PIN before the world view is served.</p>
  <form method="post" action="/login">
    <label for="pin">Access PIN</label>
    <input id="pin" name="pin" type="password" inputmode="numeric" autocomplete="one-time-code" autofocus required>
    <button type="submit">Unlock world</button>
  </form>
  {error}
  <small>No raw secrets are stored in the portal repo. The PIN hash and session secret live only in the local systemd environment file.</small>
</main>
</body>
</html>
"""


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def sign(secret: str, payload: str) -> str:
    return b64url(hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest())


class PinGateway(http.server.BaseHTTPRequestHandler):
    server_version = "DrewWorldPinGateway/1.0"

    @property
    def gateway(self) -> "ThreadingHTTPServer":
        return cast("ThreadingHTTPServer", self.server)

    def do_HEAD(self) -> None:  # noqa: N802
        if not self.is_authenticated():
            self.render_login(head_only=True)
            return
        self.serve_static(head_only=True)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/logout":
            self.send_response(303)
            self.send_header("Set-Cookie", self.expire_cookie())
            self.send_header("Location", "/")
            self.security_headers()
            self.end_headers()
            return
        if not self.is_authenticated():
            self.render_login()
            return
        self.serve_static(head_only=False)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/login":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(min(length, 4096)).decode("utf-8", errors="replace")
        pin = parse_qs(body).get("pin", [""])[0].strip()
        expected = self.gateway.pin_hash
        if expected and hmac.compare_digest(sha256_hex(pin), expected):
            self.send_response(303)
            self.send_header("Set-Cookie", self.session_cookie())
            self.send_header("Location", "/")
            self.security_headers()
            self.end_headers()
            return
        time.sleep(0.5)
        self.render_login(error="Invalid PIN.", status=401)

    def render_login(self, error: str = "", status: int = 200, head_only: bool = False) -> None:
        error_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
        page = LOGIN_PAGE.replace("{error}", error_html).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.security_headers()
        self.end_headers()
        if not head_only:
            self.wfile.write(page)

    def session_cookie(self) -> str:
        expires = int(time.time()) + self.gateway.session_ttl
        nonce = secrets.token_urlsafe(16)
        payload = f"{expires}.{nonce}"
        token = f"{payload}.{sign(self.gateway.session_secret, payload)}"
        return f"{COOKIE_NAME}={token}; Max-Age={self.gateway.session_ttl}; Path=/; HttpOnly; Secure; SameSite=Lax"

    def expire_cookie(self) -> str:
        return f"{COOKIE_NAME}=; Max-Age=0; Path=/; HttpOnly; Secure; SameSite=Lax"

    def is_authenticated(self) -> bool:
        cookie = self.headers.get("Cookie", "")
        prefix = f"{COOKIE_NAME}="
        token = ""
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith(prefix):
                token = part[len(prefix):]
                break
        if not token:
            return False
        bits = token.split(".")
        if len(bits) != 3:
            return False
        expires, nonce, received = bits
        payload = f"{expires}.{nonce}"
        if not hmac.compare_digest(sign(self.gateway.session_secret, payload), received):
            return False
        try:
            return int(expires) >= int(time.time())
        except ValueError:
            return False

    def safe_path(self) -> Path | None:
        parsed = urlparse(self.path)
        raw_path = unquote(parsed.path)
        if raw_path in {"", "/"}:
            raw_path = f"/{DEFAULT_INDEX}"
        normalized = posixpath.normpath(raw_path).lstrip("/")
        if normalized == "ecosystem":
            normalized = DEFAULT_INDEX
        elif normalized.startswith("ecosystem/"):
            normalized = normalized.removeprefix("ecosystem/")
        if normalized.startswith("..") or "/../" in normalized:
            return None
        candidate = (self.gateway.root / normalized).resolve()
        try:
            candidate.relative_to(self.gateway.root)
        except ValueError:
            return None
        if candidate.is_dir():
            candidate = candidate / DEFAULT_INDEX
        if candidate.suffix.lower() not in ALLOWED_SUFFIXES:
            return None
        return candidate

    def serve_static(self, head_only: bool = False) -> None:
        candidate = self.safe_path()
        if not candidate or not candidate.exists() or not candidate.is_file():
            self.send_error(404)
            return
        data = b"" if head_only else candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(candidate.stat().st_size))
        self.security_headers()
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    def security_headers(self) -> None:
        self.send_header("Cache-Control", "private, no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Robots-Tag", "noindex, nofollow, noarchive")

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - - [{self.log_date_time_string()}] {fmt % args}")


class ThreadingHTTPServer(http.server.ThreadingHTTPServer):
    root: Path
    pin_hash: str
    session_secret: str
    session_ttl: int


def build_server(host: str, port: int, root: Path) -> ThreadingHTTPServer:
    pin_hash = os.environ.get("WORLD_PORTAL_PIN_SHA256", "").strip().lower()
    session_secret = os.environ.get("WORLD_PORTAL_SESSION_SECRET", "").strip()
    if not pin_hash or len(pin_hash) != 64:
        raise SystemExit("WORLD_PORTAL_PIN_SHA256 must be set to a SHA-256 hex digest")
    if len(session_secret) < 32:
        raise SystemExit("WORLD_PORTAL_SESSION_SECRET must be set to at least 32 characters")
    root = root.resolve()
    if not (root / DEFAULT_INDEX).exists():
        raise SystemExit(f"{root / DEFAULT_INDEX} does not exist")
    server = ThreadingHTTPServer((host, port), PinGateway)
    server.root = root
    server.pin_hash = pin_hash
    server.session_secret = session_secret
    server.session_ttl = int(os.environ.get("WORLD_PORTAL_SESSION_TTL_SECONDS", DEFAULT_SESSION_TTL_SECONDS))
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="PIN-gated static gateway for ecosystem world")
    parser.add_argument("--host", default=os.environ.get("WORLD_PORTAL_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("WORLD_PORTAL_PORT", "8137")))
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("WORLD_PORTAL_ROOT", "/opt/homelab-status-dashboard/ecosystem")))
    args = parser.parse_args()
    server = build_server(args.host, args.port, args.root)
    print(f"Serving PIN-gated world portal on http://{args.host}:{args.port} from {server.root}")
    server.serve_forever()


if __name__ == "__main__":
    main()
