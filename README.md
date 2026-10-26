# Dialog-RSN-1 examples

Dialog-RSN-1 is PolyAI's audio-native model for voice agents. It hears the caller, decides when
they've finished, and replies in one pass, spoken by the server or as text for your own TTS.

It speaks the OpenAI Realtime protocol, so any OpenAI Realtime client works once you change the
URL, the key and the model name. This repo collects every public sample in one place: framework
examples live here, and each guide's full example lives in its own repo, linked below.

Docs: [docs.poly.ai/dialog-rsn-1](https://docs.poly.ai/dialog-rsn-1) ·
[Quickstart](https://docs.poly.ai/dialog-rsn-1/quickstart) ·
[Reference](https://docs.poly.ai/api-reference/dialog-rsn-1/reference)

## Get a key

1. Sign up or log in at [studio.poly.ai](https://studio.poly.ai).
2. Create a key in the **API Keys** tab.
3. Put it in `POLY_API_KEY`, in each example's `.env` or your shell.

Every example connects to `wss://api.studio.poly.ai/v1/realtime`. Set `DIALOG_REALTIME_URL` only if
your key belongs to a regional workspace, for example `wss://api.us.poly.ai/v1/realtime`. A key
used on another region's host gets a 401.

| Variable | What it is |
| --- | --- |
| `POLY_API_KEY` | Your Dialog-RSN-1 API key. Required |
| `DIALOG_REALTIME_URL` | The full realtime URL. Optional; defaults to `wss://api.studio.poly.ai/v1/realtime` |

## In this repo

Framework examples: the framework's own OpenAI Realtime integration, with only the connection
changed. Each runs with the server speaking the reply (the default) or with your own TTS.

| Folder | What it is |
| --- | --- |
| [`pipecat/`](pipecat) | Pipecat's OpenAI Realtime voice bot on Dialog-RSN-1, with tools, in the browser over WebRTC |
| [`livekit/`](livekit) | A LiveKit Agents voice agent on LiveKit's OpenAI Realtime plugin, with tools, in your terminal or a LiveKit room |

## Guides and their repos

Each guide on docs.poly.ai has a repo with its full example.

| Guide | Repo | What it is |
| --- | --- | --- |
| [Python from scratch](https://docs.poly.ai/dialog-rsn-1/guides/python-from-scratch) | [dialog-rsn-1-python-from-scratch](https://github.com/polyai/dialog-rsn-1-python-from-scratch) | Voice agent on plain `websockets`, with tool calling and a live microphone |
| [Browser with JavaScript](https://docs.poly.ai/dialog-rsn-1/guides/javascript-browser) | [dialog-rsn-1-javascript-browser](https://github.com/polyai/dialog-rsn-1-javascript-browser) | Browser microphone through a small key-holding relay |
| [Speech to text](https://docs.poly.ai/dialog-rsn-1/guides/speech-to-text) | [dialog-rsn-1-speech-to-text](https://github.com/PolyAI-LDN/dialog-rsn-1-speech-to-text) | Transcriber and support agent on the `openai` SDK, in Python and Node |
| [Streaming to your TTS](https://docs.poly.ai/dialog-rsn-1/guides/streaming-text-to-speech) | [dialog-rsn-1-streaming-tts](https://github.com/PolyAI-LDN/dialog-rsn-1-streaming-tts) | Replies spoken through ElevenLabs as they stream, with barge-in |
| [Browser voice agent with Cartesia](https://docs.poly.ai/dialog-rsn-1/guides/voice-agent-cartesia) | [dialog-rsn-1-voice-agent](https://github.com/PolyAI-LDN/dialog-rsn-1-voice-agent) | FastAPI voice agent with Cartesia speech and a browser page |
| [LiveKit Agents](https://docs.poly.ai/dialog-rsn-1/guides/livekit) | [dialog-rsn-1-livekit](https://github.com/PolyAI-LDN/dialog-rsn-1-livekit) | A hotel agent on LiveKit Agents, with a scripted caller |
| [Migrating from OpenAI Realtime](https://docs.poly.ai/dialog-rsn-1/guides/openai-realtime-migration) | [dialog-rsn-1-openai-migration](https://github.com/PolyAI-LDN/dialog-rsn-1-openai-migration) | The same agent on the `openai` SDK, before and after the switch |

## Larger samples

| Repo | What it is |
| --- | --- |
| [dialog-rsn-1-realtime-agents](https://github.com/polyai/dialog-rsn-1-realtime-agents) | Multi-agent handoffs, a chat supervisor and a knowledge agent, in plain JavaScript |
| [dialog-rsn-1-sagemaker](https://github.com/polyai/dialog-rsn-1-sagemaker) | Notebook and client bridge for the Dialog-RSN-1 model package on Amazon SageMaker |

## License

[Apache 2.0](LICENSE).
