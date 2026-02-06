#!/usr/bin/env bash
# One-command report generation: data/ → output/ (HTML + PDF)
# Usage: ./run_report.sh [--open]
# From project root. Override: REPORT_DATA_DIR=/path/to/csvs ./run_report.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DATA_DIR="${REPORT_DATA_DIR:-data}"
OUTPUT_DIR="output"
OUTPUT_HTML="$OUTPUT_DIR/IRCTC_Takedown_Report_generated.html"
OPEN_PDF=false
for arg in "$@"; do
  [ "$arg" = "--open" ] && OPEN_PDF=true
done

if [ -d ".venv" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="python3"
fi

# Ensure package is importable
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH:-}"

echo "Using data dir: $DATA_DIR"
$PYTHON -m scripts.generate_report --data-dir "$DATA_DIR" --output "$SCRIPT_DIR/$OUTPUT_HTML" --pdf

echo "Done. HTML: $SCRIPT_DIR/$OUTPUT_HTML"
echo "      PDF: $SCRIPT_DIR/$OUTPUT_DIR/IRCTC_Takedown_Report_generated.pdf"

if [ "$OPEN_PDF" = true ] && [ -f "$SCRIPT_DIR/$OUTPUT_DIR/IRCTC_Takedown_Report_generated.pdf" ]; then
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$SCRIPT_DIR/$OUTPUT_DIR/IRCTC_Takedown_Report_generated.pdf"
  elif command -v open >/dev/null 2>&1; then
    open "$SCRIPT_DIR/$OUTPUT_DIR/IRCTC_Takedown_Report_generated.pdf"
  else
    echo "Open the PDF manually."
  fi
fi
