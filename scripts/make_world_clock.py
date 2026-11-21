#!/usr/bin/env python3
"""Render a self-hosted animated world clock SVG."""

from __future__ import annotations

import argparse
import html
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


SAFE_RAIN = "01*+:.abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


# The full table: every major city / timezone, west to east.
CITIES = [
    ("Honolulu", "Pacific/Honolulu"),
    ("Los Angeles", "America/Los_Angeles"),
    ("Denver", "America/Denver"),
    ("Chicago", "America/Chicago"),
    ("Maryland", "America/New_York"),
    ("New York", "America/New_York"),
    ("Toronto", "America/Toronto"),
    ("Mexico City", "America/Mexico_City"),
    ("Sao Paulo", "America/Sao_Paulo"),
    ("UTC", "UTC"),
    ("London", "Europe/London"),
    ("Paris", "Europe/Paris"),
    ("Cairo", "Africa/Cairo"),
    ("Dubai", "Asia/Dubai"),
    ("Mumbai", "Asia/Kolkata"),
    ("Bangkok", "Asia/Bangkok"),
    ("Singapore", "Asia/Singapore"),
    ("Tokyo", "Asia/Tokyo"),
    ("Sydney", "Australia/Sydney"),
]

# Decorative globe pins for the featured route (name, x, y at canvas height 500).
PINS = [
    ("Maryland", 480, 210),
    ("UTC", 553, 250),
    ("London", 558, 180),
    ("Dubai", 620, 208),
    ("Tokyo", 692, 192),
    ("Sao Paulo", 530, 302),
]


def clock_row(y: int, city: str, zone: str, now_utc: datetime) -> str:
    local = now_utc.astimezone(ZoneInfo(zone))
    offset = local.strftime("%z")
    offset_label = f"UTC{offset[:3]}:{offset[3:]}" if offset else "UTC+00:00"
    return (
        f'<text x="34" y="{y}" class="city">{html.escape(city)}</text>'
        f'<text x="185" y="{y}" class="time">{local:%H:%M}</text>'
        f'<text x="245" y="{y}" class="date">{local:%a %b %d}</text>'
        f'<text x="338" y="{y}" class="offset">{offset_label}</text>'
    )


def rain(panel_id: str, width: int, height: int) -> str:
    out = [f'<g clip-path="url(#{panel_id})" opacity="0.11">']
    for col in range(38):
        x = 24 + col * 20
        chars = "".join(SAFE_RAIN[(col * 11 + row * 5) % len(SAFE_RAIN)] for row in range(17))
        delay = 0.01 + (col % 10) * 0.13
        dur = 6 + (col % 6)
        out.append(
            f'<text x="{x}" y="-36" class="rain">{html.escape(chars)}'
            f'<animate attributeName="y" values="-36;{height + 36};-36" '
            f'keyTimes="0;0.92;1" calcMode="discrete" dur="{dur}s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            '</text>'
        )
    out.append("</g>")
    return "\n".join(out)


def render(now_utc: datetime) -> str:
    width = 790
    row_step = 21
    first_row = 70
    height = first_row + len(CITIES) * row_step + 52
    cy = height // 2
    generated = now_utc.strftime("%Y-%m-%d %H:%M UTC")
    rows = "\n".join(clock_row(first_row + i * row_step, city, zone, now_utc) for i, (city, zone) in enumerate(CITIES))

    pins = []
    for i, (city, x, y) in enumerate(PINS):
        # Pin y positions were tuned for height 500; rescale if the table grows.
        y = round(y * height / 500)
        delay = 0.01 + i * 0.18
        pins.append(
            f'<circle cx="{x}" cy="{y}" r="3.2" fill="#39d353"/>'
            f'<circle cx="{x}" cy="{y}" r="3.2" fill="none" stroke="#7cff9b" stroke-width="1" opacity="0">'
            f'<animate attributeName="r" values="3;3;13;20" keyTimes="0;0.12;0.55;1" dur="3.6s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.75;0.2;0" keyTimes="0;0.12;0.55;1" dur="3.6s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
            f'<text x="{x + 8}" y="{y - 7}" class="pin-label">{html.escape(city)}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Animated world clock">
<defs>
  <clipPath id="clock-clip"><rect x="18" y="16" width="754" height="{height - 32}" rx="16"/></clipPath>
  <linearGradient id="clock-bg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#06170d"/><stop offset="0.58" stop-color="#07110c"/><stop offset="1" stop-color="#020706"/></linearGradient>
  <radialGradient id="clock-glow" cx="72%" cy="42%" r="58%"><stop offset="0" stop-color="#39d353" stop-opacity="0.22"/><stop offset="1" stop-color="#39d353" stop-opacity="0"/></radialGradient>
  <filter id="soft-glow"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{width}" height="{height}" rx="18" fill="#020504"/>
<rect x="18" y="16" width="754" height="{height - 32}" rx="16" fill="url(#clock-bg)" stroke="#1f8f4d" stroke-width="1.2"/>
<rect x="18" y="16" width="754" height="{height - 32}" rx="16" fill="url(#clock-glow)"/>
{rain("clock-clip", width, height)}
<circle cx="39" cy="38" r="5" fill="#ff5f57"/><circle cx="57" cy="38" r="5" fill="#ffbd2e"/><circle cx="75" cy="38" r="5" fill="#28c840"/>
<text x="96" y="43" class="title">martinezworldwide@github: ~/world-clock</text>
<g clip-path="url(#clock-clip)">
  <rect x="416" y="56" width="312" height="{height - 112}" rx="10" fill="#06120b" opacity="0.76"/>
  <ellipse cx="572" cy="{cy}" rx="132" ry="{height // 4}" fill="none" stroke="#245b37" stroke-width="1"/>
  <ellipse cx="572" cy="{cy}" rx="87" ry="{height // 4}" fill="none" stroke="#163d26" stroke-width="0.8"/>
  <ellipse cx="572" cy="{cy}" rx="44" ry="{height // 4}" fill="none" stroke="#12331f" stroke-width="0.8"/>
  <path d="M440 {cy}h264M572 {cy - height // 4}v{height // 2}M458 {cy - height // 8}h228M458 {cy + height // 8}h228" stroke="#12331f" stroke-width="0.8"/>
  <path d="M154 88C248 54 390 44 488 94S583 126 622 86" fill="none" stroke="#39d353" stroke-width="1.3" opacity="0.42" stroke-dasharray="4 8">
    <animate attributeName="stroke-dashoffset" values="48;0" dur="4.8s" begin="0.01s" repeatCount="indefinite"/>
  </path>
  <g filter="url(#soft-glow)">{"".join(pins)}</g>
  <rect x="416" y="56" width="42" height="{height - 112}" fill="#6dff95" opacity="0">
    <animate attributeName="x" values="416;686;416" keyTimes="0;0.88;1" dur="7s" begin="0.01s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;0.18;0" keyTimes="0;0.42;1" dur="7s" begin="0.01s" repeatCount="indefinite"/>
  </rect>
</g>
<text x="34" y="52" class="label">city</text><text x="185" y="52" class="label">time</text><text x="245" y="52" class="label">local date</text><text x="338" y="52" class="label">offset</text>
{rows}
<text x="34" y="{height - 28}" class="updated">updated: {generated}</text>
<text x="526" y="{height - 28}" class="prompt">$ chronyc tracking</text>
<rect x="688" y="{height - 41}" width="9" height="16" fill="#39d353" opacity="0">
  <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.85;0.86;0.99;1" dur="1s" begin="0.01s" repeatCount="indefinite"/>
</rect>
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.title{{fill:#e4ffea;font-size:16px;font-weight:700}}.label{{fill:#7fb98d;font-size:10px;text-transform:uppercase}}
.city{{fill:#d7ffe3;font-size:13px;font-weight:700}}.time{{fill:#39d353;font-size:16px;font-weight:800}}
.date,.offset{{fill:#b8e8c2;font-size:12px}}.updated{{fill:#7fb98d;font-size:11px}}.prompt{{fill:#39d353;font-size:13px}}
.rain{{fill:#39d353;font-size:10px;writing-mode:vertical-rl}}.pin-label{{fill:#b8e8c2;font-size:9px}}
</style>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="assets/world-clock.svg")
    args = parser.parse_args()
    now_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(now_utc), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
