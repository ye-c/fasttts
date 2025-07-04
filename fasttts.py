import tts
from datetime import datetime
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from utils.task_queue import TTSQueue, PlaybackQueue
from utils.models import TTSRequest
from utils.stream_utils import TextBuffer, clean_text_for_tts
from utils.logg import get_logger

logger = get_logger()
# 全局队列映射
engine_map = {}
# 全局文本缓冲区
text_buffer = TextBuffer()
playback_queue = PlaybackQueue()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine_map, playback_queue

    # 初始化所有 TTS 引擎及其独立队列
    engines = {
        "megatts3": tts.MegaTTS3(),
        "minimax": tts.MinimaxTTS(),
        "cosyvoice": tts.CosyVoice(),
    }

    await playback_queue.start_worker()
    for name, tts_engine in engines.items():
        text_queue = TTSQueue(
            lambda payload, e=tts_engine: e.tts_sync(**payload.model_dump()),
            playback_queue,
        )
        await text_queue.start_worker()

        # 存储引擎与队列映射关系
        engine_map[name] = {
            "engine": tts_engine,
            "text_queue": text_queue,
            # "playback_queue": playback_queue,
        }

    await text_queue.add(TTSRequest(text="Hello，我来啦"))
    yield

    # 清理资源
    await playback_queue.stop_worker()
    for name in engine_map:
        await engine_map[name]["text_queue"].stop_worker()


app = FastAPI(lifespan=lifespan)


@app.post("/status")
async def status_all(request: Request):
    """返回全局状态 + 所有引擎状态"""
    global engine_map, text_buffer, playback_queue

    engines_status = {}
    for name, engine_info in engine_map.items():
        engines_status[name] = {
            "text_queue": engine_info["text_queue"].len,
            # "playback_queue": engine_info["playback_queue"].len,
        }

    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "global": {
            "text_buffer": str(text_buffer),
            "active_engines": list(engine_map.keys()),
        },
        "playback_queue": playback_queue.len,
        "engines": engines_status,
    }


@app.post("/status/{engine_name}")
async def status_single(engine_name: str, request: Request):
    """返回指定引擎的详细状态"""
    if engine_name not in engine_map:
        return {"status": "error", "message": f"Engine {engine_name} not found"}

    engine_info = engine_map[engine_name]
    return {
        "status": "success",
        "engine": engine_name,
        "timestamp": datetime.now().isoformat(),
        "tts_queue": engine_info["text_queue"].len,
        "config": {
            "engine_type": engine_info["engine"].__class__.__name__,
            "tts_url": getattr(engine_info["engine"], "URL", "N/A"),
        },
    }


@app.post("/tts")
async def default_tts_endpoint(payload: TTSRequest, request: Request):
    # 默认使用 megatts3 cosyvoice minimax
    return await tts_endpoint("cosyvoice", payload, request)


@app.post("/tts/{engine_name}")
async def tts_endpoint(engine_name: str, payload: TTSRequest, request: Request):
    if engine_name not in engine_map:
        return {"status": "error", "message": f"Engine {engine_name} not found"}

    text_queue = engine_map[engine_name]["text_queue"]

    global text_buffer
    text_buffer.add_text(payload.text)
    # sentence_gen = text_buffer.pop_sentence()
    # while sentence := next(sentence_gen):
    for sentence in text_buffer.pop_sentence():
        cleaned = clean_text_for_tts(sentence)
        if not cleaned.strip():
            continue  # 该句全是无意义内容，跳过
        new_payload = payload.model_copy(update={"text": cleaned})
        logger.debug(f"Sentence: {cleaned}")
        logger.debug(f"text_queue={text_queue.len}")
        await text_queue.add(new_payload)

    return {"status": "success", "queue": text_queue.len, "engine": engine_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("fasttts:app", host="0.0.0.0", port=8800)
