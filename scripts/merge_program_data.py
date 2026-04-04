"""
merge_program_data.py

Merges:
- fees_scraped.json
- structures_scraped.json
- rules_overrides.json

Outputs:
- tru_pgwp_programs_master.generated.json
"""

from __future__ import annotations

import json
from pathlib import Path

FEES_FILE = Path("fees_scraped.json")
STRUCTURES_FILE = Path("structures_scraped.json")
OVERRIDES_FILE = Path("rules_overrides.json")
OUTPUT_FILE = Path("tru_pgwp_programs_master.generated.json")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm(text: str | None) -> str:
    return (text or "").strip().lower()


def main() -> None:
    fees = load_json(FEES_FILE)
    structures = load_json(STRUCTURES_FILE)
    overrides = load_json(OVERRIDES_FILE)

    structure_map = {norm(x["program_name"]): x for x in structures}
    override_map = {norm(x["program_name"]): x for x in overrides.get("program_overrides", [])}

    merged = []
    for fee in fees:
        key = norm(fee["program_name"])
        structure = structure_map.get(key, {})
        override = override_map.get(key, {})

        semesters = override.get("semesters_display")
        if semesters is None:
            semesters = structure.get("semesters_declared")

        row = {
            "program_name": fee["program_name"],
            "fees_section": fee["section"],
            "fee_year": fee["year"],
            "raw_fee_text": fee["raw_fee_text"],
            "total_tuition_cad": fee["amount_cad"],
            "duration_text": override.get("duration_text_override") or structure.get("duration_text"),
            "total_credits": structure.get("total_credits"),
            "total_courses": structure.get("total_courses"),
            "semesters_declared": structure.get("semesters_declared"),
            "semesters_display": semesters,
            "display_mode": override.get("display_mode", "standard"),
            "semester_plan": override.get("semester_plan"),
            "exclude_from_search": override.get("exclude_from_search", False),
            "notes": [n for n in [
                fee.get("notes"),
                *structure.get("notes", []),
                *override.get("notes", []),
            ] if n],
        }
        merged.append(row)

    OUTPUT_FILE.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(merged)} merged rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
