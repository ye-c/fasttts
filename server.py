from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from tts import KokoroTTS, MegaTTS3
from utils.task_queue import TTSQueue, PlaybackQueue
from utils.playback import play_audio
from utils.stream_utils import TextBuffer, clean_markdown_for_tts
from utils.models import TTSText


# 初始化文本缓冲区
text_buffer = TextBuffer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # tts_engine = KokoroTTS(voice="zf_071")
    tts_engine = MegaTTS3()
    app.state.play_queue = PlaybackQueue(play_audio)
    app.state.text_queue = TTSQueue(
        lambda text: tts_engine.tts(text), app.state.play_queue
    )

    await app.state.play_queue.start_worker()
    await app.state.text_queue.start_worker()

    await app.state.text_queue.add("我来了")

    yield

    await app.state.text_queue.stop_worker()
    await app.state.play_queue.stop_worker()


app = FastAPI(lifespan=lifespan)


@app.post("/status")
async def status(request: Request):
    global text_buffer
    text_queue = request.app.state.text_queue
    play_queue = request.app.state.play_queue
    return {
        "status": "success",
        "tts_queue": text_queue.len,
        "playback_queue": play_queue.len,
        "text_buffer": text_buffer,
    }


@app.post("/tts")
async def tts_endpoint(payload: TTSText, request: Request):
    text_queue = request.app.state.text_queue
    await text_queue.add(payload.text)
    return {"status": "success", "queue": text_queue.len}


@app.post("/stream_tts")
async def stream_tts_endpoint(payload: TTSText, request: Request):
    text_queue = request.app.state.text_queue
    global text_buffer
    text_buffer.add_text(payload.text)
    sentence_gen = text_buffer.pop_sentence()
    while sentence := next(sentence_gen):
        cleaned = clean_markdown_for_tts(sentence)
        if not cleaned.strip():
            continue  # 该句全是无意义内容，跳过
        await text_queue.add(sentence)
    return {"status": "success", "queue_size": text_queue.len}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8800)
