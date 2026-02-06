"""
IRCTC Takedown Report – load CSV data, render HTML, convert to PDF.
"""

from .constants import DEFAULT_KEY_OUTCOMES
from .loader import build_context, load_meta, load_table
from .pdf import convert_to_pdf
from .render import render_html

__all__ = [
    "DEFAULT_KEY_OUTCOMES",
    "build_context",
    "load_meta",
    "load_table",
    "render_html",
    "convert_to_pdf",
]
