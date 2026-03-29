from pipeline.embedder import embed_texts
from pipeline.clustering import cluster_embeddings
from pipeline.analyzer import analyze_clusters
from pipeline.llm import build_prompt, call_llm


texts = [
    "this apartment is too expensive",
    "price is very high",
    "amazing location",
    "beautiful apartment",
    "bad service",
    "terrible experience"
]


print("Step 1: Embedding...")
embeddings = embed_texts(texts)

print("Step 2: Clustering...")
labels = cluster_embeddings(embeddings)

print("Labels:", labels)

print("Step 3: Analyze...")
clusters = analyze_clusters(texts, labels)

print("Clusters:", clusters)

print("Step 4: LLM...")
prompt = build_prompt(clusters)
analysis = call_llm(prompt)

print("\n=== FINAL ANALYSIS ===\n")
print(analysis)
