import hdbscan
from .config import MIN_CLUSTER_SIZE


def cluster_embeddings(embeddings):
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,  # Captures small specific groups
        min_samples=1, 
        cluster_selection_epsilon=0.8, # 🔥 MUCH higher to grab more points
        metric="euclidean",
        cluster_selection_method='leaf' 
    )

    labels = clusterer.fit_predict(embeddings)

    return labels
