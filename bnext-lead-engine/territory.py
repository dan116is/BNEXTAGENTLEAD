"""
Bnext Lead Engine — Territory assignment.

Assigns an agent based on the lead's region field (set during discovery).
Fallback: nearest region by coordinate bounding box.
"""

import logging
from config import TERRITORY_AGENTS

logger = logging.getLogger("territory")

# Rough bounding boxes for fallback assignment
_BBOXES = {
    "north":     (31.5, 33.5, 34.8, 36.0),   # (lat_min, lat_max, lng_min, lng_max)
    "center":    (31.7, 32.2, 34.6, 35.3),
    "sharon":    (32.1, 32.6, 34.6, 35.2),
    "jerusalem": (31.5, 32.0, 34.8, 35.5),
    "south":     (29.5, 31.7, 34.3, 35.5),
}


def assign(lead: dict) -> str:
    region = lead.get("region")
    if region and region in TERRITORY_AGENTS:
        return TERRITORY_AGENTS[region]

    # Fallback by coordinates
    lat = lead.get("lat")
    lng = lead.get("lng")
    if lat is not None and lng is not None:
        for r, (la, lb, lo, lh) in _BBOXES.items():
            if la <= lat <= lb and lo <= lng <= lh:
                return TERRITORY_AGENTS.get(r, "agent_unassigned")

    logger.warning("Could not assign territory for lead: %s / %s", lead.get("name"), lead.get("city"))
    return "agent_unassigned"
