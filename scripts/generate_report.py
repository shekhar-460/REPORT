#!/usr/bin/env python3
"""
Generate IRCTC Takedown Report HTML from CSV data; optionally convert to PDF.

Usage:
  python -m scripts.generate_report [--data-dir data] [--output output/report.html] [--pdf]
"""

import argparse
import shutil
import sys
from pathlib import Path

# Project root and ensure src is on path for irctc_report
PROJECT_ROOT = Path(__file__).resolve().parent.parent
_src = PROJECT_ROOT / "src"
if _src.exists() and str(_src) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_src))


def ensure_logo_in_output(output_path: Path, assets_dir: Path) -> None:
    """Copy main_logo.png to output dir so the generated HTML can load it."""
    logo_src = assets_dir / "main_logo.png"
    if not logo_src.exists():
        return
    out_dir = output_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    logo_dst = out_dir / "main_logo.png"
    if not logo_dst.exists() or logo_src.stat().st_mtime > logo_dst.stat().st_mtime:
        shutil.copy2(logo_src, logo_dst)


def main() -> None:
    default_data = PROJECT_ROOT / "data"
    default_template = PROJECT_ROOT / "templates" / "IRCTC_Takedown_Report_template.html"
    default_output = PROJECT_ROOT / "output" / "IRCTC_Takedown_Report_generated.html"
    assets_dir = PROJECT_ROOT / "assets"

    parser = argparse.ArgumentParser(
        description="Generate IRCTC Takedown Report HTML from CSV data; optionally convert to PDF.",
    )
    parser.add_argument("--data-dir", type=Path, default=default_data, help="Directory with report CSVs")
    parser.add_argument("--template", type=Path, default=default_template, help="Jinja2 template path")
    parser.add_argument("--output", type=Path, default=default_output, help="Output HTML path")
    parser.add_argument("--pdf", action="store_true", help="Also convert to PDF")
    parser.add_argument("--assets-dir", type=Path, default=assets_dir, help="Assets (e.g. logo) directory")
    args = parser.parse_args()

    data_dir = args.data_dir.resolve()
    template_path = args.template.resolve()
    output_path = args.output.resolve()

    if not data_dir.is_dir():
        print(f"Error: data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)
    if not template_path.exists():
        print(f"Error: template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    from irctc_report import build_context, render_html, convert_to_pdf

    try:
        context = build_context(data_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    html = render_html(template_path, context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    ensure_logo_in_output(output_path, args.assets_dir.resolve())
    print(f"HTML saved: {output_path}")

    if args.pdf:
        try:
            pdf_path = convert_to_pdf(output_path)
            print(f"PDF saved: {pdf_path}")
        except Exception as e:
            print(f"PDF conversion failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
