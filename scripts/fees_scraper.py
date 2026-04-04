#!/usr/bin/env python3
"""
fees_scraper.py

Scrapes the TRU international fees page and extracts 2026-2027 tuition totals for:
- Graduate Programs
- Post-Baccalaureate Diplomas
- Undergraduate Programs
- Exceptions

This scraper is intended for a PGWP-focused pipeline, so it keeps the fee data
clean and current, while allowing later filtering/override logic.

Output format:
[
  {
    "program_name": "Master of Business Administration",
    "total_tuition_cad": 57235,
    "section": "Graduate Programs"
  },
  ...
]
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

FEES_URL = "https://www.tru.ca/truworld/future-students/fees.html"
OUTPUT_FILE = Path("tru_fees_raw.json")


def fetch_page_text(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)


def clean_currency_to_int(value: str) -> int:
    return int(re.sub(r"[^\d]", "", value))


def normalize_program_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name).strip()
    name = name.replace("’", "'")
    return name


def is_money(line: str) -> bool:
    return bool(re.fullmatch(r"\$[\d,]+", line.strip()))


def split_into_sections(text: str) -> Dict[str, List[str]]:
    lines = text.splitlines()

    sections: Dict[str, List[str]] = {
        "Graduate Programs": [],
        "Post-Baccalaureate Diplomas": [],
        "Undergraduate Programs": [],
        "Exceptions": [],
    }

    current_section: Optional[str] = None

    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        combined = f"{line} {next_line}".strip()

        # Start sections
        if "Graduate Programs Tuition Fees (2026-2027)" in combined:
            current_section = "Graduate Programs"
            continue

        if "Post-Baccalaureate Diplomas Tuition Fees (2026-2027)" in combined:
            current_section = "Post-Baccalaureate Diplomas"
            continue

        if "Undergraduate Programs Tuition Fees (2026-2027)" in combined:
            current_section = "Undergraduate Programs"
            continue

        if line.strip().startswith("Exceptions:"):
            current_section = "Exceptions"
            continue

        # Stop conditions
        if current_section == "Graduate Programs":
            if "Fees (2025-2026)" in combined:
                current_section = None
                continue

        if current_section == "Post-Baccalaureate Diplomas":
            if "Fees (2025-2026)" in combined:
                current_section = None
                continue

        if current_section == "Exceptions":
            if "English for Academic Purposes (EAP) Tuition Fees" in combined:
                current_section = None
                continue
            if "Housing Fees" in combined:
                current_section = None
                continue
            if "Frequently Asked Questions" in combined:
                current_section = None
                continue
            if "2025/26 $/per credit rate" in combined:
                current_section = None
                continue

        if current_section is not None:
            sections[current_section].append(line)

    return sections


def parse_graduate_block(lines: List[str]) -> List[Dict]:
    results: List[Dict] = []

    skip_exact = {
        "Graduate Programs",
        "Total Tuition Fee",
    }

    i = 0
    while i < len(lines):
        line = lines[i]

        if line in skip_exact:
            i += 1
            continue

        name_parts: List[str] = []

        while i < len(lines):
            current = lines[i]

            if current in skip_exact:
                i += 1
                continue

            if is_money(current):
                break

            if current.startswith("Project option:") or current.startswith("Thesis option:"):
                break

            name_parts.append(current)
            i += 1

        if not name_parts:
            i += 1
            continue

        program_name = " ".join(name_parts)
        program_name = re.sub(r"\bCompletion requires minimum of .*?$", "", program_name).strip()
        program_name = re.sub(r"\b4th semester may be needed for .*?$", "", program_name).strip()
        program_name = normalize_program_name(program_name)

        if not program_name:
            continue

        total_fee: Optional[int] = None

        if i < len(lines):
            current = lines[i]

            if current.startswith("Project option:"):
                m = re.search(r"\$[\d,]+", current)
                if m:
                    total_fee = clean_currency_to_int(m.group())
                i += 1
                if i < len(lines) and lines[i].startswith("Thesis option:"):
                    i += 1

            elif is_money(current):
                total_fee = clean_currency_to_int(current)
                i += 1

        if total_fee is None:
            continue

        results.append(
            {
                "program_name": program_name,
                "total_tuition_cad": total_fee,
                "section": "Graduate Programs",
            }
        )

    return results


def parse_tabular_block(lines: List[str], section_name: str) -> List[Dict]:
    results: List[Dict] = []

    skip_exact = {
        "Fees (2026-2027)",
        "Post-Baccalaureate Diplomas",
        "Programs",
        "2026/27 $ per credit rate",
        "2026/27 $ per course",
        "Number of courses",
        "Total tuition fees",
        "required to enrol in every semester:",
    }

    filtered: List[str] = []
    for line in lines:
        if line in skip_exact:
            continue
        if line.startswith("Tuition fees for the programs listed below may vary"):
            continue
        if "Fees (2025-2026)" in line:
            break
        if "2025/26 $/per credit rate" in line:
            break
        if "English for Academic Purposes (EAP) Tuition Fees" in line:
            break
        if "Housing Fees" in line:
            break
        if "Frequently Asked Questions" in line:
            break
        filtered.append(line)

    i = 0
    while i + 4 < len(filtered):
        program_name = filtered[i]
        per_credit = filtered[i + 1]
        per_course = filtered[i + 2]
        _num_courses = filtered[i + 3]
        total_fee = filtered[i + 4]

        if is_money(per_credit) and is_money(per_course) and is_money(total_fee):
            results.append(
                {
                    "program_name": normalize_program_name(program_name),
                    "total_tuition_cad": clean_currency_to_int(total_fee),
                    "section": section_name,
                }
            )
            i += 5
        else:
            i += 1

    return results


def dedupe_rows(rows: List[Dict]) -> List[Dict]:
    seen = set()
    deduped: List[Dict] = []

    for row in rows:
        key = (row["section"], row["program_name"], row["total_tuition_cad"])
        if key not in seen:
            seen.add(key)
            deduped.append(row)

    return deduped


def scrape_fees() -> List[Dict]:
    text = fetch_page_text(FEES_URL)
    sections = split_into_sections(text)

    rows: List[Dict] = []
    rows.extend(parse_graduate_block(sections["Graduate Programs"]))
    rows.extend(parse_tabular_block(sections["Post-Baccalaureate Diplomas"], "Post-Baccalaureate Diplomas"))
    rows.extend(parse_tabular_block(sections["Undergraduate Programs"], "Undergraduate Programs"))
    rows.extend(parse_tabular_block(sections["Exceptions"], "Exceptions"))

    return dedupe_rows(rows)


def main() -> None:
    rows = scrape_fees()

    OUTPUT_FILE.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Saved {len(rows)} records to {OUTPUT_FILE}")
    for row in rows:
        print(f"{row['section']}: {row['program_name']} -> ${row['total_tuition_cad']:,}")


if __name__ == "__main__":
    main()