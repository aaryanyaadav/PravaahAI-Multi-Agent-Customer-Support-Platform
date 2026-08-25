from pydantic import BaseModel
from typing import Any


class LLMResponse(BaseModel):

    success: bool

    content: str

    raw_response: Any = None
    tokens_used: int = 0