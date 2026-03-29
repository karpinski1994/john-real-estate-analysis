def merge_similar_clusters(clusters):
    """
    Merge clusters with strongly similar labels to prevent fragmentation.
    For example, 'High Prices' and 'Expensive' are combined into one.
    """
    merged = {}

    for c in clusters:
        name = c["name"].lower()
        key = None

        # 🔥 HEURISTIC MERGING RULES
        if any(x in name for x in ["price", "expensive", "cost", "value"]):
            key = "High Prices"
        elif "pool" in name:
            key = "No Pool"
        elif "kitchen" in name or "cooking" in name:
            key = "Kitchen Issues"
        elif any(x in name for x in ["security", "safe", "dangerous"]):
            key = "Safety Concerns"
        elif any(x in name for x in ["design", "modern", "beautiful", "look"]):
            key = "Luxury Design"
        elif any(x in name for x in ["response", "communication", "reply", "whatsapp"]):
            key = "Poor Communication"
        elif any(x in name for x in ["location", "area", "neighborhood"]):
            key = "Location Feedback"
        else:
            # Group clusters with the exact same name together
            key = c["name"]

        if key not in merged:
            merged[key] = {
                "name": key,
                "count": 0,
                "quotes": []
            }

        merged[key]["count"] += c["count"]
        # Extend quotes and dedup them at the same time
        merged[key]["quotes"].extend(c["quotes"])

    # Clean up results
    results = []
    for m in merged.values():
        # Deduplicate quotes and keep max 5
        m["quotes"] = list(dict.fromkeys(m["quotes"]))[:5]
        results.append(m)

    return results
