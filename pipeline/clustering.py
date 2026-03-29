import hdbscan
from .config import MIN_CLUSTER_SIZE


def cluster_embeddings(embeddings):
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=MIN_CLUSTER_SIZE,
        min_samples=1,  # More sensitive to small clusters
        metric="euclidean"
    )

    labels = clusterer.fit_predict(embeddings)

    return labels
