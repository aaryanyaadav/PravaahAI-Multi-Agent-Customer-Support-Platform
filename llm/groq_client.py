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
            
        self.api_key = api_key or "placeholder_key"
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception:
            self.client = None
        model = os.getenv("DEFAULT_MODEL") or getattr(settings, "DEFAULT_MODEL", None) or "llama-3.3-70b-versatile"
        if "openai" in model or "gpt-oss" in model:
            model = "llama-3.3-70b-versatile"
        self.default_model = model

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
