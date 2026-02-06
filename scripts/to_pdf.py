#!/usr/bin/env python3
"""Convert any HTML file to PDF (Playwright). Usage: python -m scripts.to_pdf [path/to/file.html]"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_src = PROJECT_ROOT / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from irctc_report import convert_to_pdf


def main():
    if len(sys.argv) < 2:
        default = PROJECT_ROOT / "output" / "IRCTC_Takedown_Report_generated.html"
        html_path = default if default.exists() else None
        if not html_path:
            print("Usage: python -m scripts.to_pdf <path/to/file.html>", file=sys.stderr)
            sys.exit(1)
    else:
        html_path = Path(sys.argv[1]).resolve()
    try:
        pdf_path = convert_to_pdf(html_path)
        print(f"PDF saved: {pdf_path}")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
