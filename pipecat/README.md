# Pipecat with Dialog-RSN-1

[`bot.py`](bot.py) is Pipecat's own OpenAI Realtime voice bot (`examples/realtime/realtime-openai.py`
and `realtime-openai-text.py`, v1.12.0) pointed at Dialog-RSN-1. Only the connection changes.

## Run it

Needs [uv](https://docs.astral.sh/uv/) and a Dialog-RSN-1 API key from
[studio.poly.ai](https://studio.poly.ai) (API Keys tab).

```bash
cd pipecat
cp .env.example .env               # add POLY_API_KEY, and CARTESIA_API_KEY for client-side speech
uv run bot.py                      # Dialog-RSN-1 speaks the reply
DIALOG_TTS=client uv run bot.py    # Dialog-RSN-1 writes it, Cartesia speaks it here
```

Then open <http://localhost:7860/client>, pick **SmallWebRTC**, press Connect, allow the microphone
and talk. The other transports listed are ones Pipecat's runner offers; this bot only sets up
SmallWebRTC. `uv run` installs Pipecat from the script's inline metadata, at the versions in
[`bot.py.lock`](bot.py.lock).

The bot greets you, and has two tools: the weather and a restaurant recommendation.

## Who speaks the reply

| `DIALOG_TTS` | Session | Pipeline |
|---|---|---|
| `server` (default) | `output_modalities: ["audio"]` | no TTS: Pipecat plays Dialog-RSN-1's audio |
| `client` | `output_modalities: ["text"]` | a `CartesiaTTSService` after the LLM speaks the text |

Server-side speech is the default and the simplest path. Client-side speech lets you pick any TTS
Pipecat supports.

## The swap

Against Pipecat's example, only the connection changes:

```python
llm = OpenAIRealtimeLLMService(
    api_key=os.environ["POLY_API_KEY"],               # was OPENAI_API_KEY
    base_url="wss://api.studio.poly.ai/v1/realtime",  # new; the default is OpenAI
    settings=OpenAIRealtimeLLMService.Settings(
        model="dialog-rsn-1",                         # new
        ...                                           # the rest is unchanged
```

Pipecat sends the key as `Authorization: Bearer`, which Dialog-RSN-1 accepts. The rest of
Pipecat's session config goes through as it is: `semantic_vad` and `input_audio_transcription`
are accepted, and the fields Dialog-RSN-1 doesn't use (`noise_reduction`) are ignored rather than
refused.

Set `DIALOG_REALTIME_URL` only if your key belongs to a regional workspace, for example
`wss://api.us.poly.ai/v1/realtime`. A key used on another region's host gets a 401.

## What works

On server-driven turn taking, in both modes:

- the greeting from `LLMRunFrame`;
- one reply per caller turn, with the server deciding where the turn ends;
- tool calls from the context's functions, with the result going back and used in the reply;
- several turns in a row with the context carried;
- barge-in: speaking over a reply stops it, and the reply is kept as far as you heard it.

## Limits

- Turns are always decided by Dialog-RSN-1, so Pipecat's `turn_detection=False` mode is refused.
- Poly extensions (`poly_knowledge`, `poly_response_language`, ...) can't be set through
  Pipecat's session config. See the [reference](https://docs.poly.ai/dialog-rsn-1/reference) and
  set them on the raw protocol.
- In the playground your line can appear under the reply to it, and a barge-in can be added to
  that same bubble. Dialog-RSN-1 writes the transcript after the reply, so the reply starts
  sooner, and Pipecat's client places your line when its transcript arrives. The conversation
  itself is right; only the playground's layout is affected.
- With `DIALOG_TTS=client`, Pipecat's realtime TTFB metric is wrong: it waits for model audio
  that never comes and stops at your next turn.
