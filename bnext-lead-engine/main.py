"""
Bnext Lead Engine — Orchestrator.

Runs the full pipeline:
  1. Discovery  — Google Places scan → DB (deduplication)
  2. Enrichment — phone, website, rating, territory, Firecrawl categories
  3. Segmentation / routing — channel + sales angle
  4. Reporting  — print summary and persist run log
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("engine.log"),
    ],
)
logger = logging.getLogger("main")

import config
import database
import discovery
import enrichment
import segmentation
import reporter


def main() -> None:
    logger.info("═" * 60)
    logger.info("BNEXT LEAD ENGINE  starting")
    if not config.GOOGLE_PLACES_API_KEY:
        logger.info("MODE: simulation  (set GOOGLE_PLACES_API_KEY for live data)")
    else:
        logger.info("MODE: live  (Google Places API)")
    logger.info("═" * 60)

    database.init_db()

    # ── 1. Discovery ──────────────────────────────────────────────────────────
    logger.info("STAGE 1 — Discovery")
    disc_stats = discovery.run()

    # ── 2. Enrichment ─────────────────────────────────────────────────────────
    logger.info("STAGE 2 — Enrichment")
    enrich_stats = enrichment.run()

    # ── 3. Segmentation / Routing ─────────────────────────────────────────────
    logger.info("STAGE 3 — Segmentation & Routing")
    seg_stats = segmentation.run()

    # ── 4. Report ─────────────────────────────────────────────────────────────
    run_stats = {
        **disc_stats,
        "enriched":       enrich_stats["enriched"],
        "enrich_errors":  enrich_stats["errors"],
        "routed":         seg_stats["routed"],
        "segment_errors": seg_stats["errors"],
    }
    database.log_run({
        "discovered": disc_stats["inserted"],
        "enriched":   enrich_stats["enriched"],
        "routed":     seg_stats["routed"],
        "errors":     str(enrich_stats["errors"] + seg_stats["errors"]) or None,
    })

    reporter.print_report(run_stats)

    total_errors = enrich_stats["errors"] + seg_stats["errors"]
    if total_errors:
        logger.warning("Pipeline finished with %d error(s) — see engine.log", total_errors)
        sys.exit(1)
    else:
        logger.info("Pipeline finished successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
