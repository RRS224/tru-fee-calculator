TRU Tuition Calculator – Project Memory
Objective

Build a clean, reliable, PGWP-only tuition calculator for TRU, hosted on GitHub Pages.

Core Principles
Fees must come ONLY from:
https://www.tru.ca/truworld/future-students/fees.html
Do NOT use approximate tables
Do NOT guess missing values
If unclear → manual override
Display Rules
Show TOTAL tuition first
Then SEMESTER breakdown
Do NOT show:
per-credit
per-course
MBA Rule (Critical)
Use ONLY 2-year MBA
Ignore 1-year MBA
Internally:
Year 1 = GDBA
Year 2 = MBA
Display:
5 semesters (2 + 3)
Never mention "GDBA"
Graduate Programs
No year-wise display
Only:
total
semester breakdown
Data Architecture

Pipeline approach:

fees_scraper.py → fees
structure_scraper.py → structure
rules_overrides.json → exceptions
merge_program_data.py → final JSON
Current Status
GitHub Pages working
JSON loading working
Deterministic search working
Graduate scraper working cleanly
Next Steps
Extend scraper:
Post-bacc
Undergraduate
Exceptions
Build structure scraper
Merge pipeline
Connect to UI
Notes
This is a data-driven system, not a calculator
Accuracy > automation
Manual overrides are acceptable and necessary
