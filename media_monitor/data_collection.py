"""
data_collection.py
------------------
Two collection paths:

1. google_search_collect()   — Mocked Google/SerpAPI results.
                               Replace _mock_serp_results() with a real
                               SerpAPI / Google Custom Search call when
                               credentials are available.

2. manual_scan_collect()     — Load articles from a CSV file produced
                               by a human analyst scanning the web.

Both paths return a list[dict] using the canonical CoverageItem schema.
"""

import csv
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from media_monitor import KEY_MESSAGES, ME_MARKETS, PRESS_RELEASE_URL
from media_monitor.utils import (
    extract_domain,
    get_logger,
    lookup_outlet,
    parse_date,
    utcnow,
    estimate_impressions,
)

log = get_logger(__name__)

# ── Canonical record schema ───────────────────────────────────────────────────
#
# Every coverage item (regardless of collection method) must conform to this
# schema before being stored or validated.

COVERAGE_SCHEMA_KEYS = [
    "id",                   # str  — UUID
    "source",               # str  — publication name
    "domain",               # str  — bare domain
    "link",                 # str  — article URL
    "headline",             # str  — article headline
    "publication_date",     # str  — ISO 8601 date string  (YYYY-MM-DD)
    "market",               # str  — country / region from ME_MARKETS
    "tier",                 # str  — Tier 1 / Tier 2 / Tier 3 / Unknown
    "language",             # str  — English / Arabic / …
    "messages_covered",     # list[str] — matched key messages
    "message_pullthrough",  # float — 0.0–1.0 ratio
    "umv",                  # int  — unique monthly visitors
    "impressions",          # int  — estimated article impressions
    "article_type",         # str  — news / feature / exclusive / brief
    "collection_method",    # str  — google_search / manual / rss
    "collected_at",         # str  — ISO timestamp of collection
    "notes",                # str  — free-text analyst notes
]


# ── Key-message detection ─────────────────────────────────────────────────────

def detect_messages(text: str) -> tuple[list[str], float]:
    """
    Scan *text* (headline + snippet) for KEY_MESSAGES.
    Returns (list_of_matched_messages, pullthrough_ratio).
    """
    text_lower = text.lower()
    matched = [msg for msg in KEY_MESSAGES if msg.lower() in text_lower]
    ratio = len(matched) / len(KEY_MESSAGES) if KEY_MESSAGES else 0.0
    return matched, ratio


# ── Record factory ────────────────────────────────────────────────────────────

def build_record(
    link: str,
    headline: str,
    snippet: str,
    raw_date: str,
    article_type: str = "news",
    collection_method: str = "google_search",
    notes: str = "",
    market_override: Optional[str] = None,
) -> dict:
    """
    Assemble a canonical coverage record from raw fields.
    Outlet metadata is resolved automatically via utils.lookup_outlet().
    """
    domain  = extract_domain(link)
    outlet  = lookup_outlet(domain)

    full_text = f"{headline} {snippet}"
    messages, pullthrough = detect_messages(full_text)

    parsed_dt = parse_date(raw_date)
    iso_date  = parsed_dt.strftime("%Y-%m-%d") if parsed_dt else raw_date

    market = market_override or outlet.get("market", "Unknown")
    # Ensure market is in scope; if not, flag for review
    if market not in ME_MARKETS:
        market = "Middle East (Regional)"  # fallback

    umv         = outlet.get("umv", 0)
    impressions = estimate_impressions(umv, article_type)

    return {
        "id":                  str(uuid.uuid4()),
        "source":              outlet.get("name", domain),
        "domain":              domain,
        "link":                link,
        "headline":            headline,
        "publication_date":    iso_date,
        "market":              market,
        "tier":                outlet.get("tier", "Unknown"),
        "language":            outlet.get("language", "English"),
        "messages_covered":    messages,
        "message_pullthrough": round(pullthrough, 4),
        "umv":                 umv,
        "impressions":         impressions,
        "article_type":        article_type,
        "collection_method":   collection_method,
        "collected_at":        utcnow().isoformat(),
        "notes":               notes,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  1.  GOOGLE SEARCH COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

# Search queries used to find ME coverage of the announcement
SEARCH_QUERIES = [
    "Denodo Snowflake data AI interoperability Middle East",
    "Denodo Snowflake open standards UAE",
    "Denodo interoperability announcement Saudi Arabia",
    "\"data interoperability\" Denodo Snowflake Gulf",
    "Denodo press release 2026 Middle East",
]


def _mock_serp_results() -> list[dict]:
    """
    Return simulated SerpAPI / Google Custom Search results.
    """
    return [
        {
            "link":    "https://www.arabianbusiness.com/technology/denodo-snowflake-data-ai-interoperability-open-standards",
            "title":   "Denodo Joins Snowflake to Advance Data and AI Interoperability Through Open Standards",
            "snippet": "Denodo and Snowflake announce a strategic initiative to drive data interoperability and AI interoperability across the enterprise using open standards including Apache Iceberg and ADBC.",
            "date":    "March 25, 2026",
        },
        {
            "link":    "https://www.tahawultech.com/news/denodo-snowflake-data-ai-open-standards-partnership",
            "title":   "Denodo Partners with Snowflake and Industry Leaders on Data Fabric Interoperability",
            "snippet": "The partnership focuses on advancing data fabric and data virtualization capabilities to enable seamless AI interoperability across hybrid cloud environments in the Middle East.",
            "date":    "March 25, 2026",
        },
        {
            "link":    "https://www.itp.net/enterprise/denodo-snowflake-open-standards-ai-interoperability-middle-east",
            "title":   "Denodo and Snowflake Lead Industry Drive for AI and Data Interoperability",
            "snippet": "Regional technology leaders welcome the Denodo–Snowflake collaboration on open standards for data interoperability, with implications for the UAE's AI strategy.",
            "date":    "March 26, 2026",
        },
        {
            "link":    "https://www.zawya.com/en/press-release/companies-news/denodo-joins-snowflake-to-advance-ai-data-interoperability",
            "title":   "Denodo Joins Snowflake and Industry Leaders to Advance Data and AI Interoperability",
            "snippet": "Press release: Denodo announces collaboration with Snowflake and other industry leaders to promote open standards, semantic layer adoption, and AI interoperability across enterprises.",
            "date":    "March 24, 2026",
        },
        {
            "link":    "https://www.arabnews.com/node/denodo-snowflake-data-interoperability-saudi",
            "title":   "Tech Giants Push for Data Interoperability as AI Adoption Accelerates in Saudi Arabia",
            "snippet": "Denodo and Snowflake's announcement on data fabric and AI interoperability is seen as critical for Saudi Arabia's Vision 2030 data infrastructure goals.",
            "date":    "March 27, 2026",
        },
        {
            "link":    "https://www.cio-me.com/analytics/denodo-snowflake-open-standards-data-virtualization",
            "title":   "CIOs Eye Denodo–Snowflake Open-Standards Push as Data Virtualisation Strategy Matures",
            "snippet": "The announcement highlights data virtualization and data fabric as critical enablers for AI interoperability, offering CIOs a pathway to vendor-neutral data access.",
            "date":    "March 26, 2026",
        },
        {
            "link":    "https://www.intelligentsme.com/2026/03/26/denodo-snowflake-industry-leaders-ai-interoperability/",
            "title":   "Denodo and Snowflake Drive Open Standards for SME Data Interoperability",
            "snippet": "SMEs across the Middle East stand to benefit from the Denodo–Snowflake partnership on open standards, reducing data silos and enabling AI-ready infrastructure.",
            "date":    "March 26, 2026",
        },
        {
            "link":    "https://www.thenationalnews.com/business/technology/2026/03/25/denodo-snowflake-data-ai-interoperability/",
            "title":   "Denodo and Snowflake Unveil Open Standards Initiative for AI Data Interoperability",
            "snippet": "The two companies are working with industry leaders to establish a common framework for data interoperability that could reshape how AI systems access enterprise data.",
            "date":    "March 25, 2026",
        },
        {
            "link":    "https://www.meafinance.com/technology/denodo-snowflake-open-standards-data-fabric/",
            "title":   "Financial Sector to Gain from Denodo–Snowflake Data Fabric Push",
            "snippet": "The Denodo–Snowflake collaboration on data fabric and open standards is expected to accelerate industry collaboration across the MEA financial services sector.",
            "date":    "March 27, 2026",
        },
        {
            "link":    "https://www.menabytes.com/denodo-snowflake-data-interoperability-2026/",
            "title":   "Denodo and Snowflake Target MENA Data Interoperability Gap",
            "snippet": "The joint initiative to advance AI interoperability and open standards addresses a critical gap in the MENA region's data infrastructure.",
            "date":    "March 28, 2026",
        },
    ]


def google_search_collect() -> list[dict]:
    """
    Run (mocked) Google searches and return a list of canonical coverage records.
    """
    log.info("Starting Google Search collection (mock mode)…")
    raw_results = _mock_serp_results()
    records: list[dict] = []

    for r in raw_results:
        rec = build_record(
            link=r["link"],
            headline=r["title"],
            snippet=r["snippet"],
            raw_date=r["date"],
            article_type="news",
            collection_method="google_search",
        )
        records.append(rec)
        log.debug("Collected: %s", rec["source"])

    log.info("Google Search collection complete — %d records", len(records))
    return records


# ─────────────────────────────────────────────────────────────────────────────
#  2.  MANUAL SCAN COLLECTION
# ─────────────────────────────────────────────────────────────────────────────

# Expected CSV column names (case-insensitive).  Unmapped columns are ignored.
CSV_COLUMN_MAP = {
    "link":         ["link", "url", "article_url", "article url"],
    "headline":     ["headline", "title", "article title", "article_title"],
    "snippet":      ["snippet", "excerpt", "summary", "body", "description"],
    "raw_date":     ["date", "publication date", "pub_date", "publication_date"],
    "article_type": ["type", "article_type", "article type"],
    "market":       ["market", "country", "region"],
    "notes":        ["notes", "analyst notes", "comments"],
}


def _resolve_csv_headers(headers: list[str]) -> dict[str, str]:
    """
    Build a mapping {canonical_key: actual_csv_column} from *headers*.
    """
    lowered = {h.lower().strip(): h for h in headers}
    resolved: dict[str, str] = {}
    for canonical, aliases in CSV_COLUMN_MAP.items():
        for alias in aliases:
            if alias in lowered:
                resolved[canonical] = lowered[alias]
                break
    return resolved


def manual_scan_collect(csv_path: str) -> list[dict]:
    """
    Load articles from a manually prepared CSV file and return canonical records.

    Required CSV column (at minimum): link / url
    Recommended columns: headline, date, market
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    records: list[dict] = []
    log.info("Loading manual scan from %s…", path)

    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        col_map = _resolve_csv_headers(reader.fieldnames or [])

        if "link" not in col_map:
            raise ValueError("CSV must contain a 'link' or 'url' column.")

        for row_num, row in enumerate(reader, start=2):   # row 1 = header
            link = row.get(col_map["link"], "").strip()
            if not link:
                log.warning("Row %d: empty link — skipping", row_num)
                continue

            headline = row.get(col_map.get("headline", ""), "No headline provided").strip()
            snippet  = row.get(col_map.get("snippet",  ""), "").strip()
            raw_date = row.get(col_map.get("raw_date", ""), utcnow().strftime("%Y-%m-%d")).strip()
            art_type = row.get(col_map.get("article_type", ""), "news").strip() or "news"
            market   = row.get(col_map.get("market", ""), "").strip() or None
            notes    = row.get(col_map.get("notes", ""),  "").strip()

            rec = build_record(
                link=link,
                headline=headline,
                snippet=snippet,
                raw_date=raw_date,
                article_type=art_type,
                collection_method="manual",
                notes=notes,
                market_override=market if market in ME_MARKETS else None,
            )
            records.append(rec)
            log.debug("Manual row %d → %s", row_num, rec["source"])

    log.info("Manual scan complete — %d records loaded", len(records))
    return records


# ─────────────────────────────────────────────────────────────────────────────
#  3.  PERSISTENCE
# ─────────────────────────────────────────────────────────────────────────────

from media_monitor.utils import DATA_DIR, ensure_dirs   # noqa: E402

COVERAGE_DB = DATA_DIR / "coverage_data.json"


def load_db() -> list[dict]:
    """Load the persisted coverage database.  Returns [] if empty/absent."""
    ensure_dirs()
    if not COVERAGE_DB.exists():
        return []
    with open(COVERAGE_DB, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            log.error("coverage_data.json is corrupt — returning empty list")
            return []


def save_db(records: list[dict]) -> None:
    """Persist *records* to the JSON database (overwrites existing file)."""
    ensure_dirs()
    with open(COVERAGE_DB, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2, ensure_ascii=False)
    log.info("Database saved — %d total records", len(records))


def merge_records(existing: list[dict], new: list[dict]) -> tuple[list[dict], int]:
    """
    Merge *new* into *existing*, deduplicating on the article URL.
    Returns (merged_list, count_added).
    """
    seen_links = {r["link"] for r in existing}
    added = 0
    for rec in new:
        if rec["link"] not in seen_links:
            existing.append(rec)
            seen_links.add(rec["link"])
            added += 1
        else:
            log.debug("Duplicate skipped: %s", rec["link"])
    return existing, added
