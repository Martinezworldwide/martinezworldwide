#!/usr/bin/env python3
"""Build a neofetch-style SVG info card with SMIL-only animation."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


def line(y: int, label: str, value: str) -> str:
    return (
        f'<text x="148" y="{y}" class="key">{html.escape(label)}</text>'
        f'<text x="232" y="{y}" class="value">{html.escape(value)}</text>'
    )


def render(username: str, height: int, width: int, os_name: str, stack: str, ships: str, socials: str) -> str:
    rows = [
        ("OS", os_name),
        ("Stack", stack),
        ("Ship", ships),
        ("Socials", socials),
    ]
    body = []
    y = 92
    for label, value in rows:
        body.append(line(y, label, value))
        y += 28

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(username)} neofetch info card">
<defs>
  <clipPath id="card-clip"><rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14"/></clipPath>
</defs>
<rect width="{width}" height="{height}" rx="14" fill="#050807"/>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="#07130d" stroke="#1f6f43"/>
<g clip-path="url(#card-clip)" opacity="0.20">
  <text x="18" y="-20" class="rain">0101make ship push build git svg smil terminal</text>
  <animateTransform attributeName="transform" type="translate" values="0 0;0 {height + 80};0 0" keyTimes="0;0.92;1" calcMode="discrete" dur="8s" begin="0.01s" repeatCount="indefinite"/>
</g>
<circle cx="22" cy="22" r="5" fill="#ff5f57"/><circle cx="40" cy="22" r="5" fill="#ffbd2e"/><circle cx="58" cy="22" r="5" fill="#28c840"/>
<text x="76" y="27" class="title">{html.escape(username)}@github</text>
<text x="28" y="82" class="logo">       .</text>
<text x="28" y="102" class="logo">      / \\</text>
<text x="28" y="122" class="logo">     / _ \\</text>
<text x="28" y="142" class="logo">    / ___ \\</text>
<text x="28" y="162" class="logo">   /_/   \\_\\</text>
<text x="148" y="58" class="name">{html.escape(username)}</text>
{''.join(body)}
<text x="28" y="{height - 29}" class="prompt">$ echo keep_shipping</text>
<rect x="218" y="{height - 42}" width="10" height="17" fill="#39d353" opacity="0">
  <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.1;0.11;0.58;0.59" dur="1s" begin="0.01s" repeatCount="indefinite"/>
</rect>
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.title{{fill:#d7ffe3;font-size:13px}}.name{{fill:#39d353;font-size:18px;font-weight:700}}
.logo{{fill:#39d353;font-size:18px}}.key{{fill:#8fd19e;font-size:13px}}.value{{fill:#d7ffe3;font-size:13px}}
.prompt{{fill:#39d353;font-size:14px}}.rain{{fill:#39d353;font-size:11px;writing-mode:vertical-rl}}
</style>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="USERNAME")
    parser.add_argument("--height", type=int, default=240)
    parser.add_argument("--width", type=int, default=360)
    parser.add_argument("--os", default="macOS / Linux")
    parser.add_argument("--stack", default="Python, JS, SVG, CI")
    parser.add_argument("--ships", default="tools, automations, art")
    parser.add_argument("--socials", default="GitHub, LinkedIn, X")
    parser.add_argument("--out", default="assets/info-card.svg")
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(args.username, args.height, args.width, args.os, args.stack, args.ships, args.socials), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
