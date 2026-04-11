import os
import requests
from config.config import Config


class TavilyClient:
    def __init__(self):
        # 🔁 Just change ENV key name
        self.api_key = os.getenv("TAVILY_API_KEY")

        self.base_url = "https://api.tavily.com/search"

        if not self.api_key:
            print("❌ ERROR: TAVILY_API_KEY not found in environment")

    def search(self, query, max_results=3):

        print("🚨 SEARCH FUNCTION HIT (TAVILY)")

        try:
            # ==========================
            # 🔑 API KEY
            # ==========================
            api_key = os.getenv("TAVILY_API_KEY")

            if not api_key:
                print("❌ ERROR: TAVILY_API_KEY missing")
                return {"error": "Missing API key"}

            # ==========================
            # 📦 PAYLOAD (TAVILY FORMAT)
            # ==========================
            payload = {
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results
            }

            print("🔥 TAVILY API CALLED:", query)

            # ==========================
            # 🌐 API CALL
            # ==========================
            response = requests.post(
                self.base_url,
                json=payload,
                timeout=3
            )

            # ==========================
            # ❌ ERROR HANDLING
            # ==========================
            if response.status_code != 200:
                print("❌ STATUS CODE:", response.status_code)
                print("❌ RESPONSE:", response.text)
                return {"error": "Tavily API failed"}

            data = response.json()

            # ==========================
            # 📦 RESULT PARSING (KEEP SAME FORMAT)
            # ==========================
            tavily_results = data.get("results", [])

            if not tavily_results:
                print("⚠️ No Tavily results found")
                return {"results": []}

            results = []
            for r in tavily_results[:max_results]:
                results.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", "")
                })

            print(f"✅ TAVILY RESULTS FOUND: {len(results)}")

            return {
                "results": results
            }

        except requests.exceptions.Timeout:
            print("⏱️ TAVILY TIMEOUT")
            return {"error": "Timeout"}

        except Exception as e:
            print("❌ Tavily Error:", e)
            return {"error": "Search failed"}

    def format_results_for_llm(self, search_data):
        """
        SAME FUNCTION — NO CHANGE NEEDED
        """

        if "error" in search_data:
            return ""

        context = ""

        for i, result in enumerate(search_data.get("results", []), 1):
            context += f"{i}. {result.get('title')}\n"
            context += f"{result.get('content')}\n\n"

        return context.strip()


# ==========================
# 🔥 SINGLETON INSTANCE
# ==========================
tavily_client = TavilyClient()