import asyncio
from .audio_utils import add_silence
from .logg import get_logger
from utils.playback import play_audio

logger = get_logger()


class TTSQueue:
    def __init__(self, tts_fn, playback_queue):
        self._queue = asyncio.Queue()
        self._tts_fn = tts_fn  # 例如tts_engine.tts
        self._playback_queue = playback_queue
        self._worker = None
        self._shutdown = False

    @property
    def len(self):
        return self._queue.qsize()

    async def start_worker(self):
        if self._worker is None:
            self._worker = asyncio.create_task(self._loop())

    async def _loop(self):
        while not self._shutdown:
            text = await self._queue.get()
            if text is None:
                break
            # TTS处理
            audio, sr = await self._tts_fn(text)
            # TTS产物丢到下一队列
            await self._playback_queue.add(audio, sr)
            self._queue.task_done()

    async def add(self, text):
        await self._queue.put(text)

    async def stop_worker(self):
        self._shutdown = True
        await self._queue.put(None)
        if self._worker:
            await self._worker


class PlaybackQueue:
    def __init__(self):
        self._queue = asyncio.Queue()
        self._worker = None
        self._shutdown = False

    @property
    def len(self):
        return self._queue.qsize()

    async def start_worker(self):
        if self._worker is None:
            self._worker = asyncio.create_task(self._loop())

    async def _loop(self):
        while not self._shutdown:
            task = await self._queue.get()
            if task is None:
                break
            audio, sr = task
            logger.debug(f"playback_queue={self._queue.qsize()}")
            await asyncio.to_thread(play_audio, audio, sr)
            self._queue.task_done()

    async def add(self, audio, samplerate):
        try:
            if self._queue.empty():
                audio = add_silence(audio, samplerate, 0.6, True)
            await self._queue.put((audio, samplerate))
        except Exception as e:
            logger.error(f"{type(audio)=} {samplerate=}")
            logger.error(e)

    async def stop_worker(self):
        self._shutdown = True
        await self._queue.put(None)
        if self._worker:
            await self._worker
