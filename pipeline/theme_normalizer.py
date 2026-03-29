def normalize_theme(name):
    """
    Categorize fine-grained cluster names into broad, strategic market themes.
    This provides 'Level 2 Intelligence' for a consolidated report.
    """
    n = name.lower()

    # 🔴 PRICE & COST (High Priority)
    if any(x in n for x in ["price", "cost", "usd", "value", "cuanto", "cuánto", "money", "fee", "valer", "precio"]):
        return "Price & Cost"

    # 🔴 INFORMATION REQUESTS
    if any(x in n for x in ["info", "information", "available", "number", "tel", "contacto", "disponible", "details"]):
        return "Information Requests"

    # 🔴 TRUST & SAFETY ISSUES
    if any(x in n for x in ["fraud", "scam", "dishonest", "abuse", "fake", "bad", "dangerous", "unsafe", "careful", "cuidado"]):
        return "Trust & Safety Issues"

    # 🔴 SERVICE QUALITY (NEGATIVE)
    if any(x in n for x in ["bad service", "poor service", "terrible", "rude", "slow", "unresponsive", "negativa"]):
        return "Negative Service Experience"

    # 🟢 SERVICE QUALITY (POSITIVE)
    if any(x in n for x in ["excellent service", "good service", "recommended", "professional", "atencion", "atención", "asesoria", "asesoría"]):
        return "Positive Service Experience"

    # 🟢 DESIGN & AESTHETICS
    if any(x in n for x in ["design", "beautiful", "luxury", "modern", "design", "estile", "precioso", "hermosa"]):
        return "Design & Aesthetics"

    # 🟢 LOCATION
    if any(x in n for x in ["location", "area", "neighborhood", "medellin", "medellín"]):
        return "Location & Area"

    return "Other Market Signals"

def group_normalized(clusters):
    """
    Aggregates fragmented clusters into consolidated strategic themes.
    Normalizes names and sums counts and unique quotes.
    """
    grouped = {}

    for c in clusters:
        theme = normalize_theme(c["name"])

        if theme not in grouped:
            grouped[theme] = {
                "name": theme,
                "count": 0,
                "quotes": []
            }

        grouped[theme]["count"] += c["count"]
        # Limit quotes per final theme to keep it readable
        existing_quotes = grouped[theme]["quotes"]
        new_quotes = c["quotes"]
        
        # Merge and dedup
        combined = list(dict.fromkeys(existing_quotes + new_quotes))
        grouped[theme]["quotes"] = combined[:8] # slightly more for top themes

    # Final sort by total impact
    results = list(grouped.values())
    results.sort(key=lambda x: x["count"], reverse=True)
    
    return results
