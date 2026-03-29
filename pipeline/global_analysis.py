from pipeline.dataset import load_all_comments
from pipeline.embedder import embed_texts
from pipeline.clustering import cluster_embeddings
from pipeline.analyzer import analyze_clusters
from pipeline.labeler import label_clusters


def run_global_analysis():
    """Execute the full data pipeline: LOAD -> EMBED -> CLUSTER -> ANALYZE -> LABEL."""
    print("\n📊 1. LOADING COMMENTS...")
    texts = load_all_comments()
    total_comments = len(texts)
    print(f"✅ Total comments: {total_comments}")

    if not texts:
        print("❌ No comments found in database!")
        return [], 0

    print("\n🧠 2. EMBEDDING...")
    embeddings = embed_texts(texts)
    print(f"✅ Embeddings generated: {len(embeddings)}")

    print("\n🔗 3. CLUSTERING (HDBSCAN)...")
    labels = cluster_embeddings(embeddings)
    # Filter noise - the analyzer does this too, but for logging:
    num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"✅ Clusters found: {num_clusters}")

    print("\n📈 4. AGGREGATING STATISTICS...")
    clusters = analyze_clusters(texts, labels)
    print(f"✅ Data aggregated into {len(clusters)} valid clusters")

    print("\n🏷️ 5. LABELING CLUSTERS (LLM)...")
    labeled_clusters = label_clusters(clusters)
    print(f"✅ Labels assigned: {len(labeled_clusters)}")

    print("\n🔗 6. MERGING SIMILAR CLUSTERS...")
    from pipeline.cluster_merger import merge_similar_clusters
    merged_clusters = merge_similar_clusters(labeled_clusters)
    print(f"✅ Clusters merged: {len(labeled_clusters)} -> {len(merged_clusters)}")

    print("\n🧠 7. THEMATIC NORMALIZATION (LEVEL 2 INTELLIGENCE)...")
    from pipeline.theme_normalizer import group_normalized
    final_clusters = group_normalized(merged_clusters)
    print(f"✅ Strategic themes consolidated: {len(merged_clusters)} -> {len(final_clusters)}")

    return final_clusters, total_comments
