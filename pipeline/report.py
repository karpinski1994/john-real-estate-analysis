def generate_report(cluster_data):
    """Generate a combined VoC report featuring the 'Real Voice' with actual user quotes."""
    lines = ["# 🎤 Voice of Customer (Combined Market Report)\n"]
    lines.append(f"This report highlights the **Real Market Themes** based on actual user comments and reviews.\n")

    lines.append("## 🔥 Top Market Themes & Representative Quotes\n")

    for c in cluster_data[:15]:
        name = c.get('name', 'General Topic')
        lines.append(f"### {name} — {c['percentage']}% ({c['count']} mentions)")
        
        # Sources formatting
        sources = ", ".join([s.replace("_", " ").title() for s in c.get('sources', [])])
        if sources:
            lines.append(f"*Sources: {sources}*")
            
        lines.append("\n**Real user quotes:**")
        for q in c["quotes"]:
            lines.append(f'- "{q}"')
        
        lines.append("\n---")

    lines.append("\n### 🧠 Market Insights Interpretation\n")
    
    # Simple logic-based insights
    top_theme = cluster_data[0]['theme'] if 'theme' in cluster_data[0] else cluster_data[0].get('name', 'N/A')
    lines.append(f"1. **Most Dominant Theme**: The market is primarily talking about **{top_theme}**. This should be the core focus of your marketing messaging.\n")
    
    cross_source = [item for item in cluster_data if len(item.get('sources', [])) > 1]
    if cross_source:
        lines.append(f"2. **Cross-Platform Consistency**: Themes like **{', '.join([c.get('name', '') for c in cross_source[:2]])}** are appearing everywhere. These are universal consumer non-negotiables.\n")
    
    lines.append("3. **Messaging Recommendation**: Audit your current copy against the top 3 themes above to ensure you are answering the most frequent objections and desires.\n")

    return "\n".join(lines)
