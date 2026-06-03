"""
Bnext Lead Engine — Configuration
"""

import os

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

# Israel's 50 largest cities with coordinates and region
ISRAEL_CITIES = [
    {"name": "Jerusalem",       "lat": 31.7683, "lng": 35.2137, "region": "jerusalem"},
    {"name": "Tel Aviv",        "lat": 32.0853, "lng": 34.7818, "region": "center"},
    {"name": "Haifa",           "lat": 32.7940, "lng": 34.9896, "region": "north"},
    {"name": "Rishon LeZion",   "lat": 31.9642, "lng": 34.8007, "region": "center"},
    {"name": "Petah Tikva",     "lat": 32.0840, "lng": 34.8878, "region": "center"},
    {"name": "Ashdod",          "lat": 31.8044, "lng": 34.6553, "region": "south"},
    {"name": "Netanya",         "lat": 32.3215, "lng": 34.8532, "region": "sharon"},
    {"name": "Beersheba",       "lat": 31.2530, "lng": 34.7915, "region": "south"},
    {"name": "Bnei Brak",       "lat": 32.0841, "lng": 34.8337, "region": "center"},
    {"name": "Holon",           "lat": 32.0100, "lng": 34.7798, "region": "center"},
    {"name": "Ramat Gan",       "lat": 32.0684, "lng": 34.8248, "region": "center"},
    {"name": "Rehovot",         "lat": 31.8928, "lng": 34.8113, "region": "center"},
    {"name": "Bat Yam",         "lat": 32.0216, "lng": 34.7497, "region": "center"},
    {"name": "Ashkelon",        "lat": 31.6688, "lng": 34.5743, "region": "south"},
    {"name": "Beit Shemesh",    "lat": 31.7427, "lng": 34.9933, "region": "jerusalem"},
    {"name": "Kfar Saba",       "lat": 32.1784, "lng": 34.9078, "region": "sharon"},
    {"name": "Herzliya",        "lat": 32.1643, "lng": 34.8439, "region": "sharon"},
    {"name": "Hadera",          "lat": 32.4372, "lng": 34.9170, "region": "sharon"},
    {"name": "Modiin",          "lat": 31.8940, "lng": 35.0096, "region": "center"},
    {"name": "Nazareth",        "lat": 32.6996, "lng": 35.3035, "region": "north"},
    {"name": "Lod",             "lat": 31.9519, "lng": 34.8956, "region": "center"},
    {"name": "Ramla",           "lat": 31.9298, "lng": 34.8701, "region": "center"},
    {"name": "Raanana",         "lat": 32.1840, "lng": 34.8710, "region": "sharon"},
    {"name": "Kiryat Gat",      "lat": 31.6100, "lng": 34.7700, "region": "south"},
    {"name": "Eilat",           "lat": 29.5577, "lng": 34.9519, "region": "south"},
    {"name": "Nahariya",        "lat": 33.0075, "lng": 35.0925, "region": "north"},
    {"name": "Afula",           "lat": 32.6078, "lng": 35.2890, "region": "north"},
    {"name": "Akko",            "lat": 32.9250, "lng": 35.0818, "region": "north"},
    {"name": "Kiryat Ata",      "lat": 32.8117, "lng": 35.1044, "region": "north"},
    {"name": "Kiryat Bialik",   "lat": 32.8222, "lng": 35.0762, "region": "north"},
    {"name": "Rosh HaAyin",     "lat": 32.0952, "lng": 34.9571, "region": "center"},
    {"name": "Givatayim",       "lat": 32.0705, "lng": 34.8111, "region": "center"},
    {"name": "Or Yehuda",       "lat": 32.0282, "lng": 34.8563, "region": "center"},
    {"name": "Netivot",         "lat": 31.4197, "lng": 34.5892, "region": "south"},
    {"name": "Kiryat Motzkin",  "lat": 32.8360, "lng": 35.0778, "region": "north"},
    {"name": "Dimona",          "lat": 31.0680, "lng": 35.0321, "region": "south"},
    {"name": "Tiberias",        "lat": 32.7922, "lng": 35.5312, "region": "north"},
    {"name": "Sderot",          "lat": 31.5236, "lng": 34.5960, "region": "south"},
    {"name": "Yavne",           "lat": 31.8758, "lng": 34.7395, "region": "center"},
    {"name": "Kiryat Yam",      "lat": 32.8504, "lng": 35.0656, "region": "north"},
    {"name": "Kiryat Ono",      "lat": 32.0545, "lng": 34.8554, "region": "center"},
    {"name": "Umm al-Fahm",     "lat": 32.5164, "lng": 35.1538, "region": "north"},
    {"name": "Tzfat",           "lat": 32.9647, "lng": 35.4961, "region": "north"},
    {"name": "Or Akiva",        "lat": 32.5073, "lng": 34.9166, "region": "sharon"},
    {"name": "Sakhnin",         "lat": 32.8658, "lng": 35.2944, "region": "north"},
    {"name": "Ofakim",          "lat": 31.3175, "lng": 34.6219, "region": "south"},
    {"name": "Migdal HaEmek",   "lat": 32.6739, "lng": 35.2384, "region": "north"},
    {"name": "Beit Shean",      "lat": 32.5000, "lng": 35.5000, "region": "north"},
    {"name": "Tirat Carmel",    "lat": 32.7592, "lng": 34.9730, "region": "north"},
    {"name": "Nof HaGalil",     "lat": 32.7003, "lng": 35.3236, "region": "north"},
]

# Segment-specific Google Places query types
SEGMENT_QUERIES = {
    "retail": [
        "clothing store", "boutique", "sports store", "gift shop",
        "shoe store", "jewelry store", "toy store", "bookstore",
    ],
    "chain": [
        "supermarket chain", "pharmacy chain", "fast food chain",
        "coffee chain", "electronics chain", "fashion chain",
    ],
    "institution": [
        "school", "kindergarten", "non-profit organization",
        "municipal department", "hospital", "community center",
    ],
    "employee_org": [
        "workers committee", "trade union", "employees organization",
        "labor organization", "professional association",
    ],
}

# Sales routing by segment
SEGMENT_ROUTING = {
    "retail":       {"channel": "whatsapp", "angle": "תשלומים קלים לעסק שלך – ללא עמלות מיותרות"},
    "chain":        {"channel": "email",    "angle": "פתרון תשלומים לרשת – מותאם לסניפים מרובים"},
    "institution":  {"channel": "email",    "angle": "מסלול מוסדי – ניהול תשלומים לארגונים ומוסדות"},
    "employee_org": {"channel": "whatsapp", "angle": "הטבות לעובדים – פשוט, דיגיטלי, ומשתלם"},
}

# Territory → agent mapping
TERRITORY_AGENTS = {
    "center":    "agent_center_01",
    "sharon":    "agent_sharon_01",
    "north":     "agent_north_01",
    "south":     "agent_south_01",
    "jerusalem": "agent_jerusalem_01",
}

DB_PATH = "leads.db"
LOG_LEVEL = "INFO"
