import numpy as np
import sounddevice as sd


def play_audio(audio: np.ndarray, samplerate: int):
    """
    用于直接播放器本地音频。阻塞直到播放完成。
    """
    sd.play(audio, samplerate)
    sd.wait()
