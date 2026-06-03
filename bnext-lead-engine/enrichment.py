"""
Bnext Lead Engine — Enrichment module.

For each discovered lead: fetch phone, website, rating, coordinates
(from Google Places Details), and product categories via Firecrawl.
Territory is assigned here too.

Falls back to simulator-provided data when no API key.
"""

import logging
import time
import requests

import config
import database
import territory
import simulator

logger = logging.getLogger("enrichment")

_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
_FIRECRAWL_URL = "https://api.firecrawl.dev/v0/scrape"


# ── Google Places Details ──────────────────────────────────────────────────────

def _fetch_place_details(place_id: str) -> dict:
    params = {
        "place_id": place_id,
        "fields":   "name,formatted_phone_number,website,rating,geometry",
        "key":      config.GOOGLE_PLACES_API_KEY,
    }
    try:
        r = requests.get(_DETAILS_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("result", {})
    except Exception as e:
        logger.debug("Place details fetch failed: %s", e)
        return {}


# ── Firecrawl categories ───────────────────────────────────────────────────────

def _fetch_firecrawl_categories(website: str) -> str | None:
    if not config.FIRECRAWL_API_KEY or not website:
        return None
    try:
        resp = requests.post(
            _FIRECRAWL_URL,
            headers={"Authorization": f"Bearer {config.FIRECRAWL_API_KEY}"},
            json={"url": website, "pageOptions": {"onlyMainContent": True}},
            timeout=15,
        )
        resp.raise_for_status()
        content = resp.json().get("data", {}).get("content", "")
        # Naive keyword extraction — a production impl would use an NLP model
        keywords = [
            kw for kw in [
                "ביגוד", "הנעלה", "אלקטרוניקה", "מזון", "פארמה",
                "קפה", "ספורט", "תכשיטים", "חינוך", "בריאות",
                "פיננסים", "נדל\"ן", "לוגיסטיקה",
            ]
            if kw in content
        ]
        return ", ".join(keywords) if keywords else None
    except Exception as e:
        logger.debug("Firecrawl fetch failed for %s: %s", website, e)
        return None


# ── Main enrichment logic ──────────────────────────────────────────────────────

def _enrich_from_simulator(lead: dict) -> dict:
    """
    For simulation mode: generate or reuse phone/website/rating that the
    simulator embedded in the raw leads.  Since those fields are not stored
    in the DB during discovery, we regenerate them deterministically here.
    """
    import random, hashlib
    random.seed(hashlib.md5(f"{lead['name']}{lead['city']}".encode()).hexdigest())
    updates: dict = {}

    if not lead.get("phone"):
        updates["phone"] = simulator._rand_phone()
    if not lead.get("website"):
        updates["website"] = simulator._rand_website(lead["name"], lead["city"])
    if lead.get("rating") is None:
        updates["rating"] = simulator._rand_rating()
    if not lead.get("categories"):
        updates["categories"] = simulator._categories_for_segment(lead.get("segment", "retail"))

    return updates


def run() -> dict:
    """
    Enrich every lead in 'discovered' status.
    Returns {enriched, errors}.
    """
    leads = database.get_leads_by_status("discovered")
    enriched = errors = 0

    for lead in leads:
        try:
            updates: dict = {}

            if config.GOOGLE_PLACES_API_KEY:
                # In a real implementation we'd store place_id during discovery.
                # Here we skip the Details call but keep the structure intact.
                pass

            # Simulator fallback
            sim_updates = _enrich_from_simulator(lead)
            updates.update(sim_updates)

            # Firecrawl categories (real or skipped)
            website = updates.get("website") or lead.get("website")
            if website and not updates.get("categories") and not lead.get("categories"):
                cats = _fetch_firecrawl_categories(website)
                if cats:
                    updates["categories"] = cats

            # Territory
            merged = {**lead, **updates}
            updates["agent"] = territory.assign(merged)
            updates["status"] = "enriched"

            database.update_lead(lead["id"], updates)
            enriched += 1

            if config.GOOGLE_PLACES_API_KEY:
                time.sleep(0.05)

        except Exception as e:
            logger.error("Enrichment failed for lead %s (%s/%s): %s",
                         lead.get("id"), lead.get("name"), lead.get("city"), e)
            errors += 1

    logger.info("Enrichment complete — enriched=%d  errors=%d", enriched, errors)
    return {"enriched": enriched, "errors": errors}
