import os
import numpy as np
import asyncio
import json
import soundfile as sf
import ssl
import websockets
from io import BytesIO

from .base import BaseTTS


class MinimaxTTS(BaseTTS):
    """
    Minimax TTS模型适配接口，适用于同步批量文本的tts调用。
    """

    def __init__(
        self,
        api_key="",
        module="speech-02-hd",
        emotion="neutral",
        voice="male-qn-qingse",
        tts_samplerate=32000,
    ):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.module = module
        self.emotion = emotion
        self.voice_id = voice
        self.tts_samplerate = tts_samplerate

    def tts(self, text: str):
        """
        同步调用：文本→完整音频
        """
        import nest_asyncio

        loop = asyncio.get_running_loop()
        nest_asyncio.apply()
        return loop.run_until_complete(self.tts_sync(text))

    async def tts_sync(self, text: str):
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
                            "speed": 1.2,
                            "vol": 1,
                            "pitch": 0,
                            "emotion": self.emotion,
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
        return samplerate, np.array(data)
