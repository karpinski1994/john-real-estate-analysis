from pipeline.search import search_similar

def main():
    print("🔍 Testing semantic search with query: 'expensive apartment'")
    try:
        results = search_similar("expensive apartment", k=5)
        
        print("\n🔍 RESULTS:\n")
        if not results:
            print("No results found. Did you build the index yet?")
        else:
            for r in results:
                print("-", r)
    except Exception as e:
        print(f"❌ Search failed: {e}")

if __name__ == "__main__":
    main()
