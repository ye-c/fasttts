import numpy as np
import httpx

from .base import BaseTTS


class MegaTTS3(BaseTTS):
    URL = "http://172.31.31.21:8889"

    def tts(self, text: str):
        payload = {"text": text}
        try:
            with httpx.Client() as client:
                resp = client.post(f"{self.URL}/tts", json=payload, timeout=10)
                resp.raise_for_status()  # 如果响应错误会抛异常
                data = resp.json()
                return data.get("audio"), data.get("sr")
        except Exception as e:
            print("请求失败：", e)
1