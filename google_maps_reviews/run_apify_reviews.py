import json
import os
from pathlib import Path
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =====================
# CONFIG
# =====================
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
ACTOR_ID = "compass/Google-Maps-Reviews-Scraper"

if not APIFY_TOKEN:
    print("Error: APIFY_TOKEN not found in environment variables. Please check your .env file.")
    exit(1)

# Paths
BASE_DIR = Path("/Users/karpinski94/projects/google maps scraper")
INPUT_FILE = BASE_DIR / "50_competitors_analysis.json"
OUTPUT_DIR = BASE_DIR / "apify_results"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================
# INIT CLIENT
# =====================
client = ApifyClient(APIFY_TOKEN)

# =====================
# LOAD JSON
# =====================
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# =====================
# FILTER OBJECTS
# =====================
# Filters where reviewsCount is not null and greater than 5
filtered = [
    item for item in data
    if item.get("reviewsCount") is not None and item.get("reviewsCount", 0) > 5
]

print(f"Found {len(filtered)} valid places")

# =====================
# RUN ACTOR FOR EACH
# =====================
for idx, item in enumerate(filtered):
    place_url = item.get("url")
    name = item.get("title", f"place_{idx}")

    if not place_url:
        continue

    print(f"Running actor for: {name}")

    run_input = {
        "startUrls": [{"url": place_url}],
        "maxReviews": 200,  # you can change this
        "reviewsSort": "newest",
        "language": "en"
    }

    try:
        run = client.actor(ACTOR_ID).call(run_input=run_input)

        dataset_id = run["defaultDatasetId"]

        results = list(client.dataset(dataset_id).iterate_items())

        # Save file
        safe_name = name.replace("/", "_").replace(" ", "_").replace(":", "_").replace("?", "")
        output_file = OUTPUT_DIR / f"{safe_name}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Saved: {output_file}")

    except Exception as e:
        print(f"Error for {name}: {e}")

