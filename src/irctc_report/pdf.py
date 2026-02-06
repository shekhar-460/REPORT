"""Convert HTML report to PDF using Playwright."""

import pathlib

PRINT_CSS = """
@media print {
    html {
        font-size: 11px !important;
    }
    body {
        width: 100% !important;
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .ml-64, [class*="ml-64"] {
        margin-left: 0 !important;
        max-width: none !important;
        width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .p-8 {
        padding: 1rem !important;
    }
    .text-4xl { font-size: 1.5rem !important; }
    .text-3xl { font-size: 1.25rem !important; }
    .text-2xl { font-size: 1.15rem !important; }
    .text-xl { font-size: 1.05rem !important; }
    .text-lg { font-size: 1rem !important; }
    .prose p, .text-gray-700, .text-gray-600 { font-size: 0.95rem !important; }
    pre, code, .diagram { font-size: 0.7rem !important; }
    .mb-16 { margin-bottom: 1.5rem !important; }
    .mb-12 { margin-bottom: 1rem !important; }
    .mb-6 { margin-bottom: 0.5rem !important; }
    .mb-4 { margin-bottom: 0.35rem !important; }
    .space-y-2 > * + * { margin-top: 0.25rem !important; }
    h2, h3, h4 {
        page-break-after: avoid !important;
    }
    ul, ol {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    .bg-green-50, div[class*="border-l-4"] {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
    li {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }
}
"""


def convert_to_pdf(html_path: pathlib.Path) -> pathlib.Path:
    """Convert an HTML file to PDF. Returns the path to the created PDF."""
    html_path = pathlib.Path(html_path).resolve()
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    if html_path.suffix.lower() not in (".html", ".htm"):
        raise ValueError(f"Expected .html or .htm file, got {html_path.suffix!r}")
    pdf_path = html_path.with_suffix(".pdf")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "Playwright not installed. Run: pip install playwright && playwright install chromium"
        ) from None
    file_url = html_path.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(file_url, wait_until="networkidle")
        page.add_style_tag(content=PRINT_CSS)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "18px", "bottom": "18px", "left": "18px", "right": "18px"},
        )
        browser.close()
    return pdf_path
