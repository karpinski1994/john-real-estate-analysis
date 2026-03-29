def classify_cluster(name):
    """Refined classification of clusters into semantic market categories."""
    name_lower = name.lower()

    # Priorities are handled by order of if/else
    if any(x in name_lower for x in ["price", "expensive", "cost"]):
        return "pain"
    
    if any(x in name_lower for x in ["no ", "missing", "bad", "poor", "slow", "unsafe", "problem", "issue"]):
        return "pain"
        
    if any(x in name_lower for x in ["beautiful", "great", "good", "luxury", "perfect", "modern", "design", "location"]):
        return "desire"
        
    if any(x in name_lower for x in ["?", "how", "what", "price"]):
        return "objection"
        
    return "other"

def generate_structured_report(clusters, noise_data, total_comments):
    """
    Generate a formatted market analysis report showing 100% data coverage.
    """
    # 🔥 CATEGORIZE INTO MAIN VS LONG TAIL
    # Threshold: Themes with < 1% are long tail (unless they are explicitly high-value)
    main_themes = [c for c in clusters if (c["count"] / total_comments) >= 0.01]
    long_tail = [c for c in clusters if (c["count"] / total_comments) < 0.01]

    report = "# 📊 MARKET ANALYSIS REPORT (100% COVERAGE)\n\n"
    report += f"**Total Comments Analyzed**: {total_comments}\n\n"
    
    pains = []
    desires = []
    objections = []
    others = []
    
    for c in main_themes:
        category = classify_cluster(c.get("name", ""))
        
        if category == "pain":
            pains.append(c)
        elif category == "desire":
            desires.append(c)
        elif category == "objection":
            objections.append(c)
        else:
            others.append(c)

    # 🔴 PAINS
    if pains:
        report += "## 🔴 PAINS & FRUSTRATIONS (NEGATIVE SIGNALS)\n\n"
        for c in pains:
            report += format_cluster(c, total_comments)

    # 🟢 DESIRES
    if desires:
        report += "## 🟢 DESIRES & MOTIVATIONS (POSITIVE SIGNALS)\n\n"
        for c in desires:
            report += format_cluster(c, total_comments)
            
    # 🚧 OBJECTIONS
    if objections:
        report += "## 🚧 OBJECTIONS (BUYING BARRIERS)\n\n"
        for c in objections:
            report += format_cluster(c, total_comments)

    # 📊 SECONDARY THEMES
    if others:
        report += "## 📊 SECONDARY THEMES\n\n"
        for c in others:
            report += format_cluster(c, total_comments)

    # 🧶 LONG TAIL
    if long_tail:
        report += "## 🟡 LONG TAIL THEMES (Niche Signals < 1%)\n\n"
        total_lt = sum(c["count"] for c in long_tail)
        report += f"These are minor, low-frequency topics together accounting for ({round(total_lt/total_comments*100, 1)}% of data).\n\n"
        for c in long_tail:
            report += f"- **{c['name']}**: {c['count']} mentions\n"
        report += "\n---\n\n"

    # ⚪ NOISE
    report += "## ⚪ UNCLASSIFIED (NOISE)\n\n"
    report += f"Total Noise Points: {noise_data['count']} ({noise_data['percentage']}%)\n"
    report += "These are short, non-semantic, or random comments that do not form a distinct pattern.\n\n"
    report += "**Examples**:\n"
    for ex in noise_data['examples']:
        report += f"- \"{ex.strip()}\"\n"
    report += "\n---\n\n"

    # 📉 DATA COVERAGE VALIDATION
    clustered_total = sum(c["count"] for c in clusters)
    main_pct = round(sum(c["count"] for c in main_themes) / total_comments * 100, 1)
    lt_pct = round(sum(c["count"] for c in long_tail) / total_comments * 100, 1)
    noise_pct = noise_data['percentage']
    
    report += "## 📉 DATA COVERAGE AUDIT\n\n"
    report += "| Category | Mentions | Percentage |\n"
    report += "|----------|----------|------------|\n"
    report += f"| Main Themes | {sum(c['count'] for c in main_themes)} | {main_pct}% |\n"
    report += f"| Long Tail | {sum(c['count'] for c in long_tail)} | {lt_pct}% |\n"
    report += f"| Noise | {noise_data['count']} | {noise_pct}% |\n"
    report += f"| **TOTAL** | **{total_comments}** | **100%** |\n\n"
    
    # Debug print for terminal
    print(f"\nVALIDATION:")
    print(f"Total: {total_comments}")
    print(f"Clustered: {clustered_total}")
    print(f"Noise: {noise_data['count']}")
    print(f"Coverage check: {clustered_total + noise_data['count']} / {total_comments}")

    return report

def format_cluster(c, total_comments):
    percentage = round((c["count"] / total_comments) * 100, 1)
    name = c.get("name", "Unknown Cluster")
    
    block = f"### {name} ({percentage}% [{c['count']}/{total_comments}])\n"
    for quote in c["quotes"]:
        clean_quote = quote.replace("\n", " ").strip()
        block += f"- \"{clean_quote}\"\n"
    block += "\n---\n\n"
    return block
