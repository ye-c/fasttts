import numpy as np
from utils.playback import play_audio


class BaseTTS:
    """
    TTS标准接口：所有TTS后端都应继承本类，实现 tts/stream_tts 两种方式。
    """

    def tts(self, text: str) -> tuple[int, np.ndarray]:
        raise NotImplementedError

    def stream_tts(self, text: str):
        raise NotImplementedError

    def play(self, audio, sr):
        play_audio(audio, sr)
