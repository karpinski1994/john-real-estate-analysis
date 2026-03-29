import hdbscan
from .config import MIN_CLUSTER_SIZE


def cluster_embeddings(embeddings):
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=4,  # Enough for a small meaningful group
        min_samples=1, 
        cluster_selection_epsilon=0.08, # 🔥 Break up giant blobs
        metric="euclidean",
        cluster_selection_method='leaf' # 🎯 Focus on smaller, more granular clusters
    )

    labels = clusterer.fit_predict(embeddings)

    return labels
