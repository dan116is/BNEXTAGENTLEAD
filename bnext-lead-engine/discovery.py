"""
Bnext Lead Engine — Discovery module.

Scans Google Places Text Search across Israel's 50 cities using
segment-specific queries.  Falls back to simulator when no API key.
"""

import logging
import time
import requests
from typing import Generator

import config
import database
import simulator

logger = logging.getLogger("discovery")

_PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


def _google_places_query(query: str, city: dict) -> list[dict]:
    """Single Google Places Text Search page (max 20 results)."""
    params = {
        "query":    f"{query} in {city['name']} Israel",
        "key":      config.GOOGLE_PLACES_API_KEY,
        "language": "he",
        "region":   "il",
    }
    try:
        resp = requests.get(_PLACES_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            logger.warning("Places API status %s for query '%s' in %s",
                           data.get("status"), query, city["name"])
            return []
        return data.get("results", [])
    except Exception as e:
        logger.error("Places API error: %s", e)
        return []


def _places_to_lead(result: dict, segment: str, city: dict) -> dict:
    geo = result.get("geometry", {}).get("location", {})
    return {
        "name":    result.get("name", ""),
        "city":    city["name"],
        "segment": segment,
        "rating":  result.get("rating"),
        "lat":     geo.get("lat", city["lat"]),
        "lng":     geo.get("lng", city["lng"]),
        "region":  city["region"],
        "phone":   None,
        "website": None,
        "categories": None,
    }


def _scan_live() -> Generator[dict, None, None]:
    """Scan real Google Places API — one request per (segment, query, city)."""
    for city in config.ISRAEL_CITIES:
        for segment, queries in config.SEGMENT_QUERIES.items():
            for query in queries:
                results = _google_places_query(query, city)
                for r in results:
                    yield _places_to_lead(r, segment, city)
                time.sleep(0.05)   # respect rate limits


def run() -> dict:
    """
    Discover leads and write to DB.
    Returns {inserted, skipped, total_scanned}.
    """
    database.init_db()

    if config.GOOGLE_PLACES_API_KEY:
        logger.info("Running LIVE discovery via Google Places API")
        raw_leads = list(_scan_live())
    else:
        logger.info("No Google Places API key — using simulator")
        raw_leads = simulator.generate_all_leads()

    inserted = skipped = 0
    for lead in raw_leads:
        if not lead.get("name") or not lead.get("city"):
            skipped += 1
            continue
        ok = database.insert_lead({
            "name":    lead["name"],
            "city":    lead["city"],
            "segment": lead["segment"],
            "lat":     lead.get("lat"),
            "lng":     lead.get("lng"),
            "region":  lead.get("region"),
        })
        if ok:
            inserted += 1
        else:
            skipped += 1

    logger.info(
        "Discovery complete — scanned=%d  inserted=%d  duplicates_skipped=%d",
        len(raw_leads), inserted, skipped,
    )
    return {"total_scanned": len(raw_leads), "inserted": inserted, "skipped": skipped}
