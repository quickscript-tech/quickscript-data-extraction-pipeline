# quickscript-data-extraction-pipeline

## What this is
A reproducible, offline-capable Python CLI mini-pipeline that:
- extracts structured product data from a **local HTML fixture** (no internet scraping),
- normalizes + validates it,
- exports **JSON + CSV**,
- generates a human-readable **summary report**,
- writes a **run log**.

This is built as a small but realistic “client deliverable” style tool: deterministic outputs, explicit validation rules, and a test that exercises the pipeline end-to-end.

## How to run (Debian)
```bash
# from repo root
sudo apt-get update
sudo apt-get install -y python3-venv

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# install dependencies + package (editable)
python -m pip install -e .

# run the pipeline
python -m qdep --input fixtures/sample_page.html --outdir sample_output

# Outputs

## Running the command above produces:
sample_output/output.json  (valid items + errors list)
sample_output/output.csv   (valid items only)
sample_output/summary.txt  (counts + category breakdown + basic stats)
sample_output/run.log      (start/end, paths, counts, brief validation errors)

# Why clients care
- Deterministic, audit-friendly output: stable IDs, stable ordering, consistent formatting.
- Validation & error segregation: bad records don’t poison downstream CSV exports.
- Portable CLI: runs on clean Debian without GUIs or external services.
- Useful reporting: gives quick business insight (counts, categories, price stats, rating averages).
- Tested: includes an end-to-end pipeline test to reduce regressions.

# Limitations (offline demo)
- The HTML is a controlled fixture, not live web scraping.
- Parsing rules target a known “product card” structure (typical client scenario: fixed templates).
- Currency detection is symbol-based for this demo (extendable to more formats).

# Suggested screenshots for Upwork/Fiverr (take these 4)
1. Terminal: python -m qdep ... run showing “extracted / valid / invalid” counts.
2. sample_output/summary.txt opened (clear stats + category breakdown).
3. A snippet of sample_output/output.json showing items and errors.
4. sample_output/run.log showing start/end + brief validation errors.