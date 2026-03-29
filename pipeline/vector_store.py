import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.id_map = []  # map FAISS index → comment_id

    def add(self, embeddings, ids):
        self.index.add(np.array(embeddings).astype("float32"))
        self.id_map.extend(ids)

    def search(self, query_embedding, k=10):
        D, I = self.index.search(
            np.array([query_embedding]).astype("float32"), k
        )

        results = []
        for idx in I[0]:
            if idx < len(self.id_map):
                results.append(self.id_map[idx])

        return results

    def save(self, path="faiss.index"):
        faiss.write_index(self.index, path)
        import json
        with open(f"{path}.id_map", "w") as f:
            json.dump(self.id_map, f)

    def load(self, path="faiss.index"):
        self.index = faiss.read_index(path)
        import json
        with open(f"{path}.id_map", "r") as f:
            self.id_map = json.load(f)
