"""
Bnext Lead Engine — Run report generator.
"""

import logging
from datetime import datetime

import database

logger = logging.getLogger("reporter")

_SEP = "─" * 60


def print_report(run_stats: dict) -> None:
    counts = database.count_leads()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'═'*60}")
    print(f"  BNEXT LEAD ENGINE — RUN REPORT  [{ts}]")
    print(f"{'═'*60}")

    # Pipeline summary
    print(f"\n  PIPELINE")
    print(f"  {_SEP}")
    print(f"  Leads scanned from source : {run_stats.get('total_scanned', 0):>6,}")
    print(f"  New leads inserted (dedup): {run_stats.get('inserted', 0):>6,}")
    print(f"  Duplicate skips           : {run_stats.get('skipped', 0):>6,}")
    print(f"  Leads enriched            : {run_stats.get('enriched', 0):>6,}")
    print(f"  Leads routed              : {run_stats.get('routed', 0):>6,}")

    # By segment
    print(f"\n  BY SEGMENT")
    print(f"  {_SEP}")
    for seg, cnt in sorted(counts["by_segment"].items()):
        routing = {
            "retail": "WhatsApp",
            "employee_org": "WhatsApp",
            "chain": "Email",
            "institution": "Email",
        }.get(seg, "—")
        print(f"  {seg:<20} {cnt:>5,}  →  channel: {routing}")

    # By region / territory
    print(f"\n  BY REGION / AGENT TERRITORY")
    print(f"  {_SEP}")
    for region, cnt in sorted(counts["by_region"].items()):
        print(f"  {region:<20} {cnt:>5,}")

    # By channel
    print(f"\n  BY OUTREACH CHANNEL")
    print(f"  {_SEP}")
    for channel, cnt in sorted(counts["by_channel"].items()):
        print(f"  {channel:<20} {cnt:>5,}")

    # Data quality flags
    errors = run_stats.get("enrich_errors", 0) + run_stats.get("segment_errors", 0)
    print(f"\n  DATA QUALITY")
    print(f"  {_SEP}")
    if errors == 0:
        print("  No errors detected.")
    else:
        print(f"  ⚠  Errors: {errors}  (check engine.log for details)")

    print(f"\n  Total leads in DB: {counts['total']:,}")
    print(f"{'═'*60}\n")
