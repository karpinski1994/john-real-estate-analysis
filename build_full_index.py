import json
from pathlib import Path
from youtube_comments.analyze_comments import extract_youtube_texts
from pipeline.build_index import build_index
from pipeline.preprocessing import clean_text

def build_market_index():
    print("🚀 Initializing Full Market Index Build (YouTube + Google)...")
    
    all_texts = []
    
    # 1. YouTube
    YT_FILE = "youtube_comments/apartamentos-en-venta-medellin.json"
    if Path(YT_FILE).exists():
        with open(YT_FILE, encoding="utf-8") as f:
            yt_data = json.load(f)
        yt_texts = extract_youtube_texts(yt_data)
        all_texts.extend(yt_texts)
        print(f"✅ Loaded {len(yt_texts)} YouTube comments.")

    # 2. Google
    GOOGLE_FILE = "google_maps_reviews/all_reviews.json"
    if Path(GOOGLE_FILE).exists():
        with open(GOOGLE_FILE, encoding="utf-8") as f:
            google_data = json.load(f)
        
        google_texts = []
        for r in google_data:
            text = (r.get("text") or r.get("textTranslated") or "").strip()
            clean = clean_text(text)
            if clean:
                google_texts.append(clean)
        
        all_texts.extend(google_texts)
        print(f"✅ Loaded {len(google_texts)} Google reviews.")

    # BUILD
    if all_texts:
        print(f"\n⚡ Processing {len(all_texts)} total data points. This may take a few minutes...")
        build_index(all_texts)
        print(f"\n🏁 Finished! Index ready at faiss.index")
    else:
        print("❌ No data found to index.")

if __name__ == "__main__":
    build_market_index()
