import re


# ==========================
# 🧠 DETECT QUERY TYPE
# ==========================
def detect_query_type(text):
    """
    Detect if user input is:
    - word
    - line
    - paragraph
    """

    if not text:
        return "line"

    text = text.strip()

    # Word → single word
    if len(text.split()) == 1:
        return "word"

    # Paragraph → long input
    if len(text.split()) > 20:
        return "paragraph"

    # Default → line
    return "line"


# ==========================
# 🧠 CLEAN INPUT TEXT
# ==========================
def clean_text(text):
    """
    Basic text cleaning before sending to AI
    """

    text = text.strip()

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


# ==========================
# 🧠 ENHANCE QUERY
# ==========================
def enhance_query(text, query_type):
    """
    Modify query before sending to AI
    """

    if query_type == "word":
        return f"Explain briefly: {text}"

    elif query_type == "line":
        return f"Explain clearly: {text}"

    else:
        return f"Explain in detail with examples: {text}"


# ==========================
# 🧠 DETECT IF QUESTION
# ==========================
def is_question(text):
    """
    Check if input is a question
    """

    question_words = [
        "what", "why", "how", "when", "where",
        "who", "which", "can", "is", "are", "do"
    ]

    text_lower = text.lower()

    return any(text_lower.startswith(word) for word in question_words)


# ==========================
# 🧠 KEYWORD EXTRACTION (BASIC)
# ==========================
def extract_keywords(text):
    """
    Extract important keywords (basic version)
    """

    words = text.lower().split()

    stopwords = {
        "the", "is", "in", "at", "on", "and",
        "a", "to", "of", "for", "with"
    }

    keywords = [word for word in words if word not in stopwords]

    return keywords[:5]  # limit