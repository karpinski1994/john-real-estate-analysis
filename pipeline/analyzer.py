from collections import defaultdict
import random

def analyze_clusters(comments, labels):
    """
    Aggregate all comments into clusters or noise buckets.
    Ensures 100% data coverage.
    """
    clusters = defaultdict(list)
    noise_comments = []

    for comment, label in zip(comments, labels):
        if label == -1:
            noise_comments.append(comment)
        else:
            clusters[int(label)].append(comment)

    total = len(comments)
    results = []

    for label, texts in clusters.items():
        count = len(texts)
        percentage = round((count / total) * 100, 2)
        
        # Keep ALL clusters for now (small ones will be handled later)
        quotes = random.sample(texts, min(5, len(texts)))

        results.append({
            "label": label,
            "count": int(count),
            "percentage": float(percentage),
            "quotes": quotes
        })

    # Sort results by count
    results.sort(key=lambda x: x["count"], reverse=True)

    # Calculate noise stats separately
    noise_data = {
        "count": len(noise_comments),
        "percentage": round((len(noise_comments) / total) * 100, 2),
        "examples": random.sample(noise_comments, min(10, len(noise_comments))) if noise_comments else []
    }

    return results, noise_data
