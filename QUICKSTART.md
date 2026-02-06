# IRCTC Report – Quick start

Get from zero to a generated report in a few minutes.

---

## 1. Setup (once)

```bash
cd /path/to/REPORT

# Create and use a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For PDF generation, install Playwright’s Chromium
playwright install chromium
```

---

## 2. Generate report

**Option A – Shell script (easiest)**

```bash
./run_report.sh
```

Reads from `data/` and writes HTML + PDF to `output/`.

**Option B – Make**

```bash
make report-pdf
```

**Option C – Python**

```bash
export PYTHONPATH=src
python -m scripts.generate_report --data-dir data --output output/IRCTC_Takedown_Report_generated.html --pdf
```

---

## 3. Where to find the report

- **HTML**: `output/IRCTC_Takedown_Report_generated.html`  
  Open in a browser (logo loads from `output/main_logo.png`).
- **PDF**: `output/IRCTC_Takedown_Report_generated.pdf`

---

## 4. Use your own data

Put your CSVs in `data/`:

- `report_meta.csv` – **required** (one row: report date, prepared by, metrics text, closing note, etc.)
- `taken_down.csv` – domain_url, reported_on, last_updated, threat_category, remarks
- `under_review.csv` – domain_url, reported_on, threat_category, remarks  
- `in_progress.csv` – same as under_review

Then run step 2 again. See **README.md** for the full CSV schema.

---

## 5. Optional: Web upload

```bash
export PYTHONPATH=src
python -m scripts.app_upload
```

The app hosts on **0.0.0.0:5000** (reachable from your LAN). Open **http://127.0.0.1:5000** on this machine, or **http://\<this-machine-ip\>:5000** from another device. Upload the four CSVs, generate, and download HTML or PDF.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| `ModuleNotFoundError: irctc_report` | Run from project root and set `PYTHONPATH=src` or use `./run_report.sh` / `make`. |
| PDF step fails | Run `playwright install chromium` (and ensure `playwright` is installed). |
| Logo missing in HTML | Ensure `assets/main_logo.png` exists; the script copies it to `output/`. |
| `report_meta.csv is empty` | Add at least one row with the required columns (see README.md). |

For full details, CSV column descriptions, and automation (cron), see **README.md**.
