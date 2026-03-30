NEC_KEYWORDS = [
    "nec",
    "grounding",
    "voltage",
    "conductor",
    "ampacity",
    "circuit",
    "breaker",
    "panel",
    "wiring",
    "electrical"
]

WATTMONK_KEYWORDS = [
    "wattmonk",
    "solar",
    "permit",
    "engineering",
    "pv",
    "inspection",
    "roof",
    "installation"
]


def classify_query(query):

    q = query.lower()

    if any(word in q for word in NEC_KEYWORDS):
        return "nec"

    if any(word in q for word in WATTMONK_KEYWORDS):
        return "wattmonk"

    return "general"
