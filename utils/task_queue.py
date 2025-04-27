import asyncio


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
            audio, sr = await asyncio.to_thread(self._tts_fn, text)
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
    def __init__(self, play_fn):
        self._queue = asyncio.Queue()
        self._play_fn = play_fn  # 例如play_audio
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
            await asyncio.to_thread(self._play_fn, audio, sr)
            self._queue.task_done()

    async def add(self, audio, samplerate):
        await self._queue.put((audio, samplerate))

    async def stop_worker(self):
        self._shutdown = True
        await self._queue.put(None)
        if self._worker:
            await self._worker
