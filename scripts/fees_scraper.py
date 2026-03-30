"""
fees_scraper.py

Scrapes the TRU international fees page and extracts fee rows from the
2026-2027 fee tables into a normalized JSON structure.

Requires:
    pip install requests beautifulsoup4 lxml

Usage:
    python fees_scraper.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag

FEES_URL = "https://www.tru.ca/truworld/future-students/fees.html"
OUTPUT_FILE = Path("fees_scraped.json")
TARGET_YEAR = "2026-2027"


@dataclass
class FeeRow:
    section: str
    year: str
    program_name: str
    raw_fee_text: str
    amount_cad: float | None
    notes: str | None = None


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_currency(text: str) -> float | None:
    m = re.search(r"\$([\d,]+(?:\.\d+)?)", text.replace(" ", ""))
    if not m:
        return None
    return float(m.group(1).replace(",", ""))


def maybe_section_heading(tag: Tag) -> str | None:
    txt = normalize_space(tag.get_text(" ", strip=True))
    if TARGET_YEAR in txt and "Tuition Fees" in txt:
        return txt
    return None


def extract_table_rows(table: Tag, section_name: str) -> list[FeeRow]:
    rows: list[FeeRow] = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        left = normalize_space(cells[0].get_text(" ", strip=True))
        right = normalize_space(cells[1].get_text(" ", strip=True))
        if not left or not right:
            continue
        if left.lower() == "graduate programs" or "total tuition fee" in right.lower():
            continue

        amount = parse_currency(right)
        notes = None
        if "\n" in cells[1].get_text():
            notes = normalize_space(cells[1].get_text(" ", strip=True))

        rows.append(
            FeeRow(
                section=section_name,
                year=TARGET_YEAR,
                program_name=left,
                raw_fee_text=right,
                amount_cad=amount,
                notes=notes,
            )
        )
    return rows


def scrape() -> list[FeeRow]:
    resp = requests.get(FEES_URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    fee_rows: list[FeeRow] = []
    current_section: str | None = None

    all_tags = soup.find_all(["h2", "h3", "button", "summary", "table", "div"])
    for tag in all_tags:
        heading = maybe_section_heading(tag)
        if heading:
            current_section = heading
            continue

        if tag.name == "table" and current_section:
            fee_rows.extend(extract_table_rows(tag, current_section))

    if not fee_rows:
        for table in soup.find_all("table"):
            heading_text = "Unknown section"
            prev = table.find_previous(["h2", "h3", "button", "summary", "div"])
            if prev:
                maybe = maybe_section_heading(prev)
                if maybe:
                    heading_text = maybe
            fee_rows.extend(extract_table_rows(table, heading_text))

    return fee_rows


def main() -> None:
    rows = scrape()
    payload = [asdict(r) for r in rows]
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(payload)} fee rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
