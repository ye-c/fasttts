from .base import BaseTTS
from .mock import MockTTS
from ._kokoro import KokoroTTS
from ._minimax import MinimaxTTS
from ._megatts3 import MegaTTS3

__all__ = [
    "BaseTTS",
    "MockTTS",
    "KokoroTTS",
    "MinimaxTTS",
    "MegaTTS3",
]
