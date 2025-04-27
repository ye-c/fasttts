# fasttts

**fasttts** is a fast, local Text-to-Speech (TTS) service supporting streaming input, sentence buffering, and strict serial processing via independent asynchronous queues for synthesis and playback. Built with FastAPI, it features robust real-time interaction, natural sentence segmentation, and is suitable for AI, subtitle, voice assistant, and developer scenarios.

## Features

- 🚀 **Asynchronous & Efficient**: Separate serial queues for TTS and audio playback maximize throughput and keep audio output in order.
- 🌐 **Multi-language Support**: Fluent handling of English, Chinese, or mixed text; automatic sentence segmentation for smooth speech.
- 🔄 **Streaming Input Friendly**: Integrates easily with LLMs or any AI model that streams output; texts are buffered and played as soon as complete sentences are formed.
- 🧹 **Markdown & Noise Cleaning**: Automatically skips code blocks, headings, and divider lines for more natural speech content.
- 📊 **Real-time Monitoring**: Query endpoints to check queue length and buffer status anytime with `/status`.

## Directory Structure

```
fasttts/
│
├── tts/                # TTS engine adapters
├── utils/              # Utilities (audio playback, markdown cleaner, async queues, etc.)
├── server.py           # Optional server/router descriptor
├── README.md
├── .gitignore
├── pyproject.toml
├── uv.lock
└── ...
```

## Quick Start

1. **Install dependencies**
   ```
   uv sync
   ```

2. **Launch the server**
   ```
   uv run server.py
   ```

3. **API endpoints**
   - `POST /tts`   Submit a full text for TTS.
     Request: `{"text": "Hello, world!"}`
   - `POST /stream_tts`  Stream/append texts for sentence-wise TTS playback (ideal for incremental output from LLMs/AI systems).
   - `POST /status`  Query the runtime queue situation and current buffer states.

4. **Plugins & Customization**
   - You may swap out TTS engines or playback modules by adapting code in `tts/` and `utils/`.
   - Easy to extend or integrate with other voice AI pipelines.

## Typical Use Cases

- Local voice assistant and smart home notifications
- Real-time AI (LLM) text-to-speech in chatbot or agent applications
- Subtitle-aligned narration for A/V sync
- Automated pipeline for custom voice projects

## TODO / Future Plans

- Broaden TTS engine and voice model support
- Websocket support for real-time progress feedback
- Automated Markdown/code cleaner improvements
