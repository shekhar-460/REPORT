# IRCTC Takedown Report

Generate the **IRCTC Daily Cyber Threat Suppression & Takedown Status Report** from CSV data as HTML and optional PDF. Supports one-off generation, automation (e.g. cron), and a web upload interface.

---

## Features

- **CSV-driven**: Report content comes from four CSVs (`report_meta`, `taken_down`, `under_review`, `in_progress`).
- **HTML + PDF**: Jinja2 template renders HTML; Playwright produces PDF with print-friendly styling.
- **Automation**: Optional script updates report date to today and generates HTML + PDF (suitable for cron).
- **Web upload**: Flask app to upload CSVs and download the generated report (HTML/PDF).

---

## Directory structure

```
REPORT/
├── README.md              # This file
├── QUICKSTART.md          # Minimal steps to first report
├── requirements.txt
├── Makefile               # report, report-pdf, open, auto, upload, clean
├── run_report.sh          # One-command: data → output (HTML + PDF)
├── .gitignore
│
├── src/irctc_report/      # Python package
│   ├── __init__.py        # build_context, render_html, convert_to_pdf
│   ├── constants.py       # Default key outcomes
│   ├── loader.py          # load_meta, load_table, build_context
│   ├── render.py          # render_html (Jinja2)
│   └── pdf.py             # convert_to_pdf (Playwright)
│
├── scripts/               # Entry points (run with python -m scripts.<name>)
│   ├── generate_report.py # CLI: generate from data/ → output/
│   ├── automate_report.py # Optional date update + generate (cron)
│   ├── app_upload.py      # Flask: upload CSVs → download report
│   └── to_pdf.py          # Convert any HTML file to PDF
│
├── templates/
│   └── IRCTC_Takedown_Report_template.html
│
├── data/                  # Input CSVs
│   ├── report_meta.csv    # Required: report metadata and metrics text
│   ├── taken_down.csv
│   ├── under_review.csv
│   └── in_progress.csv
│
├── assets/
│   └── main_logo.png      # Copied to output/ when generating
│
└── output/                # Generated HTML, PDF, and copied logo
    └── .gitkeep
```

---

## Requirements

- **Python 3.10+**
- **Dependencies**: `jinja2`, `flask` (for upload app), `playwright` (for PDF)
- **Playwright browser** (for PDF): `playwright install chromium`

---

## CSV schema

### 1. `data/report_meta.csv` (required)

One row. Columns:

| Column | Description | Example |
|--------|-------------|--------|
| `report_date` | Report date (display) | `05 February 2026` |
| `prepared_by` | Preparing organisation | `Sveltetech Technologies Pvt. Ltd.` |
| `reporting_window` | Reporting period text | `Rolling (Last 24 hours + Cumulative Status)` |
| `newly_completed_domain` | Domain completed in last 24h | `irtctc.co.in` |
| `newly_under_review_domain` | Domain newly under review | `irctc.co.com` |
| `reactivated_domains` | Semicolon-separated list | `domain1; domain2; domain3` |
| `threat_severity` | Severity text | `Predominantly High / Critical` |
| `dominant_threat_type` | Threat type text | `Phishing Websites` |
| `risk_exposure` | Risk exposure text | `Nil (Closed) / Controlled (Open)` |
| `closing_note` | Closing paragraph (can contain commas in quotes) | Full sentence(s). |

### 2. `data/taken_down.csv`

| Column | Description |
|--------|-------------|
| `domain_url` | Domain or URL |
| `reported_on` | Date reported |
| `last_updated` | Last updated date |
| `threat_category` | `Phishing Website` \| `Typosquatted Domain` \| `Fake Mobile App` |
| `remarks` | Free text (e.g. "Domain or app has been successfully removed.") |

### 3. `data/under_review.csv`

Same as above but **no** `last_updated`. Columns: `domain_url`, `reported_on`, `threat_category`, `remarks`.

### 4. `data/in_progress.csv`

Same columns as `under_review.csv`.

---

## How to run

All commands are from the **project root**. The Makefile and `run_report.sh` set `PYTHONPATH=src` so the `irctc_report` package is found.

### One command (HTML + PDF)

```bash
./run_report.sh
# or open PDF after generating:
./run_report.sh --open
```

Uses `data/` and writes to `output/`. Override CSV directory: `REPORT_DATA_DIR=/path/to/csvs ./run_report.sh`.

### Makefile

```bash
make report       # HTML only → output/
make report-pdf   # HTML + PDF → output/
make open        # report-pdf + open PDF
make auto        # Set report_date to today, then HTML + PDF
make upload      # Start Flask upload app (http://127.0.0.1:5000)
make clean       # Remove generated files in output/
```

### Python module (explicit)

```bash
export PYTHONPATH=src
.venv/bin/python -m scripts.generate_report --data-dir data --output output/IRCTC_Takedown_Report_generated.html
.venv/bin/python -m scripts.generate_report --data-dir data --output output/IRCTC_Takedown_Report_generated.html --pdf
```

### Convert any HTML to PDF

```bash
PYTHONPATH=src .venv/bin/python -m scripts.to_pdf path/to/file.html
```

### Web upload app

```bash
PYTHONPATH=src .venv/bin/python -m scripts.app_upload
# or: make upload
```

Then open **http://127.0.0.1:5000**, upload the four CSVs, optionally check “Also generate PDF”, and download the report.

---

## Automation (cron)

To generate the report daily with report date set to that day:

```bash
# Example: every day at 9:00 AM (adjust path)
0 9 * * * cd /path/to/REPORT && PYTHONPATH=src .venv/bin/python -m scripts.automate_report >> report_cron.log 2>&1
```

Options:

- **Default**: Updates `report_date` in `data/report_meta.csv` to **today**, then generates HTML + PDF to `output/`.
- `--no-update-date`: Do not change report date; generate from existing CSVs only.
- `--html-only`: Generate HTML only (no PDF; useful if Playwright is not installed).

---

## Output

- **HTML**: `output/IRCTC_Takedown_Report_generated.html`
- **PDF**: `output/IRCTC_Takedown_Report_generated.pdf` (when `--pdf` or “Also generate PDF” is used)
- **Logo**: `output/main_logo.png` (copied from `assets/` so the HTML can load it)

---

## License and attribution

Report format and content are for IRCTC cyber threat suppression and takedown reporting. CSV data and branding are the responsibility of the report owner.
