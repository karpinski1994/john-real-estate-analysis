from pipeline.dataset import load_comments_by_source
from pipeline.embedder import embed_texts
from pipeline.clustering import cluster_embeddings
from pipeline.analyzer import analyze_clusters
from pipeline.labeler import label_clusters

def run_analysis_for_source(source: str):
    """
    Run the full data analysis pipeline for a specific data source.
    Ensures 100% data coverage for that source.
    """
    print(f"\n🚀 STARTING ANALYSIS FOR SOURCE: {source.upper()}")
    
    # 🔗 1. LOADING
    texts = load_comments_by_source(source)
    total_comments = len(texts)
    
    if not texts:
        print(f"⚠️ No comments found for source: {source}")
        return None, None, 0

    print(f"📊 1. LOADING... ({total_comments} comments)")

    # 🧠 2. EMBEDDING
    print("🧠 2. EMBEDDING...")
    embeddings = embed_texts(texts)

    # 🔗 3. CLUSTERING
    print("🔗 3. CLUSTERING...")
    labels = cluster_embeddings(embeddings)
    num_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    # 📈 4. AGGREGATING
    print("📈 4. AGGREGATING...")
    clusters, noise_data = analyze_clusters(texts, labels)

    # 🏷️ 5. LABELING
    print("🏷️ 5. LABELING...")
    labeled_clusters = label_clusters(clusters)

    # 🔗 6. MERGING
    print("🔗 6. MERGING...")
    from pipeline.cluster_merger import merge_similar_clusters
    merged_clusters = merge_similar_clusters(labeled_clusters)

    # 🧠 7. THEMATIC NORMALIZATION
    print("🧠 7. THEMATIC NORMALIZATION...")
    from pipeline.theme_normalizer import group_normalized
    final_clusters = group_normalized(merged_clusters)

    return final_clusters, noise_data, total_comments

def run_global_analysis():
    """Legacy entry point fallback."""
    # This now just runs a combined run or we avoid it
    from pipeline.dataset import load_all_comments
    texts = load_all_comments()
    # ... (similar steps as above)
    # But for this task, we better skip this or implement it using the source-specific ones.
    pass
