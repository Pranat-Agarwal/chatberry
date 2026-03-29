import requests
from config.config import Config


# ==========================
# 📰 NEWS SERVICE (OPTIONAL)
# ==========================
class NewsService:

    @staticmethod
    def get_top_headlines(country="us", category=None):
        try:
            params = {
                "apiKey": Config.NEWS_API_KEY,
                "country": country,
            }

            if category:
                params["category"] = category

            response = requests.get(
                Config.NEWS_BASE_URL,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                return []

            data = response.json()
            return data.get("articles", [])

        except Exception as e:
            print(f"❌ News API Error: {str(e)}")
            return []

    @staticmethod
    def search_news(query):
        try:
            url = "https://newsapi.org/v2/everything"

            params = {
                "apiKey": Config.NEWS_API_KEY,
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": 5
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()
            return data.get("articles", [])

        except Exception as e:
            print(f"❌ News Search Error: {str(e)}")
            return []

    @staticmethod
    def format_news_for_llm(articles):
        if not articles:
            return ""

        formatted = "Latest News:\n\n"

        for i, article in enumerate(articles[:5], 1):
            formatted += f"{i}. {article.get('title')}\n"
            formatted += f"{article.get('description')}\n\n"

        return formatted.strip()


# ==========================
# 🔎 TAVILY SEARCH (MAIN)
# ==========================
def tavily_search(query):
    """
    Raw Tavily API call
    """
    try:
        url = "https://api.tavily.com/search"

        payload = {
            "api_key": Config.TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": 5
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code != 200:
            print("❌ Tavily API Error:", response.text)
            return []

        data = response.json()

        # Tavily returns { results: [...] }
        return data.get("results", [])

    except Exception as e:
        print("❌ Tavily Error:", str(e))
        return []


# ==========================
# 🔒 SAFE WRAPPER (IMPORTANT)
# ==========================
def tavily_search_safe(query):
    try:
        results = tavily_search(query)

        if not results:
            return []

        # normalize structure
        cleaned = []

        for r in results:
            cleaned.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")
            })

        return cleaned

    except Exception as e:
        print("❌ Tavily Safe Error:", e)
        return []