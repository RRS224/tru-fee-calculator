"""
fees_scraper.py (FIXED VERSION)

Extracts program fees from TRU fees page using text parsing (not tables)
"""

import requests
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

FEES_URL = "https://www.tru.ca/truworld/future-students/fees.html"
OUTPUT_FILE = Path("fees_scraped.json")


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_section(text, start_marker, end_marker):
    start = text.find(start_marker)
    if start == -1:
        return ""

    end = text.find(end_marker, start) if end_marker else -1
    if end == -1:
        return text[start:]
    return text[start:end]


def extract_grad_programs(section_text):
    results = []

    # pattern: Program Name $Amount
    pattern = r"([A-Za-z0-9 ,\-()]+?)\s*\$([\d,]+)"

    matches = re.findall(pattern, section_text)

    for name, amount in matches:
        name = clean_text(name)

        # skip junk lines
        if len(name) < 5:
            continue
        if "Tuition Fees" in name:
            continue
        if "Total Tuition Fee" in name:
            continue
        if "Graduate Programs" in name:
            continue

        results.append({
            "program_name": name,
            "total_tuition_cad": int(amount.replace(",", "")),
            "section": "Graduate Programs"
        })

    return results


def scrape():
    response = requests.get(FEES_URL)
    soup = BeautifulSoup(response.text, "lxml")

    full_text = clean_text(soup.get_text())

    # isolate Graduate section
    grad_section = extract_section(
        full_text,
        "Graduate Programs Tuition Fees (2026-2027)",
        "Post-Baccalaureate Diplomas Tuition Fees"
    )

    grad_programs = extract_grad_programs(grad_section)

    return grad_programs


def main():
    data = scrape()

    OUTPUT_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    print(f"Extracted {len(data)} graduate programs.")


if __name__ == "__main__":
    main()
