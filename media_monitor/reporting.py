"""
reporting.py
------------
Three report types:

  • 24-hour coverage update  — rapid snapshot, console + Excel
  • Weekly summary           — trend tables + chart, console + Excel
  • Monthly campaign report  — full analytics, console + Excel + HTML

Each public function accepts a list[dict] of coverage records and writes
artifacts to reports/.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    def tabulate(data, headers=(), tablefmt="grid", **kw):  # type: ignore
        """Minimal fallback when tabulate is not installed."""
        if not data:
            return "(no data)"
        rows = ["\t".join(str(c) for c in row) for row in data]
        header = "\t".join(str(h) for h in headers)
        return header + "\n" + "\n".join(rows)

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from media_monitor.utils import (
    REPORTS_DIR,
    ensure_dirs,
    get_logger,
    number_fmt,
    pct,
    truncate,
    utcnow,
)

log = get_logger(__name__)


# ── Shared helpers ────────────────────────────────────────────────────────────

def _filter_by_window(records: list[dict], days: int) -> list[dict]:
    """Return records whose publication_date falls within the last *days* days."""
    cutoff = (utcnow() - timedelta(days=days)).date()
    out = []
    for r in records:
        raw = r.get("publication_date", "")
        try:
            dt = datetime.strptime(raw[:10], "%Y-%m-%d").date()
            if dt >= cutoff:
                out.append(r)
        except ValueError:
            out.append(r)  # keep records with unparseable dates
    return out


def _tier_sort_key(tier: str) -> int:
    return {"Tier 1": 0, "Tier 2": 1, "Tier 3": 2}.get(tier, 3)


def _report_path(name: str, ext: str) -> Path:
    ensure_dirs()
    ts = utcnow().strftime("%Y%m%d_%H%M%S")
    return REPORTS_DIR / f"{name}_{ts}.{ext}"


def _section(title: str, width: int = 72) -> None:
    """Print a bold section divider to stdout."""
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def _kpi_box(label: str, value: str, width: int = 24) -> str:
    """Return a single KPI box string."""
    inner = f" {label} ".center(width - 2, "─")
    return f"┌{inner}┐\n│{str(value).center(width - 2)}│\n└{'─' * (width - 2)}┘"


def _print_kpis(kpis: dict[str, str]) -> None:
    """Print KPI boxes side-by-side."""
    boxes = [_kpi_box(k, v) for k, v in kpis.items()]
    lines_per_box = 3
    rows: list[list[str]] = [[] for _ in range(lines_per_box)]
    for box in boxes:
        for i, line in enumerate(box.split("\n")):
            rows[i].append(line)
    for row in rows:
        print("  ".join(row))
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  REPORT 1 — 24-HOUR COVERAGE UPDATE
# ─────────────────────────────────────────────────────────────────────────────

def report_24h(records: list[dict], export: bool = True) -> dict:
    """
    Generate a 24-hour coverage update.
    Returns a summary dict and optionally writes an Excel file.
    """
    window = _filter_by_window(records, days=1)
    _section("24-HOUR COVERAGE UPDATE  ·  Denodo × Snowflake  ·  Middle East")
    print(f"  Report generated : {utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Window           : Last 24 hours")
    print(f"  Total hits found : {len(window)}")
    print()

    if not window:
        print("  No new coverage in the last 24 hours.\n")
        return {"window": "24h", "total": 0, "records": []}

    # KPIs
    total_umv  = sum(r.get("umv", 0) for r in window)
    total_imp  = sum(r.get("impressions", 0) for r in window)
    avg_pt     = (sum(r.get("message_pullthrough", 0) for r in window) / len(window))
    tier1_hits = sum(1 for r in window if r.get("tier") == "Tier 1")

    _print_kpis({
        "Articles":     str(len(window)),
        "Tier-1 Hits":  str(tier1_hits),
        "Total UMV":    number_fmt(total_umv),
        "Impressions":  number_fmt(total_imp),
        "Avg Pull-thru": pct(avg_pt),
    })

    # Sortable table
    rows = []
    for r in sorted(window, key=lambda x: _tier_sort_key(x.get("tier", ""))):
        rows.append([
            r.get("tier", "?"),
            truncate(r.get("source", "?"), 28),
            truncate(r.get("headline", ""), 55),
            r.get("market", "?"),
            r.get("publication_date", "?"),
            number_fmt(r.get("umv", 0)),
            pct(r.get("message_pullthrough", 0)),
        ])

    headers = ["Tier", "Source", "Headline", "Market", "Date", "UMV", "Pull-thru"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print()

    summary = {
        "window":        "24h",
        "total":         len(window),
        "tier_1_hits":   tier1_hits,
        "total_umv":     total_umv,
        "total_impressions": total_imp,
        "avg_pullthrough": round(avg_pt, 4),
        "records":       window,
    }

    if export and HAS_PANDAS:
        df   = pd.DataFrame(window)
        path = _report_path("24h_coverage_update", "xlsx")
        df.to_excel(str(path), sheet_name="24h Coverage", index=False)
        print(f"  ✓  Excel saved → {path}\n")

    return summary


# ─────────────────────────────────────────────────────────────────────────────
#  REPORT 2 — WEEKLY SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def report_weekly(records: list[dict], export: bool = True) -> dict:
    """
    Generate a weekly summary with tier breakdown and market distribution.
    """
    window = _filter_by_window(records, days=7)
    _section("WEEKLY SUMMARY REPORT  ·  Denodo × Snowflake  ·  Middle East")
    print(f"  Report generated : {utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Window           : Last 7 days")
    print(f"  Total articles   : {len(window)}\n")

    if not window:
        print("  No coverage in the last 7 days.\n")
        return {"window": "weekly", "total": 0, "records": []}

    # ── Tier breakdown ────────────────────────────────────────────────────────
    tier_counter: Counter = Counter(r.get("tier", "Unknown") for r in window)
    tier_umv:     dict    = defaultdict(int)
    tier_imp:     dict    = defaultdict(int)
    tier_pt:      dict    = defaultdict(list)

    for r in window:
        t = r.get("tier", "Unknown")
        tier_umv[t] += r.get("umv", 0)
        tier_imp[t] += r.get("impressions", 0)
        tier_pt[t].append(r.get("message_pullthrough", 0))

    _section("  Tier Breakdown")
    tier_rows = []
    for tier in ["Tier 1", "Tier 2", "Tier 3", "Unknown"]:
        count = tier_counter.get(tier, 0)
        if count == 0:
            continue
        avg_pt_tier = sum(tier_pt[tier]) / len(tier_pt[tier])
        tier_rows.append([
            tier,
            count,
            number_fmt(tier_umv[tier]),
            number_fmt(tier_imp[tier]),
            pct(avg_pt_tier),
        ])
    print(tabulate(tier_rows,
                   headers=["Tier", "Articles", "Total UMV", "Impressions", "Avg Pull-thru"],
                   tablefmt="grid"))

    # ── Market breakdown ──────────────────────────────────────────────────────
    market_counter: Counter = Counter(r.get("market", "Unknown") for r in window)
    _section("  Market Distribution")
    market_rows = sorted(
        [[m, c, pct(c / len(window))] for m, c in market_counter.items()],
        key=lambda x: -x[1],
    )
    print(tabulate(market_rows,
                   headers=["Market", "Articles", "Share"],
                   tablefmt="grid"))

    # ── Top articles by UMV ───────────────────────────────────────────────────
    _section("  Top 5 Articles by UMV")
    top5 = sorted(window, key=lambda x: x.get("umv", 0), reverse=True)[:5]
    top5_rows = [
        [
            truncate(r.get("source", "?"), 22),
            truncate(r.get("headline", ""), 50),
            r.get("market", "?"),
            r.get("tier", "?"),
            number_fmt(r.get("umv", 0)),
            pct(r.get("message_pullthrough", 0)),
        ]
        for r in top5
    ]
    print(tabulate(top5_rows,
                   headers=["Source", "Headline", "Market", "Tier", "UMV", "Pull-thru"],
                   tablefmt="grid"))

    # ── Message pull-through table ────────────────────────────────────────────
    from media_monitor import KEY_MESSAGES
    _section("  Key Message Pull-Through")
    msg_counts = {
        msg: sum(1 for r in window if msg in r.get("messages_covered", []))
        for msg in KEY_MESSAGES
    }
    msg_rows = sorted(
        [[m, c, pct(c / len(window))] for m, c in msg_counts.items()],
        key=lambda x: -x[1],
    )
    print(tabulate(msg_rows,
                   headers=["Key Message", "# Articles", "Coverage Rate"],
                   tablefmt="grid"))
    print()

    summary = {
        "window":        "weekly",
        "total":         len(window),
        "tier_breakdown": dict(tier_counter),
        "market_breakdown": dict(market_counter),
        "message_coverage": msg_counts,
        "records":       window,
    }

    if export and HAS_PANDAS:
        df   = pd.DataFrame(window)
        path = _report_path("weekly_summary", "xlsx")
        df.to_excel(str(path), sheet_name="Weekly Coverage", index=False)
        print(f"  ✓  Excel saved → {path}\n")

    return summary


# ─────────────────────────────────────────────────────────────────────────────
#  REPORT 3 — MONTHLY CAMPAIGN REPORT
# ─────────────────────────────────────────────────────────────────────────────

def report_monthly(records: list[dict], export: bool = True) -> dict:
    """
    Full monthly campaign report with comprehensive analysis.
    """
    window = _filter_by_window(records, days=30)
    _section("MONTHLY CAMPAIGN REPORT  ·  Denodo × Snowflake  ·  Middle East")
    print(f"  Report generated : {utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Window           : Last 30 days")
    print()

    if not window:
        print("  No coverage in the last 30 days.\n")
        return {"window": "monthly", "total": 0, "records": []}

    # ── Executive KPIs ────────────────────────────────────────────────────────
    total_umv  = sum(r.get("umv", 0)         for r in window)
    total_imp  = sum(r.get("impressions", 0) for r in window)
    avg_pt     = sum(r.get("message_pullthrough", 0) for r in window) / len(window)
    tier1_pct  = sum(1 for r in window if r.get("tier") == "Tier 1") / len(window)
    unique_src = len({r.get("source") for r in window})

    _section("  Executive Summary")
    _print_kpis({
        "Total Articles":  str(len(window)),
        "Unique Sources":  str(unique_src),
        "Total UMV Reach": number_fmt(total_umv),
        "Est. Impressions": number_fmt(total_imp),
        "Avg Pull-thru":   pct(avg_pt),
        "Tier-1 Share":    pct(tier1_pct),
    })

    # ── Full coverage table ───────────────────────────────────────────────────
    _section("  Full Coverage Log")
    sorted_recs = sorted(
        window,
        key=lambda x: (_tier_sort_key(x.get("tier", "")), x.get("publication_date", "")),
    )
    full_rows = [
        [
            r.get("tier", "?"),
            truncate(r.get("source", "?"), 24),
            r.get("market", "?"),
            r.get("publication_date", "?"),
            truncate(r.get("headline", ""), 52),
            number_fmt(r.get("umv", 0)),
            number_fmt(r.get("impressions", 0)),
            pct(r.get("message_pullthrough", 0)),
        ]
        for r in sorted_recs
    ]
    print(tabulate(
        full_rows,
        headers=["Tier", "Source", "Market", "Date", "Headline",
                 "UMV", "Impressions", "Pull-thru"],
        tablefmt="grid",
    ))

    # ── Source-level deep dive ────────────────────────────────────────────────
    _section("  Source Performance")
    source_stats: dict = defaultdict(lambda: {"count": 0, "umv": 0, "imp": 0, "pt": []})
    for r in window:
        s = r.get("source", "Unknown")
        source_stats[s]["count"] += 1
        source_stats[s]["umv"]   += r.get("umv", 0)
        source_stats[s]["imp"]   += r.get("impressions", 0)
        source_stats[s]["pt"].append(r.get("message_pullthrough", 0))

    src_rows = []
    for src, stats in sorted(source_stats.items(), key=lambda x: -x[1]["umv"]):
        avg_pt_src = sum(stats["pt"]) / len(stats["pt"])
        src_rows.append([
            truncate(src, 26),
            stats["count"],
            number_fmt(stats["umv"]),
            number_fmt(stats["imp"]),
            pct(avg_pt_src),
        ])
    print(tabulate(src_rows,
                   headers=["Source", "Articles", "Total UMV", "Impressions", "Avg Pull-thru"],
                   tablefmt="grid"))
    print()

    # ── Excel export ──────────────────────────────────────────────────────────
    if export and HAS_PANDAS:
        excel_path = _report_path("monthly_campaign_report", "xlsx")
        df = pd.DataFrame(window)
        df.to_excel(str(excel_path), sheet_name="Coverage Data", index=False)
        print(f"  ✓  Excel saved → {excel_path}\n")

    return {
        "window":        "monthly",
        "total":         len(window),
        "total_umv":     total_umv,
        "total_impressions": total_imp,
        "avg_pullthrough": round(avg_pt, 4),
        "tier1_share":   round(tier1_pct, 4),
        "unique_sources": unique_src,
        "records":        window,
    }
