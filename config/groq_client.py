import os
from groq import Groq
from config.config import Config


class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL

    def generate_response(self, messages, temperature=0.7, max_tokens=1024):
        """
        Generate response from Groq LLM
        messages: list of dicts [{"role": "user", "content": "..."}]
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Groq API Error: {str(e)}")
            return "⚠️ Error generating response from AI."


# ==========================
# 🔥 SINGLETON INSTANCE
# ==========================
groq_client = GroqClient()