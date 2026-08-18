import os
from groq import Groq
from llm.models import LLMResponse
from config.settings import settings

class GroqClient:
    def __init__(self):
        # Load API key from settings or environment variables
        api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if not api_key:
            # Fallback: force load env file
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GROQ_API_KEY")
            
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
            
        self.client = Groq(api_key=api_key)
        self.default_model = settings.DEFAULT_MODEL or "llama-3.1-8b-instant"

    def invoke(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        try:
            completion = self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.TEMPERATURE if hasattr(settings, "TEMPERATURE") else 0.0,
            )
            
            content = completion.choices[0].message.content
            tokens = 0
            if completion.usage:
                tokens = completion.usage.total_tokens
                
            return LLMResponse(
                success=True,
                content=content,
                raw_response=completion,
                tokens_used=tokens
            )
        except Exception as e:
            print(f"Groq API client error: {e}")
            return LLMResponse(
                success=False,
                content=str(e),
                raw_response=None,
                tokens_used=0
            )
