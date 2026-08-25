import os
from dotenv import load_dotenv
load_dotenv()
class settings:
    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY"
    )
    DEFAULT_MODEL = os.getenv(
        "DEFAULT_MODEL",
        "openai/gpt-oss-120b"
    )
    TEMPERATURE = 0
settings = settings()

