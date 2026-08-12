#!/usr/bin/env python3
"""Fetch public GitHub contribution calendar data without tokens."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def parse_count(text: str) -> int:
    match = re.search(r"([\d,]+)\s+contribution", text, re.I)
    return int(match.group(1).replace(",", "")) if match else 0


def tooltip_text(soup: BeautifulSoup, cell) -> str:
    cell_id = cell.get("id")
    if cell_id:
        tip = soup.select_one(f'tool-tip[for="{cell_id}"]')
        if tip:
            return tip.get_text(" ", strip=True)

    tooltip_id = cell.get("aria-describedby") or cell.get("data-tooltip-id")
    if tooltip_id:
        tip = soup.find(id=tooltip_id)
        if tip:
            return tip.get_text(" ", strip=True)

    date = cell.get("data-date")
    if date:
        tip = soup.find(string=re.compile(re.escape(date)))
        if tip:
            return str(tip)
    return cell.get("aria-label", "")


def fetch(username: str) -> dict:
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(
        url,
        headers={
            "Accept": "text/html",
            "User-Agent": "profile-readme-contribution-fetcher",
        },
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        date = cell.get("data-date")
        if not date:
            continue
        level = int(cell.get("data-level") or 0)
        count = parse_count(tooltip_text(soup, cell))
        days.append({"date": date, "level": level, "count": count})

    if not days:
        raise RuntimeError("No contribution cells found. GitHub may have changed the calendar markup.")

    days.sort(key=lambda day: day["date"])
    return {
        "username": username,
        "source": url,
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "yearly_total": sum(day["count"] for day in days),
        "days": days,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("--out", default="data/contributions.json")
    args = parser.parse_args()

    data = fetch(args.username)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} with {len(data['days'])} days and {data['yearly_total']} contributions.")


if __name__ == "__main__":
    main()
