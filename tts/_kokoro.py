import numpy as np

from utils.audio_utils import add_silence
from .base import BaseTTS


class KokoroTTS(BaseTTS):
    """
    Kokoro模型适配接口，支持中英文混合文本的标准TTS调用。
    """

    def __init__(
        self,
        voice="af_maple",
        repo_id="hexgrad/Kokoro-82M-v1.1-zh",
        device="mps",
        samplerate=24000,
    ):
        from kokoro import KPipeline

        self.en_pipeline = KPipeline(lang_code="a", device=device)
        self.zh_pipeline = KPipeline(
            lang_code="z",
            repo_id=repo_id,
            en_callable=lambda text: self.en_pipeline.g2p(text)[0],
            device=device,
        )
        self.voice = voice
        self.samplerate = samplerate

    def _pipeline_tts(self, text, voice="", speed=1.2, split_pattern=r"\n+"):
        for _, _, audio_tensor in self.zh_pipeline(
            text, voice=voice or self.voice, speed=speed, split_pattern=split_pattern
        ):
            audio = audio_tensor.detach().cpu().numpy()
            audio = add_silence(audio, self.samplerate, 0.06, noise=True)
            yield audio, self.samplerate

    def tts(self, text: str):
        audio_all = []
        for i, audio, sr in self.stream_tts(text):
            audio_all.append(audio)
        audio = np.concatenate(audio_all) if audio_all else np.zeros(0, np.float32)
        return audio, sr

    def stream_tts(self, text: str):
        for i, (audio, sr) in enumerate(self._pipeline_tts(text)):
            # print(f"{i=}")
            yield i, audio, sr
