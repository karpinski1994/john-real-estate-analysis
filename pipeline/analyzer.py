from collections import defaultdict
import random

def short_text_bucket(text):
    """
    HEURISTIC: Catch high-value short repetitive texts that 
    HDBSCAN might miss due to low density.
    """
    t = text.lower().strip()
    
    # 🔴 Common positive triggers
    if t in ["hermoso", "hermosa", "muy bonito", "beautiful", "guau", "perfecto", "wow"]:
        return "Positive Emotion"
    
    if any(x in t for x in ["excelente servicio", "muy amable", "buen servicio", "la mejor"]):
        return "Excellent Service Label"

    if any(x in t for x in ["precio", "cuanto vale", "cuánto vale", "how much", "price"]):
        return "Inquiry (Price)"
        
    return None

def analyze_clusters(comments, labels):
    """
    Aggregate all comments into clusters or noise buckets.
    Ensures 100% data coverage.
    """
    clusters = defaultdict(list)
    noise_comments = []

    # 🎯 STEP 1: RULE-BASED CATCHER
    for i, (comment, label) in enumerate(zip(comments, labels)):
        bucket = short_text_bucket(comment)
        if bucket:
            clusters[bucket].append(comment)
        elif label == -1:
            noise_comments.append(comment)
        else:
            clusters[int(label)].append(comment)

    total = len(comments)
    results = []

    for label, texts in clusters.items():
        count = len(texts)
        if count == 0: continue
        
        # Keep ALL clusters
        # For rule-based ones, keep the bucket name
        results.append({
            "name": str(label) if isinstance(label, str) else None,
            "label": label if isinstance(label, (int, float)) else -2, # fallback
            "count": int(count),
            "percentage": round((count / total) * 100, 2),
            "quotes": random.sample(texts, min(5, len(texts)))
        })

    # Sort results by count
    results.sort(key=lambda x: x["count"], reverse=True)

    # ⚪ NOISE
    noise_data = {
        "count": len(noise_comments),
        "percentage": round((len(noise_comments) / total) * 100, 2),
        "examples": random.sample(noise_comments, min(10, len(noise_comments))) if noise_comments else []
    }

    return results, noise_data
