#!/usr/bin/env python3
"""Small Prometheus exporter for Atlas NVIDIA GPU telemetry."""

from __future__ import annotations

import argparse
import csv
import html
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO


QUERY_FIELDS = [
    "index",
    "name",
    "uuid",
    "temperature.gpu",
    "power.draw",
    "memory.used",
    "memory.total",
    "utilization.gpu",
    "utilization.memory",
]


def prom_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def parse_float(value: str) -> float | None:
    cleaned = value.strip()
    if not cleaned or cleaned.upper() in {"N/A", "[N/A]", "NOT SUPPORTED", "[NOT SUPPORTED]"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def metric_line(name: str, labels: dict[str, str], value: float | int) -> str:
    label_text = ",".join(f'{key}="{prom_escape(val)}"' for key, val in labels.items())
    return f"{name}{{{label_text}}} {value}"


def collect_metrics() -> tuple[int, str]:
    started = time.monotonic()
    lines: list[str] = [
        "# HELP nvidia_gpu_scrape_success Whether nvidia-smi collection succeeded.",
        "# TYPE nvidia_gpu_scrape_success gauge",
        "# HELP nvidia_gpu_scrape_duration_seconds Time spent collecting nvidia-smi data.",
        "# TYPE nvidia_gpu_scrape_duration_seconds gauge",
        "# HELP nvidia_gpu_info Static NVIDIA GPU identity information.",
        "# TYPE nvidia_gpu_info gauge",
        "# HELP nvidia_gpu_temperature_celsius Current NVIDIA GPU temperature.",
        "# TYPE nvidia_gpu_temperature_celsius gauge",
        "# HELP nvidia_gpu_power_draw_watts Current NVIDIA GPU power draw.",
        "# TYPE nvidia_gpu_power_draw_watts gauge",
        "# HELP nvidia_gpu_memory_used_bytes Current NVIDIA GPU memory used.",
        "# TYPE nvidia_gpu_memory_used_bytes gauge",
        "# HELP nvidia_gpu_memory_total_bytes Total NVIDIA GPU memory.",
        "# TYPE nvidia_gpu_memory_total_bytes gauge",
        "# HELP nvidia_gpu_utilization_percent Current NVIDIA GPU compute utilization.",
        "# TYPE nvidia_gpu_utilization_percent gauge",
        "# HELP nvidia_gpu_memory_utilization_percent Current NVIDIA GPU memory controller utilization.",
        "# TYPE nvidia_gpu_memory_utilization_percent gauge",
    ]

    command = [
        "nvidia-smi",
        f"--query-gpu={','.join(QUERY_FIELDS)}",
        "--format=csv,noheader,nounits",
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=8)
        rows = csv.reader(StringIO(result.stdout))
        for row in rows:
            if len(row) != len(QUERY_FIELDS):
                continue

            values = {field: cell.strip() for field, cell in zip(QUERY_FIELDS, row)}
            labels = {
                "gpu": values["index"],
                "name": values["name"],
                "uuid": values["uuid"],
            }

            lines.append(metric_line("nvidia_gpu_info", labels, 1))

            metric_map = {
                "nvidia_gpu_temperature_celsius": ("temperature.gpu", 1),
                "nvidia_gpu_power_draw_watts": ("power.draw", 1),
                "nvidia_gpu_memory_used_bytes": ("memory.used", 1024 * 1024),
                "nvidia_gpu_memory_total_bytes": ("memory.total", 1024 * 1024),
                "nvidia_gpu_utilization_percent": ("utilization.gpu", 1),
                "nvidia_gpu_memory_utilization_percent": ("utilization.memory", 1),
            }

            for metric_name, (field, multiplier) in metric_map.items():
                parsed = parse_float(values[field])
                if parsed is not None:
                    lines.append(metric_line(metric_name, labels, parsed * multiplier))

        success = 1
        status = 200
    except Exception:
        success = 0
        status = 500

    duration = time.monotonic() - started
    lines.append(f"nvidia_gpu_scrape_success {success}")
    lines.append(f"nvidia_gpu_scrape_duration_seconds {duration:.6f}")
    return status, "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            body = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path.split("?", 1)[0] != "/metrics":
            body = f"not found: {html.escape(self.path)}\n".encode("utf-8")
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        status, metrics = collect_metrics()
        body = metrics.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9701)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
