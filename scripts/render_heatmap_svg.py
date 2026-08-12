#!/usr/bin/env python3
"""Render a dark terminal-style animated GitHub contribution heatmap SVG."""

from __future__ import annotations

import argparse
import calendar
import html
import json
from datetime import date
from pathlib import Path


PALETTE = ["#0c2015", "#0f3b24", "#0f6132", "#24a148", "#39d353"]
SAFE_RAIN = "01*+:.abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def svg_text(x: int, y: int, text: str, cls: str = "", extra: str = "") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" {extra}>{html.escape(text)}</text>'


def month_labels(days: list[dict], grid_x: int, grid_y: int, cell: int, gap: int) -> list[str]:
    seen = set()
    labels = []
    for item in days:
        d = date.fromisoformat(item["date"])
        if d.day <= 7 and d.month not in seen:
            seen.add(d.month)
            week = (d - date.fromisoformat(days[0]["date"])).days // 7
            labels.append(svg_text(grid_x + week * (cell + gap), grid_y - 12, calendar.month_abbr[d.month], "month"))
    return labels


def rain_panel(panel_id: str, x: int, y: int, w: int, h: int, cols: int, rows: int) -> str:
    out = [f'<g clip-path="url(#{panel_id})" opacity="0.13">']
    for c in range(cols):
        cx = x + 7 + c * max(10, w // cols)
        chars = "".join(SAFE_RAIN[(c * 17 + r * 7) % len(SAFE_RAIN)] for r in range(rows))
        duration = 5 + (c % 7)
        delay = 0.01 + (c % 11) * 0.11
        out.append(
            f'<text x="{cx}" y="{y - 40}" class="rain">{html.escape(chars)}'
            f'<animate attributeName="y" values="{y - 40};{y + h + 40};{y - 40}" '
            f'keyTimes="0;0.92;1" calcMode="discrete" dur="{duration}s" begin="{delay}s" repeatCount="indefinite"/>'
            "</text>"
        )
    out.append("</g>")
    return "\n".join(out)


def render(data: dict) -> str:
    days = data["days"]
    width, height = 790, 220
    panel_x, panel_y, panel_w, panel_h = 18, 16, 754, 188
    grid_x, grid_y, cell, gap = 56, 74, 10, 3
    username = data.get("username", "github")
    total = str(data.get("yearly_total", 0))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(username)} contribution heatmap">',
        "<defs>",
        f'<clipPath id="panel-clip"><rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="14"/></clipPath>',
        '<linearGradient id="panel-bg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#06170d"/><stop offset="0.55" stop-color="#06110b"/><stop offset="1" stop-color="#020705"/></linearGradient>',
        '<radialGradient id="grid-glow" cx="86%" cy="38%" r="55%"><stop offset="0" stop-color="#1db954" stop-opacity="0.28"/><stop offset="1" stop-color="#1db954" stop-opacity="0"/></radialGradient>',
        '<clipPath id="total-type-clip"><rect x="604" y="165" width="130" height="24"><animate attributeName="width" values="0;0;130" keyTimes="0;0.12;1" dur="2.4s" begin="0.01s" fill="freeze"/></rect></clipPath>',
        '<filter id="glow"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        "</defs>",
        '<rect width="790" height="220" rx="18" fill="#020504"/>',
        f'<rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="14" fill="url(#panel-bg)" stroke="#1f8f4d" stroke-width="1.2"/>',
        f'<rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="14" fill="url(#grid-glow)"/>',
        '<circle cx="39" cy="38" r="5" fill="#ff5f57"/><circle cx="57" cy="38" r="5" fill="#ffbd2e"/><circle cx="75" cy="38" r="5" fill="#28c840"/>',
        rain_panel("panel-clip", panel_x, panel_y + 8, panel_w, panel_h - 14, 42, 18),
        f'<rect x="{panel_x + 10}" y="{panel_y + 44}" width="{panel_w - 20}" height="96" rx="8" fill="#06120b" opacity="0.72"/>',
        svg_text(96, 43, f"{username}@github: ~/contributions", "title"),
        svg_text(45, 181, "Less", "legend"),
    ]

    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{82 + i * 17}" y="170" width="11" height="11" rx="3" fill="{color}" stroke="#255235"/>')
    parts.append(svg_text(170, 181, "More", "legend"))
    parts.extend(month_labels(days, grid_x, grid_y, cell, gap))
    for label, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        parts.append(svg_text(25, grid_y + row * (cell + gap) + 8, label, "weekday"))

    for idx, item in enumerate(days):
        d = date.fromisoformat(item["date"])
        week = (d - date.fromisoformat(days[0]["date"])).days // 7
        weekday = d.weekday()
        github_row = (weekday + 1) % 7
        x = grid_x + week * (cell + gap)
        y = grid_y + github_row * (cell + gap)
        level = max(0, min(4, int(item["level"])))
        color = PALETTE[level]
        delay = 0.01 + week * 0.035 + github_row * 0.012
        flash = "#b7ffcf" if level else "#31543c"
        parts.append(
            f'<g transform="translate({x + cell / 2} {y + cell / 2}) scale(1)">'
            f'<rect x="{-cell / 2}" y="{-cell / 2}" width="{cell}" height="{cell}" rx="3" fill="{color}" stroke="#255239" stroke-width="0.8">'
            f'<animateTransform attributeName="transform" type="scale" values="1;1;1.42;0.86;1" keyTimes="0;0.55;0.7;0.84;1" dur="2.4s" begin="{delay:.3f}s" fill="freeze"/>'
            f'<animate attributeName="fill" values="{color};{color};{flash};{color}" keyTimes="0;0.55;0.68;1" dur="2.4s" begin="{delay:.3f}s" fill="freeze"/>'
            "</rect>"
            "</g>"
        )
        if level >= 3 and (idx * 37) % 29 == 0:
            parts.append(
                f'<path d="M{x+5} {y-1}l2 5 5 2-5 2-2 5-2-5-5-2 5-2z" fill="#d6ffe0" opacity="1">'
                f'<animate attributeName="opacity" values="1;1;0;1;0;0" keyTimes="0;0.02;0.07;0.12;0.18;1" dur="{7 + idx % 5}s" begin="{0.01 + (idx % 13) * .23:.2f}s" repeatCount="indefinite"/>'
                "</path>"
            )
        if level == 4:
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="#a7ffba" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;0.45;0;0" keyTimes="0;0.2;0.24;0.3;1" dur="{5 + idx % 4}s" begin="{0.01 + (idx % 9) * .31:.2f}s" repeatCount="indefinite"/>'
                "</rect>"
            )

    grid_w = 53 * (cell + gap)
    parts.append(
        f'<rect x="{grid_x - 6}" y="{grid_y - 7}" width="28" height="104" fill="#6dff95" opacity="0.0" filter="url(#glow)">'
        f'<animate attributeName="x" values="{grid_x - 8};{grid_x + grid_w}" dur="9s" begin="0.01s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;0.24;0" keyTimes="0;0.45;1" dur="9s" begin="0.01s" repeatCount="indefinite"/>'
        "</rect>"
    )
    parts.append(f'<g clip-path="url(#total-type-clip)">{svg_text(604, 181, f"total: {total}", "total")}</g>')
    parts.append(
        '<rect x="725" y="168" width="9" height="15" fill="#39d353" opacity="0">'
        '<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.1;0.11;0.58;0.59" dur="1s" begin="0.01s" repeatCount="indefinite"/>'
        "</rect>"
    )
    parts.append(
        "<style>"
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
        ".title{fill:#e4ffea;font-size:16px;font-weight:700}.month{fill:#91b89a;font-size:10px}.weekday{fill:#8db899;font-size:11px}.legend{fill:#8db899;font-size:11px}.total{fill:#39d353;font-size:16px;font-weight:700}.rain{fill:#39d353;font-size:10px;writing-mode:vertical-rl}"
        "</style></svg>"
    )
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", default="data/contributions.json")
    parser.add_argument("--out", default="assets/contribution-heatmap.svg")
    args = parser.parse_args()
    data = json.loads(Path(args.infile).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(data), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
