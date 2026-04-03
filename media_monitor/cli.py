"""
cli.py
------
Command-line interface with argparse.

Usage:
    python -m media_monitor collect --google                          # Google search collection
    python -m media_monitor collect --csv <path>                      # Manual CSV scan
    python -m media_monitor validate                                   # Validate database
    python -m media_monitor report 24h                                 # 24-hour report
    python -m media_monitor report weekly                              # Weekly report
    python -m media_monitor report monthly                             # Monthly report
    python -m media_monitor snapshot --url <url> --client <name> --magazine <name>  # Create snapshot
    python -m media_monitor coverage-24h --client <name> --campaign <name>          # 24h coverage report
    python -m media_monitor tracker update --client <name>             # Update Excel tracker
    python -m media_monitor tracker load --client <name>               # Load tracker records
"""

import argparse
import sys
from pathlib import Path

from media_monitor.data_collection import (
    google_search_collect,
    load_db,
    manual_scan_collect,
    merge_records,
    save_db,
)
from media_monitor.reporting import report_24h, report_monthly, report_weekly
from media_monitor.snapshot_reporting import (
    create_snapshot,
    create_24h_coverage,
    create_or_update_tracker,
    load_tracker,
)
from media_monitor.utils import get_logger
from media_monitor.validation import validate_all

log = get_logger(__name__)


def cmd_collect(args):
    """Handle 'collect' subcommand."""
    existing = load_db()

    if args.google:
        log.info("Starting Google Search collection…")
        new_records = google_search_collect()
    elif args.csv:
        log.info("Starting Manual CSV scan collection…")
        new_records = manual_scan_collect(args.csv)
    else:
        log.error("Must specify --google or --csv")
        return 1

    merged, added = merge_records(existing, new_records)
    save_db(merged)
    log.info("Collected %d new records (total: %d)", added, len(merged))
    return 0


def cmd_validate(args):
    """Handle 'validate' subcommand."""
    records = load_db()
    report = validate_all(records)

    print("\n" + "═" * 72)
    print("  VALIDATION REPORT")
    print("═" * 72)
    for line in report.summary_lines():
        print(line)
    print()

    if report.issues:
        print(f"  Total issues found: {len(report.issues)}\n")
        for issue in report.issues[:10]:  # Show first 10
            print(f"    [{issue.severity}] {issue.source} → {issue.field}")
            print(f"           {issue.message}")
        if len(report.issues) > 10:
            print(f"\n  ... and {len(report.issues) - 10} more issues")
    print()

    return 0 if report.pass_rate >= 0.95 else 1


def cmd_report(args):
    """Handle 'report' subcommand."""
    records = load_db()

    if not records:
        log.error("No records in database. Run 'collect' first.")
        return 1

    if args.window == "24h":
        report_24h(records, export=True)
    elif args.window == "weekly":
        report_weekly(records, export=True)
    elif args.window == "monthly":
        report_monthly(records, export=True)
    else:
        log.error("Unknown window: %s", args.window)
        return 1

    return 0


def cmd_snapshot(args):
    """Handle 'snapshot' subcommand - Create snapshot of a URL."""
    if not args.url:
        log.error("URL is required (use --url)")
        return 1
    if not args.client:
        log.error("Client name is required (use --client)")
        return 1
    if not args.magazine:
        log.error("Magazine/publication name is required (use --magazine)")
        return 1

    result = create_snapshot(
        client_name=args.client,
        magazine_name=args.magazine,
        publishing_date=args.date or str(__import__('datetime').datetime.now().date()),
        url=args.url,
        headline=args.headline,
        client_logo_path=args.client_logo,
        active_logo_path=args.active_logo,
    )

    if result:
        print(f"\n✓ Snapshot created successfully at: {result}\n")
        return 0
    else:
        log.error("Failed to create snapshot")
        return 1


def cmd_coverage_24h(args):
    """Handle 'coverage-24h' subcommand - Create 24-hour coverage report."""
    if not args.client:
        log.error("Client name is required (use --client)")
        return 1
    if not args.campaign:
        log.error("Campaign/press release name is required (use --campaign)")
        return 1

    # Load records from database
    records = load_db()
    if not records:
        log.warning("No records in database. Creating report with empty data.")
        records = []

    result = create_24h_coverage(
        client_name=args.client,
        press_release_name=args.campaign,
        coverage_data=records,
        client_logo_path=args.client_logo,
        active_logo_path=args.active_logo,
    )

    if result:
        print(f"\n✓ 24-hour coverage report created successfully at: {result}\n")
        return 0
    else:
        log.error("Failed to create 24-hour coverage report")
        return 1


def cmd_tracker(args):
    """Handle 'tracker' subcommand - Create or update Excel tracker."""
    if not args.action:
        log.error("Action is required: 'update' or 'load'")
        return 1

    if args.action == "update":
        records = load_db()
        if not records:
            log.warning("No records in database. Creating empty tracker entry.")
            records = []

        result = create_or_update_tracker(
            records=records,
            client_name=args.client,
        )

        if result:
            print(f"\n✓ Tracker updated successfully at: {result}\n")
            return 0
        else:
            log.error("Failed to update tracker")
            return 1

    elif args.action == "load":
        records = load_tracker(client_filter=args.client)
        if records:
            print(f"\n✓ Loaded {len(records)} records from tracker")
            if args.client:
                print(f"  Filter: {args.client}\n")
            for record in records[:5]:
                print(f"  - {record.get('Source', 'N/A')}: {record.get('Headline', 'N/A')[:50]}")
            if len(records) > 5:
                print(f"  ... and {len(records) - 5} more\n")
            return 0
        else:
            log.warning("No records found in tracker")
            return 0
    else:
        log.error(f"Unknown action: {args.action}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Media coverage monitor for Denodo × Snowflake announcement with AI snapshot reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m media_monitor collect --google
  python -m media_monitor collect --csv sample_manual_scan.csv
  python -m media_monitor validate
  python -m media_monitor report 24h
  python -m media_monitor report weekly
  python -m media_monitor report monthly
  python -m media_monitor snapshot --url https://example.com --client Denodo --magazine TechNews
  python -m media_monitor coverage-24h --client Denodo --campaign "Q1 Launch"
  python -m media_monitor tracker update --client Denodo
  python -m media_monitor tracker load --client Denodo
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # ── Collect ───────────────────────────────────────────────────────────────
    collect_parser = subparsers.add_parser("collect", help="Collect coverage data")
    collect_group  = collect_parser.add_mutually_exclusive_group(required=True)
    collect_group.add_argument(
        "--google",
        action="store_true",
        help="Run Google Search collection (mocked)",
    )
    collect_group.add_argument(
        "--csv",
        type=str,
        help="Load from manual CSV scan",
    )
    collect_parser.set_defaults(func=cmd_collect)

    # ── Validate ──────────────────────────────────────────────────────────────
    validate_parser = subparsers.add_parser("validate", help="Validate database")
    validate_parser.set_defaults(func=cmd_validate)

    # ── Report ────────────────────────────────────────────────────────────────
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_parser.add_argument(
        "window",
        choices=["24h", "weekly", "monthly"],
        help="Report time window",
    )
    report_parser.set_defaults(func=cmd_report)

    # ── Snapshot ──────────────────────────────────────────────────────────────
    snapshot_parser = subparsers.add_parser("snapshot", help="Create URL snapshot (Word document)")
    snapshot_parser.add_argument("--url", type=str, required=True, help="URL to snapshot")
    snapshot_parser.add_argument("--client", type=str, required=True, help="Client name")
    snapshot_parser.add_argument("--magazine", type=str, required=True, help="Magazine/publication name")
    snapshot_parser.add_argument("--date", type=str, help="Publication date (YYYY-MM-DD)")
    snapshot_parser.add_argument("--headline", type=str, help="Article headline")
    snapshot_parser.add_argument("--client-logo", type=str, help="Path to client logo image")
    snapshot_parser.add_argument("--active-logo", type=str, help="Path to Active logo image")
    snapshot_parser.set_defaults(func=cmd_snapshot)

    # ── Coverage 24h ──────────────────────────────────────────────────────────
    coverage_parser = subparsers.add_parser("coverage-24h", help="Create 24-hour coverage report (Word document)")
    coverage_parser.add_argument("--client", type=str, required=True, help="Client name")
    coverage_parser.add_argument("--campaign", type=str, required=True, help="Campaign/press release name")
    coverage_parser.add_argument("--client-logo", type=str, help="Path to client logo image")
    coverage_parser.add_argument("--active-logo", type=str, help="Path to Active logo image")
    coverage_parser.set_defaults(func=cmd_coverage_24h)

    # ── Tracker ───────────────────────────────────────────────────────────────
    tracker_parser = subparsers.add_parser("tracker", help="Create/update/load Excel tracker")
    tracker_parser.add_argument("action", choices=["update", "load"], help="Tracker action")
    tracker_parser.add_argument("--client", type=str, help="Client name (optional filter)")
    tracker_parser.set_defaults(func=cmd_tracker)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
