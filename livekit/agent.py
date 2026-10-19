"""A LiveKit Agents voice agent on Dialog-RSN-1.

LiveKit's OpenAI Realtime agent, with only the connection changed from pointing it at OpenAI:
`base_url`, the key and the model name. See README.md.

    lk agent console                    # Dialog-RSN-1 speaks the reply
    DIALOG_TTS=client lk agent console  # Cartesia here speaks it

Run from this directory. `console` talks through this machine's microphone and speaker.
"""

import logging
import os

from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli
from livekit.agents.llm import function_tool
from livekit.plugins import cartesia, openai

logger = logging.getLogger("dialog-agent")
load_dotenv()

# The swap. The full realtime URL: LiveKit appends `/realtime` only to paths it recognises
# (`/v1`, `/openai`), and uses any other path as it is.
DIALOG_URL = os.environ.get("DIALOG_REALTIME_URL", "wss://api.studio.poly.ai/v1/realtime")
DIALOG_KEY = os.environ["POLY_API_KEY"]
DIALOG_MODEL = "dialog-rsn-1"
# "server": Dialog-RSN-1 synthesises the reply and streams its audio. "client": it streams text and
# the session's own TTS speaks it.
TTS = os.environ.get("DIALOG_TTS", "server")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a helpful and friendly assistant for a restaurant guide. "
            "You can look up the weather and recommend a restaurant. Always call a tool when "
            "one fits. You are in a voice conversation: keep replies to one or two short "
            "sentences.",
        )

    async def on_enter(self) -> None:
        self.session.generate_reply(instructions="greet the user and offer your help")

    @function_tool
    async def get_current_weather(self, location: str) -> str:
        """Called when the user asks about the weather.

        Args:
            location: The city, e.g. "London".
        """
        logger.info(f"looking up weather for {location}")
        return "sunny, 22 degrees Celsius"

    @function_tool
    async def get_restaurant_recommendation(self, location: str) -> str:
        """Called when the user asks for a restaurant recommendation.

        Args:
            location: The city, e.g. "London".
        """
        return "The Golden Dragon"


def build_llm() -> openai.realtime.RealtimeModel:
    """LiveKit's OpenAI Realtime model, connected to Dialog-RSN-1."""
    return openai.realtime.RealtimeModel(
        base_url=DIALOG_URL,
        api_key=DIALOG_KEY,
        model=DIALOG_MODEL,
        modalities=["audio"] if TTS == "server" else ["text"],
    )


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    tts = cartesia.TTS() if TTS == "client" else None
    session: AgentSession[None] = AgentSession(llm=build_llm(), tts=tts)
    await session.start(agent=Assistant(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
