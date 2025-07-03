from pydantic import BaseModel


class TTSRequest(BaseModel):
    text: str
    emotion: str = "neutral"
    instruct: str = ""
    speed: float = 1.0
