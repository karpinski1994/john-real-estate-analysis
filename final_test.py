from pipeline.query_engine import ask_market

def main():
    print("🚀 Running Final Integraton Test: Deep Psychological Analysis")
    
    # Complex query that requires hybrid/rerank + context
    question = "Why are people skeptical or afraid of buying real estate here? What are the specific trust issues?"
    
    answer = ask_market(question)
    
    print("\n" + "="*40)
    print("🧠 MARKET BRAIN RESPONSE")
    print("="*40 + "\n")
    print(answer)
    print("\n" + "="*40)

if __name__ == "__main__":
    main()
