import re
import time

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
    "the","is","in","at","on","and","a","to","of","for","with",
    "what","tell","me","about","give","show","explain",
    "please","can","you"
}

    keywords = [word for word in words if word not in stopwords]

    return keywords[:5]  # limit

# ==========================
# 🧠 CONTEXT MANAGER
# ==========================
class ContextManager:
    def __init__(self):
        self.last_topic = None
        self.last_updated = 0

    def update(self, keywords):
        if keywords:
            self.last_topic = keywords[0]
            self.last_updated = time.time()

    def get(self):
        if time.time() - self.last_updated < 60:  # 60 sec memory
            return self.last_topic
        return None


context_manager = ContextManager()

def enhance_query_with_context(query):
    keywords = extract_keywords(query)
    context = context_manager.get()

    # short query → use previous topic
    if len(keywords) <= 2 and context:
        enhanced = context + " " + query
        print("🧠 CONTEXT APPLIED:", enhanced)
        return enhanced

    # update topic
    if keywords:
        context_manager.update(keywords)

    return query