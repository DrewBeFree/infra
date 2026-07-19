#!/usr/bin/env python3
import os
import socket
import struct
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

APCUPSD_HOST = os.getenv("APCUPSD_HOST", "127.0.0.1")
APCUPSD_PORT = int(os.getenv("APCUPSD_PORT", "3551"))
LISTEN_PORT = int(os.getenv("LISTEN_PORT", "9162"))
TIMEOUT = float(os.getenv("APCUPSD_TIMEOUT", "3"))

NUMERIC_FIELDS = {
    "LINEV": "apcupsd_line_voltage_volts",
    "LOADPCT": "apcupsd_load_percent",
    "BCHARGE": "apcupsd_battery_charge_percent",
    "TIMELEFT": "apcupsd_time_left_minutes",
    "MBATTCHG": "apcupsd_min_battery_charge_percent",
    "MINTIMEL": "apcupsd_min_time_left_minutes",
    "MAXTIME": "apcupsd_max_runtime_seconds",
    "OUTPUTV": "apcupsd_output_voltage_volts",
    "BATTV": "apcupsd_battery_voltage_volts",
    "NUMXFERS": "apcupsd_transfer_count_total",
    "TONBATT": "apcupsd_time_on_battery_seconds",
    "CUMONBATT": "apcupsd_cumulative_time_on_battery_seconds",
    "NOMINV": "apcupsd_nominal_input_voltage_volts",
    "NOMBATTV": "apcupsd_nominal_battery_voltage_volts",
    "NOMPOWER": "apcupsd_nominal_power_watts",
}

STATUS_FLAGS = ["ONLINE", "ONBATT", "LOWBATT", "REPLACEBATT", "OVERLOAD", "CAL", "TRIM", "BOOST"]


def _send(sock, text):
    data = text.encode("ascii")
    sock.sendall(struct.pack("!H", len(data)) + data)


def _recv_chunks(sock):
    chunks = []
    while True:
        hdr = sock.recv(2)
        if len(hdr) < 2:
            break
        size = struct.unpack("!H", hdr)[0]
        if size == 0:
            break
        data = b""
        while len(data) < size:
            part = sock.recv(size - len(data))
            if not part:
                break
            data += part
        chunks.append(data.decode("utf-8", errors="replace"))
    return "".join(chunks)


def fetch_status():
    with socket.create_connection((APCUPSD_HOST, APCUPSD_PORT), timeout=TIMEOUT) as sock:
        sock.settimeout(TIMEOUT)
        _send(sock, "status")
        return parse_status(_recv_chunks(sock))


def parse_status(raw):
    values = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def first_float(text):
    if text is None:
        return None
    for token in text.replace("%", " ").split():
        try:
            return float(token)
        except ValueError:
            continue
    return None


def labels(**items):
    return "{" + ",".join(f'{k}="{str(v).replace(chr(34), chr(92)+chr(34))}"' for k, v in items.items()) + "}"


def render_metrics():
    now = int(time.time())
    lines = []
    try:
        data = fetch_status()
        lines.append("# HELP apcupsd_up 1 if apcupsd status was readable")
        lines.append("# TYPE apcupsd_up gauge")
        lines.append("apcupsd_up 1")

        status = data.get("STATUS", "UNKNOWN")
        model = data.get("MODEL", "unknown")
        upsname = data.get("UPSNAME", "unknown")
        serial = data.get("SERIALNO", "unknown")
        lines.append("# HELP apcupsd_status UPS status flag gauges")
        lines.append("# TYPE apcupsd_status gauge")
        for flag in STATUS_FLAGS:
            lines.append(f"apcupsd_status{labels(flag=flag, model=model, upsname=upsname, serial=serial)} {1 if flag in status.split() else 0}")

        lines.append("# HELP apcupsd_info Static UPS info")
        lines.append("# TYPE apcupsd_info gauge")
        lines.append(f"apcupsd_info{labels(model=model, upsname=upsname, serial=serial, status=status)} 1")

        for key, metric in NUMERIC_FIELDS.items():
            value = first_float(data.get(key))
            if value is None:
                continue
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {value}")

        lines.append("# TYPE apcupsd_last_scrape_timestamp_seconds gauge")
        lines.append(f"apcupsd_last_scrape_timestamp_seconds {now}")
    except Exception as exc:
        lines.append("# HELP apcupsd_up 1 if apcupsd status was readable")
        lines.append("# TYPE apcupsd_up gauge")
        lines.append("apcupsd_up 0")
        lines.append("# HELP apcupsd_scrape_error Exporter scrape error")
        lines.append("# TYPE apcupsd_scrape_error gauge")
        lines.append(f"apcupsd_scrape_error{labels(error=type(exc).__name__ + ': ' + str(exc))} 1")
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/metrics"):
            self.send_response(404)
            self.end_headers()
            return
        body = render_metrics().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", LISTEN_PORT), Handler).serve_forever()
