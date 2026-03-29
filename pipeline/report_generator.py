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

def generate_structured_report(clusters, total_comments):
    """
    Generate a formatted market analysis report using pure Python logic.
    No LLM used here for synthesis or calculation.
    """
    # 🔥 SORT BY COUNT POST-MERGE
    clusters.sort(key=lambda x: x["count"], reverse=True)

    report = "# 📊 MARKET ANALYSIS REPORT\n\n"
    report += f"**Total Comments Analyzed**: {total_comments}\n\n"
    
    pains = []
    desires = []
    objections = []
    others = []
    
    for c in clusters:
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

    # 📊 MARKET PATTERNS
    if others:
        report += "## 📊 OTHER THEMES\n\n"
        for c in others:
            report += format_cluster(c, total_comments)

    # 📉 SUMMARY
    report += "## 📈 SUMMARY\n\n"
    report += f"Top 3 Dominant Themes:\n"
    for i, c in enumerate(clusters[:3]):
        percentage = round((c["count"] / total_comments) * 100, 1)
        report += f"{i+1}. {c.get('name', 'N/A')} ({percentage}%)\n"
        
    report += f"\nTotal Clusters Identified: {len(clusters)}\n"
    
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
