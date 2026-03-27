# Media Coverage Monitor — Denodo × Snowflake

Automated media-coverage monitoring and reporting system for the **Denodo and Snowflake Data & AI Interoperability** announcement (March 2026), with focus on the **Middle East region**.

## Overview

This Python application:

- **Collects** coverage data from two sources:
  - Mocked Google Search (replaceable with real SerpAPI/Google Custom Search)
  - Manual CSV imports from analyst scans
- **Validates** data quality and completeness
- **Tracks** key metrics:
  - Publication source and tier (Tier 1/2/3)
  - Market / region
  - Unique Monthly Visitors (UMV) and estimated impressions
  - Key-message pull-through ratio
  - Article headlines and links
- **Generates** three types of reports:
  - **24-hour** rapid-update snapshots
  - **Weekly** summaries with market/tier breakdowns
  - **Monthly** comprehensive campaign reports

Reports are exported to Excel, with optional HTML/PNG charts.

## Project Structure

```
media-monitor/
├── media_monitor/
│   ├── __init__.py              # Package config, key messages, markets
│   ├── data_collection.py       # Google search & CSV collection
│   ├── validation.py            # Field & record validators
│   ├── reporting.py             # Report generators (24h, weekly, monthly)
│   ├── utils.py                 # Logging, date parsing, outlet lookup, formatting
│   └── cli.py                   # Command-line interface
├── tests/
│   ├── __init__.py
│   └── test_utils.py            # Unit tests
├── requirements.txt             # Python dependencies
├── sample_manual_scan.csv       # Example CSV for manual input
└── README.md                    # This file
```

**Auto-generated directories** (created at runtime):

- `data/coverage_data.json` — persistent database
- `reports/*.xlsx` — exported reports
- `reports/*.png` — optional charts

## Installation

### Prerequisites

- Python 3.9+
- `pip`

### Steps

```bash
cd media-monitor
pip install -r requirements.txt
```

## Quick Start

### 1. Collect Coverage Data

#### Using Google Search (Mocked)

```bash
python -m media_monitor collect --google
```

This runs a mocked Google search to simulate finding 10+ articles. Replace `_mock_serp_results()` in `media_monitor/data_collection.py` with real API calls (e.g., SerpAPI) when credentials are available.

#### Using Manual CSV Scan

```bash
python -m media_monitor collect --csv sample_manual_scan.csv
```

Expects a CSV with columns: `link`, `headline`, `snippet`, `date`, `type`, `market`, `notes`.

### 2. Validate Data

```bash
python -m media_monitor validate
```

Checks for required fields, date validity, market scope, and key-message detection.

### 3. Generate Reports

```bash
python -m media_monitor report 24h      # Last 24 hours
python -m media_monitor report weekly   # Last 7 days
python -m media_monitor report monthly  # Last 30 days
```

Reports print to console and export to `reports/*.xlsx`.

## Key Features

### Data Collection

- **Canonical Schema**: Every record (regardless of source) conforms to a unified structure:
  - ID, source, domain, link, headline, publication_date, market, tier, language
  - messages_covered, message_pullthrough, umv, impressions
  - article_type, collection_method, collected_at, notes

- **Key-Message Detection**: Scans headlines and snippets for 10 tracked messages:
  - Data interoperability, AI interoperability, open standards
  - Data fabric, data virtualization, Snowflake partnership
  - Industry collaboration, ADBC, Apache Iceberg, semantic layer

- **Outlet Metadata**: Reference database of 20+ Middle East outlets with:
  - Tier classification (Tier 1/2/3 based on UMV)
  - Market, language, UMV benchmarks
  - Auto-lookup by domain

- **Deduplication**: Merges new records with existing database, avoiding duplicates on URL.

### Validation

- **Severity Levels**: ERROR (record unusable) / WARNING (review needed) / INFO (observation)
- **Field Coverage**: Per-field population percentage
- **Pass Rate**: Fraction of records with zero errors
- **Issue Reporting**: Structured list of field-level problems

### Reporting

#### 24-Hour Update

- KPI boxes: Articles, Tier-1 hits, Total UMV, Impressions, Avg pull-through
- Table of articles sorted by tier → date

#### Weekly Summary

- Tier breakdown table
- Market distribution (pie chart optional)
- Top 5 articles by UMV
- Key-message pull-through coverage rates

#### Monthly Campaign Report

- Executive KPIs: total articles, unique sources, total reach, impressions, pull-through ratio, Tier-1 share
- Full coverage log (all articles sorted by tier/date)
- Source performance rankings
- Daily volume trend
- Key-message pull-through analysis

## Configuration

### Key Messages (media_monitor/__init__.py)

Edit `KEY_MESSAGES` to track different themes:

```python
KEY_MESSAGES = [
    "data interoperability",
    "AI interoperability",
    # ... add or remove as needed
]
```

### Markets in Scope (media_monitor/__init__.py)

Edit `ME_MARKETS` to include/exclude regions:

```python
ME_MARKETS = [
    "UAE",
    "Saudi Arabia",
    # ... etc.
]
```

### Outlet Reference Data (media_monitor/utils.py)

Edit `OUTLET_REFERENCE` to add new publications or update UMV benchmarks:

```python
OUTLET_REFERENCE = {
    "newoutlet.com": {
        "name": "New Outlet",
        "tier": "Tier 2",
        "market": "UAE",
        "umv": 250_000,
        "language": "English",
    },
    # ...
}
```

## API Integration

To replace the mocked Google Search with a real API:

### Option 1: SerpAPI (Recommended)

Install: `pip install google-search-results`

In `media_monitor/data_collection.py`, replace `_mock_serp_results()`:

```python
from serpapi import GoogleSearch
import os

def _real_serp_results():
    params = {
        "engine": "google",
        "q": "Denodo Snowflake interoperability Middle East",
        "num": 20,
        "api_key": os.environ["SERPAPI_KEY"],
        "gl": "ae",       # geolocation
        "hl": "en",       # language
        "tbs": "qdr:m",   # past month
    }
    results = GoogleSearch(params).get_dict()
    organic = results.get("organic_results", [])
    return [
        {
            "link": r["link"],
            "title": r["title"],
            "snippet": r.get("snippet", ""),
            "date": r.get("date", ""),
        }
        for r in organic
    ]
```

### Option 2: Google Custom Search API

Set `GOOGLE_CSE_ID` and `GOOGLE_API_KEY` environment variables and use the official `google-api-python-client` library.

## Testing

Run unit tests:

```bash
python -m pytest tests/
# or
python -m unittest discover -s tests/
```

## Examples

### Full Workflow

```bash
# Collect from Google search
python -m media_monitor collect --google

# Validate the database
python -m media_monitor validate

# Generate reports
python -m media_monitor report 24h
python -m media_monitor report weekly
python -m media_monitor report monthly

# View reports in:
# - Console (immediate output)
# - reports/*.xlsx (Excel files with tables)
```

### Incremental Updates

```bash
# Add more data from manual CSV
python -m media_monitor collect --csv additional_articles.csv

# Re-validate (same records + new records)
python -m media_monitor validate

# Generate updated report
python -m media_monitor report weekly
```

## Limitations & Future Enhancements

### Current Limitations

- Google Search is mocked (requires API key replacement for real data)
- Charts (matplotlib) are optional; system falls back gracefully if not installed
- No database (uses JSON file storage)
- No web UI (CLI-based only)

### Future Enhancements

- Real SerpAPI / Google Custom Search integration
- Database backend (PostgreSQL/SQLite)
- REST API server
- Web dashboard with real-time updates
- Multi-language sentiment analysis
- Competitor tracking (Informatica, SAP, etc.)
- Email alerts on high-impact coverage

## Dependencies

| Package | Purpose |
|---------|---------|
| `pandas` | Data manipulation & Excel export |
| `openpyxl` | Excel (.xlsx) writing |
| `tabulate` | Console table formatting |
| `matplotlib` | Optional chart generation |

## License

Internal use only. Contact media@example.com for questions.

## Contact

**Media Intelligence Team**
Email: media@example.com
Press Release: [Denodo × Snowflake Announcement](https://www.denodo.com/en/press-release/2026-03-24/denodo-joins-snowflake-and-industry-leaders-advance-data-and-ai-interoperability-through-open)
