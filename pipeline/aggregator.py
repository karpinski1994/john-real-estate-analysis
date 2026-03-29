from collections import defaultdict
import random

def merge_clusters(youtube_clusters, google_positive, google_negative):
    """Combine clusters from all sources into a single flat list with source tags."""
    merged = []

    # YouTube → neutral / intent / top funnel
    for c in youtube_clusters:
        c["source"] = "youtube"
        merged.append(c)

    # Google negative → pains
    for c in google_negative:
        c["source"] = "google_negative"
        merged.append(c)

    # Google positive → desires
    for c in google_positive:
        c["source"] = "google_positive"
        merged.append(c)

    return merged


def group_by_theme(clusters):
    """Group clusters by their AI-generated names and aggregate quotes across sources."""
    grouped = defaultdict(list)

    for c in clusters:
        # Use the AI-generated label name
        name = c.get("name", "Unknown Topic").strip()
        grouped[name].append(c)

    results = []

    for name, items in grouped.items():
        total_percentage = sum(i["percentage"] for i in items)
        total_count = sum(i["count"] for i in items)
        sources = sorted(list(set(i["source"] for i in items)))

        # Aggregate all quotes from all items in this theme
        all_quotes = []
        for i in items:
            all_quotes.extend(i.get("quotes", []))
            
        # Sample representative quotes across all sources
        sampled_quotes = random.sample(all_quotes, min(5, len(all_quotes)))

        results.append({
            "name": name,
            "percentage": round(total_percentage, 2),
            "count": total_count,
            "sources": sources,
            "quotes": sampled_quotes
        })

    # Sort by total impact
    results.sort(key=lambda x: x["percentage"], reverse=True)

    return results
