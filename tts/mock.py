import numpy as np
from .base import BaseTTS


class MockTTS(BaseTTS):
    """
    开发调试用Mock - 不调用真实模型，直接输出静音音频。
    """

    def tts(self, text: str):
        samplerate = 24000
        duration = min(3, len(text) * 0.05)
        audio = np.zeros(int(samplerate * duration), dtype=np.float32)
        return samplerate, audio

    def stream_tts(self, text: str):
        samplerate = 24000
        duration = min(3, len(text) * 0.05)
        audio = np.zeros(int(samplerate * duration), dtype=np.float32)
        block = int(samplerate * 1)  # 每1秒一块
        for start in range(0, len(audio), block):
            yield samplerate, audio[start : start + block]
