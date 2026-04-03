#!/usr/bin/env python3
"""
example_ai_snapshot_agent.py
-----------------------------
Complete example demonstrating how to use the AI snapshot reporting agent
with the Anthropic API for intelligent headline extraction and analysis.

Usage:
    python example_ai_snapshot_agent.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from media_monitor.snapshot_reporting import (
    create_snapshot,
    create_24h_coverage,
    create_or_update_tracker,
)
from media_monitor.utils import get_logger

log = get_logger(__name__)

# ────────────────────────────────────────────────────────────────────────────
#  EXAMPLE 1: CREATE A SINGLE SNAPSHOT
# ────────────────────────────────────────────────────────────────────────────

def example_single_snapshot():
    """Example: Create a snapshot of a publication."""

    print("\n" + "="*80)
    print("EXAMPLE 1: CREATE SINGLE SNAPSHOT")
    print("="*80)

    result = create_snapshot(
        client_name="Denodo",
        magazine_name="TechNews Middle East",
        publishing_date="2026-04-03",
        url="https://www.technewsme.com",
        headline="Denodo Advances Data Integration Platform",
        client_logo_path="logos/denodo_logo.png",  # Path to your client logo
        active_logo_path="logos/active_logo.png",  # Path to your Active logo
    )

    if result:
        print(f"\n✓ Snapshot created: {result}")
    else:
        print("\n✗ Failed to create snapshot")


# ────────────────────────────────────────────────────────────────────────────
#  EXAMPLE 2: CREATE MULTIPLE SNAPSHOTS
# ────────────────────────────────────────────────────────────────────────────

def example_multiple_snapshots():
    """Example: Create snapshots for multiple publications."""

    print("\n" + "="*80)
    print("EXAMPLE 2: CREATE MULTIPLE SNAPSHOTS")
    print("="*80)

    publications = [
        {
            "url": "https://technewsme.com/article1",
            "magazine": "TechNews Middle East",
            "headline": "Denodo Launches New Enterprise Solution",
            "date": "2026-04-01",
        },
        {
            "url": "https://itpronewsmideast.com/article2",
            "magazine": "IT Pro News Middle East",
            "headline": "Data Integration Market Reaches New Heights",
            "date": "2026-04-02",
        },
        {
            "url": "https://cloudcomputingme.com/article3",
            "magazine": "Cloud Computing ME",
            "headline": "Top 5 Cloud Data Integration Platforms 2026",
            "date": "2026-04-03",
        },
    ]

    for pub in publications:
        print(f"\nCreating snapshot: {pub['magazine']}...")

        result = create_snapshot(
            client_name="Denodo",
            magazine_name=pub["magazine"],
            publishing_date=pub["date"],
            url=pub["url"],
            headline=pub["headline"],
            client_logo_path="logos/denodo_logo.png",
            active_logo_path="logos/active_logo.png",
        )

        if result:
            print(f"  ✓ Created: {result.name}")
        else:
            print(f"  ✗ Failed to create snapshot")


# ────────────────────────────────────────────────────────────────────────────
#  EXAMPLE 3: CREATE 24-HOUR COVERAGE REPORT
# ────────────────────────────────────────────────────────────────────────────

def example_24h_coverage_report():
    """Example: Create a 24-hour coverage report."""

    print("\n" + "="*80)
    print("EXAMPLE 3: CREATE 24-HOUR COVERAGE REPORT")
    print("="*80)

    # Sample coverage data (in real usage, this would come from your database)
    coverage_data = [
        {
            "source": "TechNews Middle East",
            "headline": "Denodo Launches Enterprise Platform",
            "publication_date": "2026-04-03",
            "url": "https://technewsme.com/article",
            "media_type": "Online",
            "tier": "Tier 1",
            "umv": 15000,
            "impressions": 250000,
            "message_pullthrough": 0.85,
            "client": "Denodo",
        },
        {
            "source": "IT Pro News",
            "headline": "Data Integration Solutions Evolve",
            "publication_date": "2026-04-03",
            "url": "https://itpronews.com/article",
            "media_type": "Online",
            "tier": "Tier 2",
            "umv": 8000,
            "impressions": 120000,
            "message_pullthrough": 0.72,
            "client": "Denodo",
        },
        {
            "source": "Cloud Computing Journal",
            "headline": "Top Platforms for Modern Data Environments",
            "publication_date": "2026-04-03",
            "url": "https://cloudjournal.com/article",
            "media_type": "Online",
            "tier": "Tier 1",
            "umv": 12000,
            "impressions": 300000,
            "message_pullthrough": 0.88,
            "client": "Denodo",
        },
    ]

    result = create_24h_coverage(
        client_name="Denodo",
        press_release_name="Q1 Platform Launch Initiative",
        coverage_data=coverage_data,
        client_logo_path="logos/denodo_logo.png",
        active_logo_path="logos/active_logo.png",
    )

    if result:
        print(f"\n✓ Coverage report created: {result}")
        print(f"  Articles covered: {len(coverage_data)}")
        total_umv = sum(r.get("umv", 0) for r in coverage_data)
        print(f"  Total UMV: ${total_umv:,}")
    else:
        print("\n✗ Failed to create coverage report")


# ────────────────────────────────────────────────────────────────────────────
#  EXAMPLE 4: UPDATE EXCEL TRACKER
# ────────────────────────────────────────────────────────────────────────────

def example_update_tracker():
    """Example: Update the Excel tracker with coverage records."""

    print("\n" + "="*80)
    print("EXAMPLE 4: UPDATE EXCEL TRACKER")
    print("="*80)

    # Sample records to add to tracker
    records = [
        {
            "client": "Denodo",
            "source": "TechNews Middle East",
            "publication": "TechNews ME",
            "headline": "Denodo Launches Enterprise Platform",
            "url": "https://technewsme.com/article",
            "media_type": "Online",
            "tier": "Tier 1",
            "umv": 15000,
            "impressions": 250000,
            "message_pullthrough": 0.85,
        },
        {
            "client": "Denodo",
            "source": "IT Pro News",
            "publication": "IT Pro News",
            "headline": "Data Integration Solutions Evolve",
            "url": "https://itpronews.com/article",
            "media_type": "Online",
            "tier": "Tier 2",
            "umv": 8000,
            "impressions": 120000,
            "message_pullthrough": 0.72,
        },
    ]

    result = create_or_update_tracker(
        records=records,
        client_name="Denodo",
    )

    if result:
        print(f"\n✓ Tracker updated: {result}")
        print(f"  Records added: {len(records)}")
    else:
        print("\n✗ Failed to update tracker")


# ────────────────────────────────────────────────────────────────────────────
#  EXAMPLE 5: AI-POWERED HEADLINE EXTRACTION (with Anthropic API)
# ────────────────────────────────────────────────────────────────────────────

def example_ai_headline_extraction():
    """Example: Use Claude API to extract headline from screenshot."""

    print("\n" + "="*80)
    print("EXAMPLE 5: AI-POWERED HEADLINE EXTRACTION")
    print("="*80)

    try:
        from anthropic import Anthropic
        import base64
    except ImportError:
        print("\n⚠ Anthropic SDK not installed. Skipping AI example.")
        print("  Install with: pip install anthropic")
        return

    # Initialize Anthropic client
    client = Anthropic()

    # Example: Load and process a screenshot
    screenshot_path = "reports/snapshots/temp_screenshot_20260403.png"

    if not Path(screenshot_path).exists():
        print(f"\n⚠ Screenshot not found at {screenshot_path}")
        print("  Create a snapshot first to test this feature.")
        return

    try:
        # Read and encode screenshot
        with open(screenshot_path, "rb") as f:
            screenshot_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Send to Claude for analysis
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Analyze this article screenshot and provide:
1. Main headline
2. Publication name
3. Key topics covered (comma-separated)
4. Sentiment (positive/neutral/negative)

Format as JSON."""
                        }
                    ],
                }
            ],
        )

        print(f"\n✓ AI Analysis Complete:")
        print(f"\nResponse:\n{response.content[0].text}")

    except Exception as e:
        print(f"\n✗ Failed to analyze screenshot: {e}")


# ────────────────────────────────────────────────────────────────────────────
#  EXAMPLE 6: COMPLETE WORKFLOW
# ────────────────────────────────────────────────────────────────────────────

def example_complete_workflow():
    """Example: Complete workflow from snapshot to tracker."""

    print("\n" + "="*80)
    print("EXAMPLE 6: COMPLETE WORKFLOW")
    print("="*80)

    print("\nStep 1: Creating snapshots...")

    urls = [
        "https://technewsme.com",
        "https://itpronewsmideast.com",
    ]

    snapshots = []
    for i, url in enumerate(urls, 1):
        result = create_snapshot(
            client_name="Denodo",
            magazine_name=f"Publication {i}",
            publishing_date="2026-04-03",
            url=url,
            headline=f"Denodo Article {i}",
            client_logo_path="logos/denodo_logo.png",
            active_logo_path="logos/active_logo.png",
        )
        if result:
            snapshots.append(result)
            print(f"  ✓ Snapshot {i} created")

    print(f"\nStep 2: Creating 24-hour coverage report...")

    coverage_data = [
        {
            "source": f"Publication {i}",
            "headline": f"Denodo Article {i}",
            "publication_date": "2026-04-03",
            "url": url,
            "media_type": "Online",
            "tier": "Tier 1" if i == 1 else "Tier 2",
            "umv": 15000 * i,
            "impressions": 250000 * i,
            "message_pullthrough": 0.85,
        }
        for i, url in enumerate(urls, 1)
    ]

    coverage_result = create_24h_coverage(
        client_name="Denodo",
        press_release_name="Multi-Channel Campaign",
        coverage_data=coverage_data,
        client_logo_path="logos/denodo_logo.png",
        active_logo_path="logos/active_logo.png",
    )

    if coverage_result:
        print(f"  ✓ Coverage report created")

    print(f"\nStep 3: Updating tracker...")

    tracker_result = create_or_update_tracker(
        records=coverage_data,
        client_name="Denodo",
    )

    if tracker_result:
        print(f"  ✓ Tracker updated")

    print(f"\n✓ Complete workflow finished!")
    print(f"  Snapshots: {len(snapshots)}")
    print(f"  Coverage report: {coverage_result.name if coverage_result else 'Failed'}")
    print(f"  Tracker: {tracker_result.name if tracker_result else 'Failed'}")


# ────────────────────────────────────────────────────────────────────────────
#  MAIN
# ────────────────────────────────────────────────────────────────────────────

def main():
    """Run all examples."""

    print("\n" + "🚀 "*40)
    print("AI SNAPSHOT REPORTING AGENT - EXAMPLES")
    print("🚀 "*40)

    # Run individual examples
    # example_single_snapshot()
    # example_multiple_snapshots()
    # example_24h_coverage_report()
    # example_update_tracker()
    # example_ai_headline_extraction()

    # Or run complete workflow
    example_complete_workflow()

    print("\n" + "="*80)
    print("EXAMPLES COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Update example URLs to real publications")
    print("2. Add real client and Active logos")
    print("3. Configure your Anthropic API key for AI features")
    print("4. Run: python -m media_monitor --help")


if __name__ == "__main__":
    main()
