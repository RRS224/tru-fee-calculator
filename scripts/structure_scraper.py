"""
structure_scraper.py

Scrapes the TRU international programs page, then visits linked program pages
to collect best-effort structure information.

Requires:
    pip install requests beautifulsoup4 lxml

Usage:
    python structure_scraper.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

PROGRAMS_URL = "https://www.tru.ca/truworld/future-students/programs.html"
OUTPUT_FILE = Path("structures_scraped.json")


@dataclass
class ProgramStructure:
    program_name: str
    program_url: str
    pgwp_eligible_hint: bool | None
    duration_text: str | None
    total_credits: int | None
    total_courses: int | None
    semesters_declared: int | None
    notes: list[str]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_duration(text: str) -> str | None:
    m = re.search(r"(\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?\s*(?:years?|year|months?|month|semesters?))", text, re.I)
    return m.group(1) if m else None


def extract_total_credits(text: str) -> int | None:
    m = re.search(r"(\d+)\s+credits?", text, re.I)
    return int(m.group(1)) if m else None


def credits_to_courses(credits: int | None) -> int | None:
    if credits and credits % 3 == 0:
        return credits // 3
    return None


def extract_semesters(text: str) -> int | None:
    m = re.search(r"(\d+)\s+semesters?", text, re.I)
    return int(m.group(1)) if m else None


def extract_program_links(soup: BeautifulSoup) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for a in soup.find_all("a", href=True):
        name = normalize_space(a.get_text(" ", strip=True))
        href = a["href"].strip()
        if not name:
            continue
        if "/truworld/future-students/" in href:
            continue
        if href.startswith("#"):
            continue
        if "/programs/" not in href and "/catalogue/" not in href and "/degrees/" not in href:
            continue
        links.append((name, urljoin(PROGRAMS_URL, href)))

    dedup = {}
    for name, url in links:
        dedup[(name, url)] = None
    return list(dedup.keys())


def scrape_program_page(name: str, url: str) -> ProgramStructure:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    page_text = normalize_space(soup.get_text(" ", strip=True))

    duration_text = extract_duration(page_text)
    total_credits = extract_total_credits(page_text)
    total_courses = credits_to_courses(total_credits)
    semesters = extract_semesters(page_text)

    notes: list[str] = []
    for pattern in [
        r"PGWP",
        r"post-graduation work permit",
        r"course-based",
        r"thesis",
        r"project option",
    ]:
        m = re.search(pattern, page_text, re.I)
        if m:
            notes.append(m.group(0))

    return ProgramStructure(
        program_name=name,
        program_url=url,
        pgwp_eligible_hint=None,
        duration_text=duration_text,
        total_credits=total_credits,
        total_courses=total_courses,
        semesters_declared=semesters,
        notes=notes,
    )


def main() -> None:
    resp = requests.get(PROGRAMS_URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    program_links = extract_program_links(soup)
    results = []
    for name, url in program_links:
        try:
            results.append(asdict(scrape_program_page(name, url)))
            print(f"OK  {name}")
        except Exception as exc:
            results.append(
                asdict(
                    ProgramStructure(
                        program_name=name,
                        program_url=url,
                        pgwp_eligible_hint=None,
                        duration_text=None,
                        total_credits=None,
                        total_courses=None,
                        semesters_declared=None,
                        notes=[f"SCRAPE_ERROR: {exc}"],
                    )
                )
            )
            print(f"ERR {name}: {exc}")

    OUTPUT_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(results)} program structures to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
