"""Render the report HTML from a Jinja2 template and context."""

import sys
from pathlib import Path


def render_html(template_path: Path, context: dict) -> str:
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
    except ImportError:
        print("Install Jinja2: pip install jinja2", file=sys.stderr)
        sys.exit(1)
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_path.name)
    return template.render(**context)
