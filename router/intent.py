def classify_query(query):
    q = query.lower()

    if "wattmonk" in q:
        return "wattmonk"
    elif any(word in q for word in ["nec", "voltage", "grounding", "circuit"]):
        return "nec"
    else:
        return "general"