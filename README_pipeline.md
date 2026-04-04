# TRU Fee + Structure Pipeline

This starter bundle sets up a clean, data-driven pipeline for the TRU Tuition Calculator.

## Purpose

Use two scrapers and one merge step:

1. `fees_scraper.py`
   - Reads the TRU international fees page
   - Extracts fee tables by section and year
   - Produces `fees_scraped.json`

2. `structure_scraper.py`
   - Reads the TRU international programs page
   - Visits each linked program page
   - Extracts best-effort structure fields such as duration, credits, and semester notes
   - Produces `structures_scraped.json`

3. `merge_program_data.py`
   - Merges scraped fees + scraped structure + manual overrides
   - Produces `tru_pgwp_programs_master.generated.json`

4. `rules_overrides.json`
   - Manual exceptions and presentation rules
   - Example: MBA shown as 5 semesters, ignore 1-year MBA

## Why this design

The TRU fees page should be the single source of truth for fee amounts.
The TRU programs page should be the starting list for international / PGWP-facing programs.
Some program structures will still need manual overrides.

## Suggested workflow

1. Run:
   python fees_scraper.py

2. Run:
   python structure_scraper.py

3. Review:
   rules_overrides.json

4. Run:
   python merge_program_data.py

5. Copy the generated JSON into the website repo.

## Recommended folder placement in your repo

tru-fee-calculator/
- index.html
- tru_pgwp_programs_master.json
- scripts/
  - fees_scraper.py
  - structure_scraper.py
  - merge_program_data.py
  - rules_overrides.json
  - README_pipeline.md

## Notes

- This starter bundle is conservative.
- It captures what is explicit.
- It avoids guessing.
- It leaves room for manual overrides where TRU pages are not uniform.
