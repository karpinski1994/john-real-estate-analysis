import json
from pathlib import Path

INPUT_DIR = Path("/Users/karpinski94/projects/google maps scraper/apify_results")
OUTPUT_FILE = Path("/Users/karpinski94/projects/google maps scraper/all_reviews.json")

merged = []

for json_file in sorted(INPUT_DIR.glob("*.json")):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        merged.extend(data)
    else:
        merged.append(data)
    print(f"  {json_file.name}: {len(data) if isinstance(data, list) else 1} records")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"\nDone! Total records: {len(merged)}")
print(f"Saved to: {OUTPUT_FILE}")
