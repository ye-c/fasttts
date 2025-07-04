import httpx
from utils.audio_utils import load_wav
from utils.models import TTSRequest


class BaseAPI:
    URL = None  # 子类必须定义
    HTTPX = httpx.AsyncClient(timeout=30)

    def tts(self, **kwargs):
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(self.URL, json=kwargs)
                resp.raise_for_status()  # 如果响应错误会抛异常
                data = resp.json()
                return data.get("audio"), data.get("sr")
        except Exception as e:
            print("请求失败：", e)

    async def tts_sync(self, **kwargs):
        """
        异步 TTS 调用，支持 await。
        :param kwargs: 包含 text, emotion, speed 等参数
        :return: {"audio": bytes, "sr": int}
        """
        try:
            resp = await self.HTTPX.post(self.URL, json=kwargs)
            resp.raise_for_status()
            data = resp.json()
            return data.get("audio"), data.get("sr")
        except Exception as e:
            print(f"请求失败({self.__class__.__name__}):", e)
            return {"audio": None, "sr": 0}


class MegaTTS3(BaseAPI):
    URL = "http://172.31.31.21:8800/tts/megatts3"


class CosyVoice(BaseAPI):
    URL = "http://172.31.31.21:8800/tts/cosy"

    async def tts_sync(self, **kwargs):
        payload = TTSRequest(**kwargs)
        if not payload.prompt_speech_16k:
            voice_wav = "assets/zh_reba18.wav"
            # voice_wav = "assets/zh_reba_manyou20.wav"
            payload.prompt_speech_16k = load_wav(voice_wav).squeeze().numpy().tolist()
        if not payload.instruct:
            payload.instruct = "轻松愉快"
        try:
            resp = await self.HTTPX.post(self.URL, json=payload.model_dump())
            resp.raise_for_status()
            data = resp.json()
            return data.get("audio"), data.get("sr")
        except Exception as e:
            print(f"请求失败({self.__class__.__name__}):", e)
            return {"audio": None, "sr": 0}
