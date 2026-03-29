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

def generate_source_section(source_name, title, clusters, noise_data, total_comments):
    """Generates a markdown section for a specific source."""
    if total_comments == 0:
        return f"# {title}\n\nNo data found for this source.\n\n"

    # 🔥 CATEGORIZE INTO MAIN VS LONG TAIL
    main_themes = [c for c in clusters if (c["count"] / total_comments) >= 0.01]
    long_tail = [c for c in clusters if (c["count"] / total_comments) < 0.01]

    section = f"# {title}\n\n"
    section += f"**Total Comments Analyzed**: {total_comments}\n\n"

    pains = []
    desires = []
    others = []
    
    for c in main_themes:
        category = classify_cluster(c.get("name", ""))
        if category == "pain":
            pains.append(c)
        elif category == "desire":
            desires.append(c)
        else:
            others.append(c)

    # 🔴 PAINS / NEGATIVE
    if pains:
        section += "## 🔴 CRITICAL PAINS & NEGATIVES\n\n"
        for c in pains:
            section += format_cluster(c, total_comments)

    # 🟢 DESIRES / POSITIVE
    if desires:
        section += "## 🟢 CORE DESIRES & POSITIVE FEEDBACK\n\n"
        for c in desires:
            section += format_cluster(c, total_comments)

    # 📊 SECONDARY
    if others:
        section += "## 📊 SECONDARY PATTERNS\n\n"
        for c in others:
            section += format_cluster(c, total_comments)

    # 🟡 LONG TAIL
    if long_tail:
        section += "## 🟡 LONG TAIL THEMES (Niche Signals < 1%)\n\n"
        total_lt = sum(c["count"] for c in long_tail)
        section += f"Minor topics together accounting for ({round(total_lt/total_comments*100, 1)}% of data).\n\n"
        for c in long_tail:
            section += f"- **{c['name']}**: {c['count']} mentions\n"
        section += "\n---\n\n"

    # ⚪ NOISE
    section += "## ⚪ UNCLASSIFIED (NOISE)\n\n"
    section += f"Total Noise Points: {noise_data['count']} ({noise_data['percentage']}%)\n"
    section += "Examples:\n"
    for ex in noise_data['examples'][:5]:
        section += f"- \"{ex.strip()}\"\n"
    section += "\n---\n\n"
    
    return section

def generate_multi_source_report(source_results):
    """
    Generates a consolidated market report with split perspectives.
    source_results = {
        'youtube': {'clusters': ..., 'noise_data': ..., 'total_comments': ...},
        'google': {'clusters': ..., 'noise_data': ..., 'total_comments': ...}
    }
    """
    report = "# 📊 INTEGRATED MARKET ANALYSIS\n\n"
    report += "---\n\n"

    if 'youtube' in source_results:
        res = source_results['youtube']
        report += generate_source_section("youtube", "🎥 YOUTUBE INSIGHTS (Perception & Sentiment)", 
                                         res['clusters'], res['noise_data'], res['total_comments'])
        report += "---\n\n"

    if 'google' in source_results:
        res = source_results['google']
        report += generate_source_section("google", "📍 GOOGLE REVIEWS INSIGHTS (Customer Experience)", 
                                         res['clusters'], res['noise_data'], res['total_comments'])
        report += "---\n\n"

    # 📉 CONSOLIDATED COVERAGE
    report += "## 📉 FINAL DATA COVERAGE AUDIT\n\n"
    report += "| Source | Clustered % | Noise % | Total |\n"
    report += "|--------|-------------|---------|-------|\n"
    
    for src, res in source_results.items():
        if res['total_comments'] > 0:
            clustered_pct = round(sum(c['count'] for c in res['clusters']) / res['total_comments'] * 100, 1)
            noise_pct = res['noise_data']['percentage']
            report += f"| {src.capitalize()} | {clustered_pct}% | {noise_pct}% | {res['total_comments']} |\n"
    
    report += "\n"
    return report

def generate_structured_report(clusters, noise_data, total_comments):
    """Legacy single-source fallback."""
    return generate_source_section("global", "MARKET ANALYSIS REPORT", clusters, noise_data, total_comments)

def format_cluster(c, total_comments):
    percentage = round((c["count"] / total_comments) * 100, 1)
    name = c.get("name", "Unknown Cluster")
    
    block = f"### {name} ({percentage}% [{c['count']}/{total_comments}])\n"
    for quote in c["quotes"]:
        clean_quote = quote.replace("\n", " ").strip()
        block += f"- \"{clean_quote}\"\n"
    block += "\n---\n\n"
    return block
