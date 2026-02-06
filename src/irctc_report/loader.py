"""Load report data from CSV files."""

import csv
from pathlib import Path


def load_meta(data_dir: Path) -> dict:
    path = data_dir / "report_meta.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError("report_meta.csv is empty")
    row = rows[0]
    reactivated = (row.get("reactivated_domains") or "").strip()
    reactivated_list = [x.strip() for x in reactivated.split(";") if x.strip()]
    return {
        "report_date": (row.get("report_date") or "").strip(),
        "prepared_by": (row.get("prepared_by") or "").strip(),
        "reporting_window": (row.get("reporting_window") or "").strip(),
        "newly_completed_domain": (row.get("newly_completed_domain") or "").strip(),
        "newly_under_review_domain": (row.get("newly_under_review_domain") or "").strip(),
        "reactivated_domains": reactivated_list,
        "threat_severity": (row.get("threat_severity") or "Predominantly High / Critical").strip(),
        "dominant_threat_type": (row.get("dominant_threat_type") or "Phishing Websites").strip(),
        "risk_exposure": (row.get("risk_exposure") or "Nil (Closed) / Controlled (Open)").strip(),
        "closing_note": (row.get("closing_note") or "").strip()
        or "All known high-risk assets have been neutralized or are under strict containment and monitoring.",
    }


def load_table(data_dir: Path, filename: str, required_columns: list) -> list[dict]:
    path = data_dir / filename
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        row = {k: (v or "").strip() for k, v in r.items()}
        if any(row.get(c) for c in required_columns):
            out.append(row)
    return out


def build_context(data_dir: Path, key_outcomes: list[str] | None = None) -> dict:
    from .constants import DEFAULT_KEY_OUTCOMES

    meta = load_meta(data_dir)
    taken_down = load_table(
        data_dir,
        "taken_down.csv",
        ["domain_url", "reported_on", "last_updated", "threat_category", "remarks"],
    )
    under_review = load_table(
        data_dir,
        "under_review.csv",
        ["domain_url", "reported_on", "threat_category", "remarks"],
    )
    in_progress = load_table(
        data_dir,
        "in_progress.csv",
        ["domain_url", "reported_on", "threat_category", "remarks"],
    )
    counts = {
        "taken_down": len(taken_down),
        "under_review": len(under_review),
        "in_progress": len(in_progress),
        "total_threats": len(taken_down) + len(under_review) + len(in_progress),
    }
    reactivated_domains_display = (
        ", ".join(meta["reactivated_domains"]) if meta["reactivated_domains"] else "None in this period."
    )
    return {
        "meta": meta,
        "counts": counts,
        "key_outcomes": key_outcomes if key_outcomes is not None else DEFAULT_KEY_OUTCOMES,
        "taken_down_rows": taken_down,
        "under_review_rows": under_review,
        "in_progress_rows": in_progress,
        "reactivated_domains_display": reactivated_domains_display,
    }
