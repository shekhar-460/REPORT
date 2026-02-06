#!/usr/bin/env python3
"""
Web app: upload CSV files to generate the IRCTC Takedown Report (HTML and optional PDF).

Run from project root: python -m scripts.app_upload
Open: http://127.0.0.1:5000 or http://<your-ip>:5000 (hosted on 0.0.0.0)
"""

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_src = PROJECT_ROOT / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

try:
    from flask import Flask, request, send_file, render_template_string, redirect, url_for
except ImportError:
    print("Install Flask: pip install flask")
    sys.exit(1)

from irctc_report import build_context, render_html, convert_to_pdf
from scripts.generate_report import ensure_logo_in_output

TEMPLATE_PATH = PROJECT_ROOT / "templates" / "IRCTC_Takedown_Report_template.html"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_HTML = OUTPUT_DIR / "IRCTC_Takedown_Report_generated.html"
ASSETS_DIR = PROJECT_ROOT / "assets"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB

UPLOAD_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>IRCTC Report – CSV Upload</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 560px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-size: 1.25rem; }
    .field { margin-bottom: 1rem; }
    label { display: block; font-weight: 600; margin-bottom: 0.25rem; }
    .hint { font-size: 0.875rem; color: #57606a; margin-top: 0.25rem; }
    input[type=file] { width: 100%; }
    button { background: #cf222e; color: #fff; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; font-size: 1rem; }
    button:hover { background: #a91c26; }
    .cb { margin: 1rem 0; }
    .cb label { font-weight: normal; display: inline; }
    .error { background: #ffebe9; color: #cf222e; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; }
    .success { background: #dafbe1; color: #1a7f37; padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; }
    .links { margin-top: 1rem; }
    .links a { margin-right: 1rem; color: #0969da; }
  </style>
</head>
<body>
  <h1>IRCTC Takedown Report – Generate from CSV</h1>
  {% if error %}
  <div class="error">{{ error }}</div>
  {% endif %}
  {% if success %}
  <div class="success">{{ success }}</div>
  <div class="links">
    <a href="{{ url_for('download_html') }}">Download HTML</a>
    {% if pdf_ready %}
    <a href="{{ url_for('download_pdf') }}">Download PDF</a>
    {% endif %}
  </div>
  {% else %}
  <form method="post" enctype="multipart/form-data" action="{{ url_for('upload') }}">
    <div class="field">
      <label for="report_meta">report_meta.csv (required)</label>
      <input type="file" name="report_meta" id="report_meta" accept=".csv" required>
      <div class="hint">report_date, prepared_by, reporting_window, newly_completed_domain, newly_under_review_domain, reactivated_domains, threat_severity, dominant_threat_type, risk_exposure, closing_note</div>
    </div>
    <div class="field">
      <label for="taken_down">taken_down.csv</label>
      <input type="file" name="taken_down" id="taken_down" accept=".csv">
      <div class="hint">domain_url, reported_on, last_updated, threat_category, remarks</div>
    </div>
    <div class="field">
      <label for="under_review">under_review.csv</label>
      <input type="file" name="under_review" id="under_review" accept=".csv">
      <div class="hint">domain_url, reported_on, threat_category, remarks</div>
    </div>
    <div class="field">
      <label for="in_progress">in_progress.csv</label>
      <input type="file" name="in_progress" id="in_progress" accept=".csv">
      <div class="hint">domain_url, reported_on, threat_category, remarks</div>
    </div>
    <div class="cb">
      <input type="checkbox" name="also_pdf" id="also_pdf" value="1">
      <label for="also_pdf">Also generate PDF (requires Playwright)</label>
    </div>
    <button type="submit">Generate Report</button>
  </form>
  {% endif %}
  <p class="hint" style="margin-top: 2rem;">Threat category values: Phishing Website, Typosquatted Domain, Fake Mobile App. reactivated_domains in meta: semicolon-separated list.</p>
</body>
</html>
"""

_generated_html_path = None
_generated_pdf_path = None


def _save_upload(f, folder: Path, name: str) -> Path:
    path = folder / name
    f.save(str(path))
    return path


@app.route("/")
def index():
    return render_template_string(
        UPLOAD_PAGE,
        error=request.args.get("error"),
        success=request.args.get("success"),
        pdf_ready=_generated_pdf_path is not None and _generated_pdf_path.exists(),
    )


@app.route("/upload", methods=["POST"])
def upload():
    global _generated_html_path, _generated_pdf_path
    _generated_html_path = None
    _generated_pdf_path = None
    report_meta = request.files.get("report_meta")
    if not report_meta or not report_meta.filename:
        return redirect(url_for("index", error="report_meta.csv is required"))
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp)
        _save_upload(report_meta, data_dir, "report_meta.csv")
        for key, name in [
            ("taken_down", "taken_down.csv"),
            ("under_review", "under_review.csv"),
            ("in_progress", "in_progress.csv"),
        ]:
            f = request.files.get(key)
            if f and f.filename:
                _save_upload(f, data_dir, name)
        try:
            context = build_context(data_dir)
        except (FileNotFoundError, ValueError) as e:
            return redirect(url_for("index", error=str(e)))
        if not TEMPLATE_PATH.exists():
            return redirect(url_for("index", error=f"Template not found: {TEMPLATE_PATH}"))
        html = render_html(TEMPLATE_PATH, context)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_HTML.write_text(html, encoding="utf-8")
        ensure_logo_in_output(OUTPUT_HTML, ASSETS_DIR)
        _generated_html_path = OUTPUT_HTML
        if request.form.get("also_pdf"):
            try:
                _generated_pdf_path = convert_to_pdf(OUTPUT_HTML)
            except Exception as e:
                return redirect(url_for("index", success=f"HTML generated. PDF failed: {e}"))
        return redirect(url_for("index", success="Report generated. Download HTML or PDF below."))


@app.route("/download/html")
def download_html():
    if _generated_html_path and _generated_html_path.exists():
        return send_file(
            _generated_html_path,
            as_attachment=True,
            download_name=_generated_html_path.name,
            mimetype="text/html",
        )
    return redirect(url_for("index", error="No report generated yet."))


@app.route("/download/pdf")
def download_pdf():
    if _generated_pdf_path and _generated_pdf_path.exists():
        return send_file(
            _generated_pdf_path,
            as_attachment=True,
            download_name=_generated_pdf_path.name,
            mimetype="application/pdf",
        )
    return redirect(url_for("index", error="No PDF generated. Run again with “Also generate PDF” checked."))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
