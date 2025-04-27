from pydantic import BaseModel


class TTSText(BaseModel):
    text: str
