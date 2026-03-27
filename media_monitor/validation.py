"""
validation.py
-------------
Field-level and record-level validation.

validate_record()     — checks a single record dict
validate_all()        — runs over a list and returns a ValidationReport
ValidationReport      — structured summary of issues found
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from media_monitor import KEY_MESSAGES, ME_MARKETS
from media_monitor.utils import get_logger, parse_date

log = get_logger(__name__)

# ── Severity constants ────────────────────────────────────────────────────────
ERROR   = "ERROR"    # record should not be used
WARNING = "WARNING"  # record usable but attention needed
INFO    = "INFO"     # informational observation

# ── Individual field validators ───────────────────────────────────────────────

def _validate_url(url: str) -> list[str]:
    issues = []
    if not url:
        issues.append("link is empty")
    elif not re.match(r"https?://", url):
        issues.append(f"link does not start with http(s)://: {url[:80]}")
    return issues


def _validate_date(date_str: str) -> list[str]:
    issues = []
    if not date_str:
        issues.append("publication_date is empty")
        return issues
    dt = parse_date(date_str)
    if dt is None:
        issues.append(f"publication_date unrecognised format: '{date_str}'")
    else:
        now = datetime.now()
        if dt.year < 2020:
            issues.append(f"publication_date suspiciously old: {date_str}")
        if dt > now:
            issues.append(f"publication_date is in the future: {date_str}")
    return issues


def _validate_market(market: str) -> list[str]:
    if market not in ME_MARKETS:
        return [f"market '{market}' is not in the ME_MARKETS list"]
    return []


def _validate_tier(tier: str) -> list[str]:
    if tier not in {"Tier 1", "Tier 2", "Tier 3", "Unknown"}:
        return [f"tier value unexpected: '{tier}'"]
    return []


def _validate_pullthrough(pt: Any) -> list[str]:
    issues = []
    try:
        val = float(pt)
        if not (0.0 <= val <= 1.0):
            issues.append(f"message_pullthrough out of range [0,1]: {val}")
    except (TypeError, ValueError):
        issues.append(f"message_pullthrough is not numeric: {pt!r}")
    return issues


def _validate_umv(umv: Any) -> list[str]:
    try:
        if int(umv) < 0:
            return [f"umv is negative: {umv}"]
    except (TypeError, ValueError):
        return [f"umv is not an integer: {umv!r}"]
    return []


# ── Record-level validation ───────────────────────────────────────────────────

@dataclass
class RecordIssue:
    record_id:  str
    source:     str
    severity:   str
    field:      str
    message:    str


def validate_record(record: dict) -> list[RecordIssue]:
    """
    Run all field validators against a single coverage record.
    Returns a (possibly empty) list of RecordIssue objects.
    """
    rid    = record.get("id", "?")
    source = record.get("source", "?")
    issues: list[RecordIssue] = []

    def add(severity: str, fld: str, msg: str) -> None:
        issues.append(RecordIssue(rid, source, severity, fld, msg))

    # Required fields — ERROR if missing / blank
    required_fields = ["source", "link", "publication_date", "market", "tier"]
    for fld in required_fields:
        if not record.get(fld):
            add(ERROR, fld, f"Required field '{fld}' is missing or empty")

    # URL
    for msg in _validate_url(record.get("link", "")):
        add(ERROR, "link", msg)

    # Date
    for msg in _validate_date(record.get("publication_date", "")):
        add(ERROR, "publication_date", msg)

    # Market
    for msg in _validate_market(record.get("market", "")):
        add(WARNING, "market", msg)

    # Tier
    for msg in _validate_tier(record.get("tier", "")):
        add(WARNING, "tier", msg)

    # Pullthrough
    for msg in _validate_pullthrough(record.get("message_pullthrough", 0)):
        add(WARNING, "message_pullthrough", msg)

    # UMV
    for msg in _validate_umv(record.get("umv", 0)):
        add(WARNING, "umv", msg)

    # Headline completeness
    if not record.get("headline") or record["headline"] == "No headline provided":
        add(INFO, "headline", "Headline is missing — recommend manual update")

    # Low message pull-through flag
    pt = record.get("message_pullthrough", 0)
    try:
        if float(pt) == 0.0:
            add(INFO, "message_pullthrough",
                "No key messages detected — verify article content manually")
    except (TypeError, ValueError):
        pass

    return issues


# ── Batch validation ──────────────────────────────────────────────────────────

@dataclass
class ValidationReport:
    total_records:  int                     = 0
    error_count:    int                     = 0
    warning_count:  int                     = 0
    info_count:     int                     = 0
    issues:         list[RecordIssue]       = field(default_factory=list)
    field_coverage: dict[str, float]        = field(default_factory=dict)

    @property
    def pass_rate(self) -> float:
        """Fraction of records with zero errors."""
        if self.total_records == 0:
            return 0.0
        err_records = len({i.record_id for i in self.issues if i.severity == ERROR})
        return (self.total_records - err_records) / self.total_records

    def summary_lines(self) -> list[str]:
        return [
            f"  Total records   : {self.total_records}",
            f"  Pass rate       : {self.pass_rate * 100:.1f}%",
            f"  Errors          : {self.error_count}",
            f"  Warnings        : {self.warning_count}",
            f"  Info notices    : {self.info_count}",
        ]


def validate_all(records: list[dict]) -> ValidationReport:
    """
    Validate every record in *records* and return a ValidationReport.
    """
    report = ValidationReport(total_records=len(records))
    all_issues: list[RecordIssue] = []

    for rec in records:
        rec_issues = validate_record(rec)
        all_issues.extend(rec_issues)

    report.issues        = all_issues
    report.error_count   = sum(1 for i in all_issues if i.severity == ERROR)
    report.warning_count = sum(1 for i in all_issues if i.severity == WARNING)
    report.info_count    = sum(1 for i in all_issues if i.severity == INFO)

    # Field coverage: percentage of records where each key field is populated
    key_fields = ["source", "link", "publication_date", "market", "tier",
                  "headline", "umv", "impressions"]
    for fld in key_fields:
        populated = sum(1 for r in records if r.get(fld) not in (None, "", 0))
        report.field_coverage[fld] = (populated / len(records)) if records else 0.0

    return report
