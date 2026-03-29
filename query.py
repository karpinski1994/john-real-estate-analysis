import sys
from pipeline.query_engine import ask_market

def main():
    if len(sys.argv) < 2:
        print("❌ Provide a market question (e.g. python query.py 'why people complain about price')")
        return

    question = " ".join(sys.argv[1:])

    print(f"\n🔍 Searching for market evidence: '{question}'...\n")

    result = ask_market(question)

    print("\n" + "="*40)
    print("🧠 MARKET BRAIN ANSWER")
    print("="*40 + "\n")
    print(result)
    print("\n" + "="*40)


if __name__ == "__main__":
    main()
