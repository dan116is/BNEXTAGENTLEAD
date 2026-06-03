"""
Bnext Lead Engine — Segmentation and routing.

Finalises segment classification and assigns channel + sales angle.
Segment is already set from discovery; this step validates and writes routing.
"""

import logging

import config
import database

logger = logging.getLogger("segmentation")

_KNOWN_SEGMENTS = set(config.SEGMENT_ROUTING.keys())


def _classify(lead: dict) -> str:
    """
    If segment is already valid, keep it.
    Otherwise try to infer from name keywords, else default to 'retail'.
    """
    seg = lead.get("segment", "")
    if seg in _KNOWN_SEGMENTS:
        return seg

    name = (lead.get("name") or "").lower()
    cats = (lead.get("categories") or "").lower()
    combined = name + " " + cats

    if any(k in combined for k in ["chain", "רשת", "supermarket", "pharma", "mega"]):
        return "chain"
    if any(k in combined for k in ["union", "ועד", "הסתדרות", "workers", "employee"]):
        return "employee_org"
    if any(k in combined for k in ["school", "hospital", "עמותה", "מוסד", "ארגון", "non-profit"]):
        return "institution"
    return "retail"


def run() -> dict:
    """
    Segment and route every lead in 'enriched' status.
    Returns {routed, by_segment}.
    """
    leads = database.get_leads_by_status("enriched")
    routed = 0
    by_segment: dict[str, int] = {}
    errors = 0

    for lead in leads:
        try:
            segment = _classify(lead)
            routing = config.SEGMENT_ROUTING[segment]
            updates = {
                "segment":    segment,
                "channel":    routing["channel"],
                "sales_angle": routing["angle"],
                "status":     "routed",
            }
            database.update_lead(lead["id"], updates)
            by_segment[segment] = by_segment.get(segment, 0) + 1
            routed += 1
        except Exception as e:
            logger.error("Segmentation failed for lead %s: %s", lead.get("id"), e)
            errors += 1

    logger.info(
        "Segmentation complete — routed=%d  by_segment=%s  errors=%d",
        routed, by_segment, errors,
    )
    return {"routed": routed, "by_segment": by_segment, "errors": errors}
