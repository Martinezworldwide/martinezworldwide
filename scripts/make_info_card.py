#!/usr/bin/env python3
"""Build a neofetch-style SVG info card with SMIL-only animation."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


def wrap(value: str, width: int = 14) -> list[str]:
    words = value.replace(",", " ,").split()
    lines: list[str] = []
    current = ""
    for word in words:
        word = word.replace(" ,", ",")
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines[:2]


def line(y: int, label: str, value: str) -> tuple[str, int]:
    lines = wrap(value)
    body = [f'<text x="150" y="{y}" class="key">{html.escape(label)}</text>']
    body.append(f'<text x="204" y="{y}" class="value">{html.escape(lines[0])}</text>')
    if len(lines) > 1:
        body.append(f'<text x="204" y="{y + 16}" class="value muted">{html.escape(lines[1])}</text>')
        return "".join(body), 38
    return "".join(body), 27


def render(username: str, height: int, width: int, os_name: str, stack: str, ships: str, socials: str) -> str:
    rows = [
        ("OS", os_name),
        ("Stack", stack),
        ("Ship", ships),
        ("Socials", socials),
    ]
    body = []
    y = 104
    for label, value in rows:
        rendered, advance = line(y, label, value)
        body.append(rendered)
        y += advance

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(username)} neofetch info card">
<defs>
  <clipPath id="card-clip"><rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14"/></clipPath>
  <linearGradient id="card-bg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#06190f"/><stop offset="1" stop-color="#020806"/></linearGradient>
  <radialGradient id="card-glow" cx="75%" cy="20%" r="70%"><stop offset="0" stop-color="#39d353" stop-opacity="0.18"/><stop offset="1" stop-color="#39d353" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{width}" height="{height}" rx="14" fill="#050807"/>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="url(#card-bg)" stroke="#1f8f4d" stroke-width="1.2"/>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="url(#card-glow)"/>
<g clip-path="url(#card-clip)" opacity="0.13">
  <text x="18" y="-20" class="rain">0101 make ship build git svg smil terminal</text>
  <animateTransform attributeName="transform" type="translate" values="0 0;0 {height + 80};0 0" keyTimes="0;0.92;1" calcMode="discrete" dur="8s" begin="0.01s" repeatCount="indefinite"/>
</g>
<circle cx="18" cy="20" r="4.5" fill="#ff5f57"/><circle cx="34" cy="20" r="4.5" fill="#ffbd2e"/><circle cx="50" cy="20" r="4.5" fill="#28c840"/>
<text x="64" y="24" class="title">{html.escape(username)}@github</text>
<text x="24" y="91" class="logo">       .</text>
<text x="24" y="112" class="logo">      / \\</text>
<text x="24" y="133" class="logo">     / _ \\</text>
<text x="24" y="154" class="logo">    / ___ \\</text>
<text x="24" y="175" class="logo">   /_/   \\_\\</text>
<text x="150" y="70" class="name">{html.escape(username)}</text>
<line x1="150" y1="82" x2="{width - 24}" y2="82" stroke="#245b37"/>
{''.join(body)}
<text x="24" y="{height - 29}" class="prompt">$ echo keep_shipping</text>
<rect x="203" y="{height - 42}" width="9" height="16" fill="#39d353" opacity="0">
  <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.1;0.11;0.58;0.59" dur="1s" begin="0.01s" repeatCount="indefinite"/>
</rect>
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.title{{fill:#e4ffea;font-size:10px;font-weight:700}}.name{{fill:#39d353;font-size:13px;font-weight:700}}
.logo{{fill:#39d353;font-size:19px}}.key{{fill:#8fd19e;font-size:11px;font-weight:700}}.value{{fill:#d7ffe3;font-size:10px}}.muted{{fill:#a7d9b2}}
.prompt{{fill:#39d353;font-size:14px}}.rain{{fill:#39d353;font-size:11px;writing-mode:vertical-rl}}
</style>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="USERNAME")
    parser.add_argument("--height", type=int, default=330)
    parser.add_argument("--width", type=int, default=300)
    parser.add_argument("--os", default="macOS + Linux")
    parser.add_argument("--stack", default="Python / JS / SVG / CI")
    parser.add_argument("--ships", default="tools + automation")
    parser.add_argument("--socials", default="GitHub / LinkedIn / X")
    parser.add_argument("--out", default="assets/info-card.svg")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(args.username, args.height, args.width, args.os, args.stack, args.ships, args.socials), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
