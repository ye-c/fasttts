import os
import numpy as np
import asyncio
import json
import soundfile as sf
import ssl
import websockets
from io import BytesIO
# import nest_asyncio

from .base import BaseTTS


class MinimaxTTS(BaseTTS):
    """
    Minimax TTS模型适配接口，适用于同步批量文本的tts调用。

    | 类别   | 音色ID                       | 音色描述         | 版本 |
    | ---- | -------------------------- | ------------ | -- |
    | 男性音色 | male-qn-qingse             | 青涩青年音色       | v1 |
    | 男性音色 | male-qn-jingying           | 精英青年音色       | v1 |
    | 男性音色 | male-qn-badao              | 霸道青年音色       | v1 |
    | 男性音色 | male-qn-daxuesheng         | 青年大学生音色      | v1 |
    | 男性音色 | presenter_male            | 男性主持人        | v1 |
    | 男性音色 | audiobook_male_1         | 男性有声书1       | v1 |
    | 男性音色 | audiobook_male_2         | 男性有声书2       | v1 |
    | 男性音色 | male-qn-qingse-jingpin     | 青涩青年音色-beta  | v1 |
    | 男性音色 | male-qn-jingying-jingpin   | 精英青年音色-beta  | v1 |
    | 男性音色 | male-qn-badao-jingpin      | 霸道青年音色-beta  | v1 |
    | 男性音色 | male-qn-daxuesheng-jingpin | 青年大学生音色-beta | v1 |
    | 男性音色 | clever_boy                | 聪明男童         | v2 |
    | 男性音色 | cute_boy                  | 可爱男童         | v2 |
    | 女性音色 | female-shaonv              | 少女音色         | v1 |
    | 女性音色 | female-yujie               | 御姐音色         | v1 |
    | 女性音色 | female-chengshu            | 成熟女性音色       | v1 |
    | 女性音色 | female-tianmei             | 甜美女性音色       | v1 |
    | 女性音色 | presenter_female          | 女性主持人        | v1 |
    | 女性音色 | audiobook_female_1       | 女性有声书1       | v1 |
    | 女性音色 | audiobook_female_2       | 女性有声书2       | v1 |
    | 女性音色 | female-shaonv-jingpin      | 少女音色-beta    | v1 |
    | 女性音色 | female-yujie-jingpin       | 御姐音色-beta    | v1 |
    | 女性音色 | female-chengshu-jingpin    | 成熟女性音色-beta  | v1 |
    | 女性音色 | female-tianmei-jingpin     | 甜美女性音色-beta  | v1 |
    | 女性音色 | lovely_girl               | 萌萌女童         | v2 |
    | 女性音色 | qiaopi_mengmei            | 俏皮萌妹         | v2 |
    | 女性音色 | diadia_xuemei             | 喃喃学妹         | v2 |
    | 女性音色 | danya_xuejie              | 淡雅学姐         | v2 |
    | 女性音色 | wumei_yujie               | 妩媚御姐         | v2 |
    | 女性音色 | tianxin_xiaoling          | 甜心小玲         | v2 |


    """

    def __init__(
        self,
        api_key="",
        module="speech-02-hd",
        emotion="neutral",
        voice="female-tianmei",
        tts_samplerate=32000,
    ):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.module = module
        self.emotion = emotion
        self.voice_id = voice
        self.tts_samplerate = tts_samplerate

    def tts(self, text: str, emotion: str = None, speed=1.0):
        """
        # 同步调用：文本→完整音频
        """
        loop = asyncio.get_running_loop()
        result = loop.run_until_complete(self.tts_sync(text, emotion, speed))
        return result

    async def tts_sync(self, text: str, emotion: str = None, speed=1.0, **kwargs):
        url = "wss://api.minimax.chat/ws/v1/t2a_v2"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        audio_hex_chunks = []

        async with websockets.connect(
            url, additional_headers=headers, ssl=ssl_context
        ) as ws:
            resp = json.loads(await ws.recv())
            if resp.get("event") != "connected_success":
                raise RuntimeError(f"WebSocket连接失败: {resp}")

            await ws.send(
                json.dumps(
                    {
                        "event": "task_start",
                        "model": self.module,
                        "voice_setting": {
                            "voice_id": self.voice_id,
                            "speed": speed,
                            "vol": 1,
                            "pitch": 0,
                            "emotion": emotion or self.emotion,
                        },
                        "audio_setting": {
                            "sample_rate": self.tts_samplerate,
                            "bitrate": 128000,
                            "format": "mp3",
                            "channel": 1,
                        },
                    }
                )
            )
            resp = json.loads(await ws.recv())
            if resp.get("event") != "task_started":
                raise RuntimeError(f"TTS启动失败: {resp}")

            await ws.send(json.dumps({"event": "task_continue", "text": text}))

            while True:
                resp = json.loads(await ws.recv())
                if "data" in resp and "audio" in resp["data"]:
                    audio_hex_chunks.append(resp["data"]["audio"])
                if resp.get("is_final"):
                    break
            try:
                await ws.send(json.dumps({"event": "task_finish"}))
            except Exception:
                pass
            await ws.close()

        audio_bytes = bytes.fromhex("".join(audio_hex_chunks))
        buf = BytesIO(audio_bytes)
        with sf.SoundFile(buf, "rb") as f:
            samplerate = f.samplerate
            data = f.read(dtype="float32")

        return np.array(data), samplerate
