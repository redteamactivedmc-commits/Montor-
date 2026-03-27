"""
media_monitor
=============
Automated media-coverage monitoring for the Denodo × Snowflake
"Data & AI Interoperability" announcement (March 2026).

Scope: Middle East region.
"""

__version__ = "1.0.0"
__author__  = "Media Intelligence Team"
__email__   = "media@example.com"

# Canonical press-release URL tracked by every module
PRESS_RELEASE_URL = (
    "https://www.denodo.com/en/press-release/2026-03-24/"
    "denodo-joins-snowflake-and-industry-leaders-advance-data-and-ai-"
    "interoperability-through-open"
)

# Key messages the PR team wants to see pulled through in coverage
KEY_MESSAGES = [
    "data interoperability",
    "AI interoperability",
    "open standards",
    "data fabric",
    "data virtualization",
    "Snowflake partnership",
    "industry collaboration",
    "ADBC",                     # Arrow Database Connectivity
    "Apache Iceberg",
    "semantic layer",
]

# Middle-East markets in scope
ME_MARKETS = [
    "UAE",
    "Saudi Arabia",
    "Qatar",
    "Kuwait",
    "Bahrain",
    "Oman",
    "Egypt",
    "Jordan",
    "Lebanon",
    "Iraq",
    "Middle East (Regional)",
]
