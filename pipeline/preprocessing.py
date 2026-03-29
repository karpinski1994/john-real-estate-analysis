import re

def clean_text(text: str) -> str:
    """Clean text by removing emojis, dates, and very short samples."""
    if not text:
        return ""
        
    text = text.lower().strip()

    # 1. Remove emojis/special characters (keep mostly letters and numbers in Spanish/English)
    # Using [^\w\s] is a bit aggressive, maybe keep basic punctuation?
    # But user wants re.sub(r'[^\w\s]', '', text) to kill emojis.
    text = re.sub(r'[^\w\s]', '', text)

    # 2. Remove purely dates (e.g., '18 noviembre 2025')
    # User's regex: r'^\d+\s+\w+\s+\d+$'
    if re.match(r'^\d+\s+\w+\s+\d+$', text):
        return ""

    # 3. Remove purely numeric strings
    if text.isdigit():
        return ""

    # 4. Filter by length
    if len(text) < 5:
        return ""

    return text
