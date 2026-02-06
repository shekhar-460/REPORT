#!/usr/bin/env python3
"""
Fully automated report: optionally set report_date to today, then generate HTML + PDF.

Suitable for cron. Example:
  0 9 * * * cd /path/to/REPORT && .venv/bin/python -m scripts.automate_report >> report_cron.log 2>&1
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_src = PROJECT_ROOT / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

DATA_DIR = PROJECT_ROOT / "data"
META_CSV = DATA_DIR / "report_meta.csv"
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "IRCTC_Takedown_Report_template.html"
OUTPUT_HTML = PROJECT_ROOT / "output" / "IRCTC_Takedown_Report_generated.html"
ASSETS_DIR = PROJECT_ROOT / "assets"


def update_report_date_to_today() -> None:
    if not META_CSV.exists():
        return
    today = datetime.now().strftime("%d %B %Y")
    with open(META_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    if not rows or "report_date" not in (fieldnames or []):
        return
    for row in rows:
        row["report_date"] = today
    with open(META_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-update-date", action="store_true", help="Do not set report_date to today")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML only, skip PDF")
    args = parser.parse_args()

    if not args.no_update_date:
        update_report_date_to_today()

    from irctc_report import build_context, render_html, convert_to_pdf
    from scripts.generate_report import ensure_logo_in_output

    try:
        context = build_context(DATA_DIR)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    html = render_html(TEMPLATE_PATH, context)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    ensure_logo_in_output(OUTPUT_HTML, ASSETS_DIR)
    print(f"HTML saved: {OUTPUT_HTML}")

    if not args.html_only:
        try:
            pdf_path = convert_to_pdf(OUTPUT_HTML)
            print(f"PDF saved: {pdf_path}")
        except Exception as e:
            print(f"PDF conversion failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
