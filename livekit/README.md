# LiveKit Agents with Dialog-RSN-1

[`agent.py`](agent.py) is a LiveKit Agents voice agent on LiveKit's OpenAI Realtime model, pointed
at Dialog-RSN-1. Only the connection changes.

For a fuller agent, a hotel front desk with a scripted caller, see the
[LiveKit Agents guide](https://docs.poly.ai/dialog-rsn-1/guides/livekit) and its
[repo](https://github.com/PolyAI-LDN/dialog-rsn-1-livekit).

## Run it

Needs the LiveKit CLI (`brew install livekit-cli`), [uv](https://docs.astral.sh/uv/) and a
Dialog-RSN-1 API key from [studio.poly.ai](https://studio.poly.ai) (API Keys tab).

```bash
cd livekit
cp .env.example .env                 # add POLY_API_KEY, and CARTESIA_API_KEY for client-side speech
lk agent console                     # Dialog-RSN-1 speaks the reply
DIALOG_TTS=client lk agent console   # Cartesia speaks it here
```

`lk agent console` runs `agent.py` from this directory's uv project and connects it to this
machine's microphone and speaker, with no LiveKit server needed. `--text` starts in text mode
(type a turn, press enter), `ctrl+t` switches between voice and text, `q` quits. The agent greets
you, and has two tools: the weather and a restaurant recommendation.

For LiveKit's browser playground instead, run a LiveKit server (`livekit-server --dev`, or a
LiveKit Cloud project), set `LIVEKIT_URL`, `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET`, start the
agent with `lk agent dev` instead, and connect from
[agents-playground.livekit.io](https://agents-playground.livekit.io).

## Who speaks the reply

| `DIALOG_TTS` | Realtime model | Session |
|---|---|---|
| `server` (default) | `modalities=["audio"]` | no `tts`: LiveKit plays Dialog-RSN-1's audio |
| `client` | `modalities=["text"]` | `tts=cartesia.TTS()` speaks the text |

Server-side speech is the default and the simplest path. LiveKit's OpenAI voice name is ignored;
set a Cartesia voice id through the session to change the voice. Client-side speech lets you pick
any TTS LiveKit supports.

## The swap

Against pointing LiveKit's realtime model at OpenAI, only the connection changes:

```python
openai.realtime.RealtimeModel(
    base_url="wss://api.studio.poly.ai/v1/realtime",  # new; the default is OpenAI
    api_key=os.environ["POLY_API_KEY"],               # was OPENAI_API_KEY
    model="dialog-rsn-1",                             # new
)
```

Give the full realtime URL. LiveKit appends `/realtime` only to paths it recognises (`/v1`,
`/openai`), so a base URL with any other path is used as it is.

LiveKit sends the key as `Authorization: Bearer`, which Dialog-RSN-1 accepts. The rest of its
session config goes through as it is; the fields Dialog-RSN-1 doesn't use (`semantic_vad`
eagerness, `noise_reduction`, the output voice, tracing) are ignored rather than refused.

Set `DIALOG_REALTIME_URL` only if your key belongs to a regional workspace, for example
`wss://api.us.poly.ai/v1/realtime`. A key used on another region's host gets a 401.

## What works

On server-driven turn taking, in both modes:

- the greeting from `generate_reply`;
- one reply per caller turn, with the server deciding where the turn ends;
- tool calls from `@function_tool` methods, with the result going back and used in the reply;
- several turns in a row with the context carried;
- barge-in over a reply Dialog-RSN-1 is speaking.

## Limits

- Poly extensions (`poly_knowledge`, `poly_response_language`, ...) can't be set through
  LiveKit's session config. Send them on a raw `session.update`, as the
  [LiveKit guide](https://docs.poly.ai/dialog-rsn-1/guides/livekit#settings-that-matter) shows;
  the [reference](https://docs.poly.ai/dialog-rsn-1/reference) lists them all.
- `lk agent console` (CLI 2.18.8) shows each of your spoken turns twice: once from the final
  transcript and once when the message joins the conversation. That is the CLI; the conversation
  has each turn once. Its agent debug logs also print in among the conversation.

Not tested yet: LiveKit's own turn detector with `create_response: false`.
