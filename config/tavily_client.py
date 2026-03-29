import os
import requests
from config.config import Config


class TavilyClient:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"

    def search(self, query, max_results=5):
        """
        Perform real-time search using Tavily
        """

        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": max_results,
                "include_answer": True
            }

            response = requests.post(self.base_url, json=payload, timeout=10)

            if response.status_code != 200:
                return {
                    "error": f"API Error {response.status_code}"
                }

            data = response.json()

            return {
                "answer": data.get("answer"),
                "results": data.get("results", [])
            }

        except Exception as e:
            print(f"❌ Tavily API Error: {str(e)}")
            return {
                "error": "Failed to fetch search results"
            }

    def format_results_for_llm(self, search_data):
        """
        Convert Tavily results into LLM-friendly context
        """

        if "error" in search_data:
            return ""

        context = ""

        if search_data.get("answer"):
            context += f"Latest Answer: {search_data['answer']}\n\n"

        for i, result in enumerate(search_data.get("results", []), 1):
            context += f"{i}. {result.get('title')}\n"
            context += f"{result.get('content')}\n\n"

        return context.strip()


# ==========================
# 🔥 SINGLETON INSTANCE
# ==========================
tavily_client = TavilyClient()