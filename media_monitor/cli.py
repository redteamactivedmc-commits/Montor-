"""
cli.py
------
Command-line interface with argparse.

Usage:
    python -m media_monitor collect --google          # Google search collection
    python -m media_monitor collect --csv <path>      # Manual CSV scan
    python -m media_monitor validate                   # Validate database
    python -m media_monitor report 24h                 # 24-hour report
    python -m media_monitor report weekly              # Weekly report
    python -m media_monitor report monthly             # Monthly report
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Media coverage monitor for Denodo × Snowflake announcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m media_monitor collect --google
  python -m media_monitor collect --csv sample_manual_scan.csv
  python -m media_monitor validate
  python -m media_monitor report 24h
  python -m media_monitor report weekly
  python -m media_monitor report monthly
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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
