from collections import defaultdict
import random

def analyze_clusters(comments, labels):
    """Aggregate comments into clusters based on labels and extract real quotes."""
    clusters = defaultdict(list)

    for comment, label in zip(comments, labels):
        if label == -1:
            continue  # noise
        clusters[int(label)].append(comment)

    total = len(comments)
    results = []

    for label, texts in clusters.items():
        count = len(texts)
        percentage = round((count / total) * 100, 2)

        # 🔥 Random samples (REAL DATA)
        # Using 5 quotes as requested
        quotes = random.sample(texts, min(5, len(texts)))

        results.append({
            "label": label,
            "count": int(count),
            "percentage": float(percentage),
            "quotes": quotes
        })

    # Sort by market impact
    results.sort(key=lambda x: x["percentage"], reverse=True)

    return results
