"""
Bnext Lead Engine — Realistic data simulator.
Used when Google Places / Firecrawl API keys are absent.
Generates plausible Israeli business leads for all 4 segments.
"""

import random
import hashlib
from config import ISRAEL_CITIES, SEGMENT_QUERIES

random.seed(42)

# ── Name templates ─────────────────────────────────────────────────────────────

_RETAIL_PREFIXES = [
    "בוטיק", "חנות", "גלריה", "סטודיו", "מרכז", "אופנת", "עולם",
    "מגזין", "טרנד", "ספורט", "מתנות", "אקספרס",
]
_RETAIL_SUFFIXES = [
    "Fashion", "Style", "Plus", "Direct", "Pro", "One", "Store",
    "ישראל", "מרכז", "דיל", "שופ",
]
_RETAIL_NOUNS = [
    "אלמוג", "ורד", "שמש", "גל", "נחל", "כוכב", "ענן", "רוח",
    "ברק", "אריאל", "שחר", "אורן", "רונן", "יעל", "דגן",
]

_CHAIN_NAMES = [
    "Super-Bnext", "FreshMart", "PharmaCare", "MegaSport", "TechHub",
    "FoodCity", "ClothingPlus", "CoffeeNation", "BurgerZone", "PizzeriaRing",
    "SuperDeal", "MaxFashion", "HomeCenter", "ElectroCity", "GreenMarket",
    "QuickStop", "HealthPlus", "FitnessWorld", "AutoMax", "PetLand",
]
_CHAIN_SUFFIXES = ["סניף", "מרכז", "פלוס", "מגה", "הייפר"]

_INSTITUTION_NAMES = [
    "עמותת נתינה", "בית ספר עמל", "גן ילדים הקשת", "מועדון קהילתי",
    "מרכז רפואי", "אגודת נשים", "ארגון הצעירים", "מכון ספיר",
    "בית ספר אורט", "עמותת יד ביד", "קרן רווחה", "עמותת חברים",
    "מרכז קהילתי", "גן ציבורי", "כפר ילדים",
]

_EMPLOYEE_ORG_NAMES = [
    "ועד עובדי עיריית", "הסתדרות עובדי", "ועד עובדים מפעל",
    "ארגון עובדי", "איגוד עובדי", "מועצת עובדי",
    "ועד עובדי בית חולים", "ועד עובדי מכון",
    "הסתדרות הפועלים", "אגוד ועדי עובדים",
]


def _rand_phone() -> str:
    prefixes = ["050", "052", "053", "054", "055", "058", "02", "03", "04", "08", "09"]
    p = random.choice(prefixes)
    if len(p) == 3:
        return f"{p}-{random.randint(1000000, 9999999)}"
    return f"{p}-{random.randint(1000000, 9999999)}"


def _rand_website(name: str, city: str) -> str | None:
    if random.random() < 0.55:
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace("/", "")
            .encode("ascii", errors="ignore")
            .decode()
        )
        slug = slug or hashlib.md5(name.encode()).hexdigest()[:8]
        tld = random.choice(["co.il", "com", "il"])
        return f"https://www.{slug}.{tld}"
    return None


def _rand_rating() -> float | None:
    if random.random() < 0.75:
        return round(random.uniform(3.2, 5.0), 1)
    return None


def _jitter(val: float, amt: float = 0.04) -> float:
    return round(val + random.uniform(-amt, amt), 6)


def _categories_for_segment(segment: str) -> str:
    cats = {
        "retail": ["ביגוד", "הנעלה", "אביזרים", "אופנה", "מוצרי ספורט", "מתנות", "תכשיטים"],
        "chain": ["מזון", "פארמה", "אלקטרוניקה", "אופנה", "קפה", "מסעדות מזון מהיר"],
        "institution": ["חינוך", "רווחה", "בריאות", "קהילה", "עמותות", "שירותים ציבוריים"],
        "employee_org": ["הטבות לעובדים", "ניהול שכר", "ביטוח", "פנסיה", "רווחת עובדים"],
    }
    pool = cats.get(segment, [])
    chosen = random.sample(pool, min(2, len(pool)))
    return ", ".join(chosen)


# ── Per-segment generators ─────────────────────────────────────────────────────

def _retail_leads(city: dict, count: int) -> list[dict]:
    leads = []
    for _ in range(count):
        p = random.choice(_RETAIL_PREFIXES)
        n = random.choice(_RETAIL_NOUNS)
        s = random.choice(_RETAIL_SUFFIXES)
        name = f"{p} {n} {s}".strip()
        leads.append(_build(name, city, "retail"))
    return leads


def _chain_leads(city: dict, count: int) -> list[dict]:
    leads = []
    for _ in range(count):
        base = random.choice(_CHAIN_NAMES)
        sfx  = random.choice(_CHAIN_SUFFIXES)
        name = f"{base} {sfx} {city['name']}"
        leads.append(_build(name, city, "chain"))
    return leads


def _institution_leads(city: dict, count: int) -> list[dict]:
    leads = []
    for _ in range(count):
        base = random.choice(_INSTITUTION_NAMES)
        name = f"{base} {city['name']}"
        leads.append(_build(name, city, "institution"))
    return leads


def _employee_org_leads(city: dict, count: int) -> list[dict]:
    leads = []
    for _ in range(count):
        base = random.choice(_EMPLOYEE_ORG_NAMES)
        name = f"{base} {city['name']}"
        leads.append(_build(name, city, "employee_org"))
    return leads


def _build(name: str, city: dict, segment: str) -> dict:
    return {
        "name":    name,
        "city":    city["name"],
        "segment": segment,
        "lat":     _jitter(city["lat"]),
        "lng":     _jitter(city["lng"]),
        "region":  city["region"],
        "phone":   _rand_phone(),
        "website": _rand_website(name, city["name"]),
        "rating":  _rand_rating(),
        "categories": _categories_for_segment(segment),
    }


def generate_all_leads() -> list[dict]:
    """
    Generate ~800 realistic leads across all 50 cities × 4 segments.
    Counts per city per segment are randomised to mimic real density variation.
    """
    leads: list[dict] = []
    generators = {
        "retail":       _retail_leads,
        "chain":        _chain_leads,
        "institution":  _institution_leads,
        "employee_org": _employee_org_leads,
    }
    # Larger cities get more leads
    city_weights = {
        "Jerusalem": 5, "Tel Aviv": 6, "Haifa": 5, "Rishon LeZion": 4,
        "Petah Tikva": 4, "Netanya": 4, "Beersheba": 4,
    }
    for city in ISRAEL_CITIES:
        weight = city_weights.get(city["name"], 2)
        for seg, gen in generators.items():
            n = random.randint(weight, weight + 3)
            leads.extend(gen(city, n))
    return leads
