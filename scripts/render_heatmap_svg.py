#!/usr/bin/env python3
"""Render a dark terminal-style animated GitHub contribution heatmap SVG."""

from __future__ import annotations

import argparse
import calendar
import html
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path


PALETTE = ["#102319", "#0e4429", "#006d32", "#26a641", "#39d353"]
SAFE_RAIN = "01*+:.abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def svg_text(x: int, y: int, text: str, cls: str = "", extra: str = "") -> str:
    return f'<text x="{x}" y="{y}" class="{cls}" {extra}>{html.escape(text)}</text>'


def month_labels(days: list[dict], grid_x: int, cell: int, gap: int) -> list[str]:
    seen = set()
    labels = []
    for item in days:
        d = date.fromisoformat(item["date"])
        if d.day <= 7 and d.month not in seen:
            seen.add(d.month)
            week = (d - date.fromisoformat(days[0]["date"])).days // 7
            labels.append(svg_text(grid_x + week * (cell + gap), 73, calendar.month_abbr[d.month], "label"))
    return labels


def rain_panel(panel_id: str, x: int, y: int, w: int, h: int, cols: int, rows: int) -> str:
    out = [f'<g clip-path="url(#{panel_id})" opacity="0.24">']
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
    by_weekday = defaultdict(int)
    width, height = 790, 300
    grid_x, grid_y, cell, gap = 78, 92, 11, 3
    username = data.get("username", "github")
    total = str(data.get("yearly_total", 0))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(username)} contribution heatmap">',
        "<defs>",
        '<clipPath id="panel-clip"><rect x="14" y="14" width="762" height="272" rx="16"/></clipPath>',
        '<clipPath id="total-type-clip"><rect x="525" y="246" width="150" height="24"><animate attributeName="width" values="0;0;150" keyTimes="0;0.12;1" dur="2.4s" begin="0.01s" fill="freeze"/></rect></clipPath>',
        '<filter id="glow"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        "</defs>",
        '<rect width="790" height="300" rx="18" fill="#050807"/>',
        '<rect x="14" y="14" width="762" height="272" rx="16" fill="#07130d" stroke="#1f6f43"/>',
        '<circle cx="34" cy="34" r="5" fill="#ff5f57"/><circle cx="52" cy="34" r="5" fill="#ffbd2e"/><circle cx="70" cy="34" r="5" fill="#28c840"/>',
        rain_panel("panel-clip", 14, 14, 762, 272, 58, 28),
        svg_text(92, 39, f"{username}@github: ~/contributions", "title"),
        svg_text(22, 263, "Less", "label"),
    ]

    for i, color in enumerate(PALETTE):
        parts.append(f'<rect x="{58 + i * 17}" y="252" width="11" height="11" rx="3" fill="{color}" stroke="#24452f"/>')
    parts.append(svg_text(146, 263, "More", "label"))
    parts.extend(month_labels(days, grid_x, cell, gap))
    for label, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
        parts.append(svg_text(35, grid_y + row * (cell + gap) + 9, label, "label"))

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
            f'<rect x="{-cell / 2}" y="{-cell / 2}" width="{cell}" height="{cell}" rx="3" fill="{color}" stroke="#1f3528">'
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
        f'<rect x="{grid_x - 8}" y="{grid_y - 8}" width="32" height="118" fill="#6dff95" opacity="0.0" filter="url(#glow)">'
        f'<animate attributeName="x" values="{grid_x - 8};{grid_x + grid_w}" dur="9s" begin="0.01s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;0.24;0" keyTimes="0;0.45;1" dur="9s" begin="0.01s" repeatCount="indefinite"/>'
        "</rect>"
    )
    parts.append(f'<g clip-path="url(#total-type-clip)">{svg_text(525, 263, f"total: {total}", "total")}</g>')
    parts.append(
        '<rect x="676" y="250" width="9" height="15" fill="#39d353" opacity="0">'
        '<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.1;0.11;0.58;0.59" dur="1s" begin="0.01s" repeatCount="indefinite"/>'
        "</rect>"
    )
    parts.append(
        "<style>"
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
        ".title{fill:#d7ffe3;font-size:15px}.label{fill:#7ca98a;font-size:11px}.total{fill:#39d353;font-size:15px}.rain{fill:#39d353;font-size:10px;writing-mode:vertical-rl}"
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
