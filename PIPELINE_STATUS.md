# PIPELINE_STATUS.md

## Project
TRU Tuition Calculator (PGWP-eligible programs only)

## GitHub Repo
https://github.com/RRS224/tru-fee-calculator

## Current Working State
The stable local pipeline work is in:

`C:\Users\Ranjit\.00 Red Box Studios\Projects\Fee Calculator\tru_fee_pipeline_starter`

The live GitHub repo currently contains:
- `PROJECT_MEMORY.md`
- `index.html`
- `scripts/README.md`
- `scripts/fees_scraper.py`
- `tru_pgwp_programs_master.csv`
- `tru_pgwp_programs_master.json`

The newer local pipeline folder contains:
- `fees_scraper.py`
- `structure_scraper.py`
- `merge_program_data.py`
- `rules_overrides.json`
- `tru_fees_raw.json`
- `README_pipeline.md`

## Important Decisions Already Made
- `fees_scraper.py` is now considered stable for PGWP-focused use.
- Current scraper output is **35 records**.
- Graduate, Post-Bacc, and Undergraduate sections are clean.
- Exception handling is clean enough for PGWP use.
- Water and Wastewater Technology is excluded because it is not PGWP-eligible.
- Do **not** keep tweaking the scraper unless there is a genuinely critical issue.

## Git Situation
A local git repo was initialized inside `tru_fee_pipeline_starter`, and `origin` was pointed to:

`https://github.com/RRS224/tru-fee-calculator.git`

After fetching `origin/main`, it became clear that:
- the local working folder and the GitHub repo do not share the same structure/history
- forcing them together in place is risky

## Chosen Safe Path
The agreed safest method is:

1. Fresh-clone the GitHub repo into a new folder
2. Compare repo structure with the newer local pipeline files
3. Copy the newer pipeline files into the fresh clone cleanly
4. Commit
5. Push
6. Then move on to `rules_overrides.json`

## Last Attempted Command
This failed because the destination folder already existed and was not empty:

```powershell
git clone https://github.com/RRS224/tru-fee-calculator.git tru-fee-calculator-sync
```

## Next Command To Run
```powershell
git clone https://github.com/RRS224/tru-fee-calculator.git tru-fee-calculator-fresh
```

## Immediate Next Actions After Clone
After the fresh clone is created:

1. Inspect repo structure
2. Decide the correct location for:
   - `structure_scraper.py`
   - `merge_program_data.py`
   - `rules_overrides.json`
   - `tru_fees_raw.json`
   - `README_pipeline.md`
3. Copy files into the repo in a clean, intentional structure
4. Review `git status`
5. Commit with a clear message
6. Push to `origin/main`

## Recommended Structure Bias
Unless the repo structure clearly suggests otherwise:
- keep pipeline scripts under `scripts/`
- keep documentation in the repo root or a docs-style location only if already used
- keep generated raw/intermediate data only if it is intentionally part of the repo
- avoid committing unnecessary local-only artifacts

## Next Development Target
After the repo is updated successfully, move next to:

`rules_overrides.json`

This is the next meaningful development step.

## Reminder
Do not get pulled back into reworking `fees_scraper.py` unless a true blocker is discovered.
