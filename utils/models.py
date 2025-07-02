from pydantic import BaseModel


class TTSRequest(BaseModel):
    text: str
    emotion: str = "neutral"
    speed: float = 1.0
