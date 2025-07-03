# import numpy as np
import httpx

# from .base import BaseTTS


class BaseAPI:
    URL = None  # 子类必须定义

    def tts(self, **kwargs):
        try:
            with httpx.Client() as client:
                resp = client.post(self.URL, json=kwargs, timeout=10)
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
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.URL, json=kwargs, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                return data.get("audio"), data.get("sr")
        except Exception as e:
            print(f"请求失败（{self.__class__.__name__}）：", e)
            return {"audio": None, "sr": 0}


class MegaTTS3(BaseAPI):
    URL = "http://172.31.31.21:8800/tts/megatts3"


class CosyVoice(BaseAPI):
    URL = "http://172.31.31.21:8800/tts/cosy"
