"""
utils.py
--------
Shared helpers: logging, date/time, outlet-tier lookup,
UMV/impressions reference data, and small formatting utilities.
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Logging ──────────────────────────────────────────────────────────────────

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
DATE_FMT   = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a consistently formatted logger for *name*."""
    logger = logging.getLogger(name)
    if not logger.handlers:                     # avoid duplicate handlers
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FMT))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


# ── Date helpers ──────────────────────────────────────────────────────────────

def utcnow() -> datetime:
    """Current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


def parse_date(raw: str) -> Optional[datetime]:
    """
    Try several common date formats and return a datetime or None.
    Supports: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, Month DD YYYY, etc.
    """
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%B %d, %Y",        # March 24, 2026
        "%b %d, %Y",        # Mar 24, 2026
        "%d %B %Y",         # 24 March 2026
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def date_label(dt: datetime) -> str:
    """Human-readable label, e.g. '2026-03-24'."""
    return dt.strftime("%Y-%m-%d")


# ── Outlet reference data ─────────────────────────────────────────────────────
#
# Tier classification (Middle East technology / business media):
#   Tier 1 — Major regional flagship publications  (≥ 500 K UMV)
#   Tier 2 — Established sector / trade titles     (100 K – 499 K UMV)
#   Tier 3 — Niche, blog, or emerging outlets      (<  100 K UMV)
#
# UMV figures are approximate reference benchmarks (SimilarWeb, 2025-Q4).

OUTLET_REFERENCE: dict[str, dict] = {
    # ── Tier 1 ────────────────────────────────────────────────────────────────
    "arabianbusiness.com": {
        "name": "Arabian Business",
        "tier": "Tier 1",
        "market": "UAE",
        "umv": 2_800_000,
        "language": "English",
    },
    "gulfnews.com": {
        "name": "Gulf News",
        "tier": "Tier 1",
        "market": "UAE",
        "umv": 5_500_000,
        "language": "English",
    },
    "khaleejtimes.com": {
        "name": "Khaleej Times",
        "tier": "Tier 1",
        "market": "UAE",
        "umv": 4_200_000,
        "language": "English",
    },
    "thenationalnews.com": {
        "name": "The National",
        "tier": "Tier 1",
        "market": "UAE",
        "umv": 6_100_000,
        "language": "English",
    },
    "arabnews.com": {
        "name": "Arab News",
        "tier": "Tier 1",
        "market": "Saudi Arabia",
        "umv": 7_300_000,
        "language": "English",
    },
    "saudigazette.com.sa": {
        "name": "Saudi Gazette",
        "tier": "Tier 1",
        "market": "Saudi Arabia",
        "umv": 1_900_000,
        "language": "English",
    },
    "zawya.com": {
        "name": "Zawya",
        "tier": "Tier 1",
        "market": "Middle East (Regional)",
        "umv": 3_400_000,
        "language": "English",
    },
    "cnbcarabia.com": {
        "name": "CNBC Arabia",
        "tier": "Tier 1",
        "market": "Middle East (Regional)",
        "umv": 2_100_000,
        "language": "Arabic",
    },
    # ── Tier 2 ────────────────────────────────────────────────────────────────
    "itp.net": {
        "name": "ITP.net",
        "tier": "Tier 2",
        "market": "UAE",
        "umv": 480_000,
        "language": "English",
    },
    "tahawultech.com": {
        "name": "Tahawul Tech",
        "tier": "Tier 2",
        "market": "UAE",
        "umv": 320_000,
        "language": "English",
    },
    "cio-me.com": {
        "name": "CIO Middle East",
        "tier": "Tier 2",
        "market": "UAE",
        "umv": 210_000,
        "language": "English",
    },
    "intelligentsme.com": {
        "name": "Intelligent SME",
        "tier": "Tier 2",
        "market": "UAE",
        "umv": 155_000,
        "language": "English",
    },
    "meafinance.com": {
        "name": "MEA Finance",
        "tier": "Tier 2",
        "market": "UAE",
        "umv": 130_000,
        "language": "English",
    },
    "gitexglobal.com": {
        "name": "GITEX Insights",
        "tier": "Tier 2",
        "market": "Middle East (Regional)",
        "umv": 280_000,
        "language": "English",
    },
    "thepeninsulaqatar.com": {
        "name": "The Peninsula",
        "tier": "Tier 2",
        "market": "Qatar",
        "umv": 190_000,
        "language": "English",
    },
    "ameinfo.com": {
        "name": "AMEinfo",
        "tier": "Tier 2",
        "market": "Middle East (Regional)",
        "umv": 240_000,
        "language": "English",
    },
    # ── Tier 3 ────────────────────────────────────────────────────────────────
    "dataconomy.com": {
        "name": "Dataconomy",
        "tier": "Tier 3",
        "market": "Middle East (Regional)",
        "umv": 85_000,
        "language": "English",
    },
    "menabytes.com": {
        "name": "MENAbytes",
        "tier": "Tier 3",
        "market": "Middle East (Regional)",
        "umv": 75_000,
        "language": "English",
    },
    "techjuice.pk": {
        "name": "TechJuice",
        "tier": "Tier 3",
        "market": "Middle East (Regional)",
        "umv": 60_000,
        "language": "English",
    },
    "ventureburn.com": {
        "name": "Venture Burn",
        "tier": "Tier 3",
        "market": "Middle East (Regional)",
        "umv": 45_000,
        "language": "English",
    },
}


def lookup_outlet(domain: str) -> dict:
    """
    Return the reference dict for *domain*.
    Strips 'www.' prefix, then does a suffix match so that
    'www.gulfnews.com' resolves to 'gulfnews.com'.
    Falls back to sensible defaults for unknown outlets.
    """
    domain = domain.lower().lstrip("www.")
    # Exact match first
    if domain in OUTLET_REFERENCE:
        return OUTLET_REFERENCE[domain]
    # Suffix match (handles sub-domains)
    for key, val in OUTLET_REFERENCE.items():
        if domain.endswith(key) or key.endswith(domain):
            return val
    # Unknown outlet — return neutral defaults
    return {
        "name": domain,
        "tier": "Unknown",
        "market": "Unknown",
        "umv": 0,
        "language": "Unknown",
    }


def extract_domain(url: str) -> str:
    """Extract bare domain from a URL string."""
    import re
    match = re.search(r"(?:https?://)?(?:www\.)?([^/?\\s]+)", url)
    return match.group(1).lower() if match else url.lower()


# ── Impressions estimator ─────────────────────────────────────────────────────

def estimate_impressions(umv: int, article_type: str = "news") -> int:
    """
    Rough impression estimate based on UMV.
    Article pages typically receive 0.5–2 % of monthly traffic per story.
    Multiplier varies by article type.
    """
    multipliers = {
        "news":      0.015,   # 1.5 %
        "feature":   0.025,   # 2.5 %
        "exclusive": 0.040,   # 4.0 %
        "brief":     0.005,   # 0.5 %
    }
    rate = multipliers.get(article_type.lower(), 0.015)
    return int(umv * rate)


# ── Formatting helpers ────────────────────────────────────────────────────────

def truncate(text: str, max_len: int = 60) -> str:
    """Truncate *text* to *max_len* chars, appending '…' if needed."""
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def pct(value: float) -> str:
    """Format a 0-1 float as a percentage string."""
    return f"{value * 100:.0f}%"


def number_fmt(n: int) -> str:
    """Format large integers with comma separators."""
    return f"{n:,}"


# ── Path helpers ──────────────────────────────────────────────────────────────

DATA_DIR    = Path(__file__).resolve().parent.parent / "data"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def ensure_dirs() -> None:
    """Create data/ and reports/ directories if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
