# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pipecat-ai[openai,cartesia,silero,webrtc,runner]==1.12.0",
#     "python-dotenv",
# ]
# ///
"""Pipecat's OpenAI Realtime voice bot, pointed at Dialog-RSN-1.

Pipecat's own `examples/realtime/realtime-openai.py` and `realtime-openai-text.py` (v1.12.0),
with only the connection changed: `base_url`, the key and the model name. See README.md.

    uv run bot.py                    # Dialog-RSN-1 speaks the reply
    DIALOG_TTS=client uv run bot.py  # Dialog-RSN-1 writes it, Cartesia here speaks it

Then open http://localhost:7860/client and pick SmallWebRTC.
"""

import os

from dotenv import load_dotenv
from loguru import logger
from pipecat.frames.frames import LLMRunFrame
from pipecat.observers.loggers.transcription_log_observer import TranscriptionLogObserver
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.llm_service import FunctionCallParams
from pipecat.services.openai.realtime.events import (
    AudioConfiguration,
    AudioInput,
    InputAudioNoiseReduction,
    InputAudioTranscription,
    SemanticTurnDetection,
    SessionProperties,
)
from pipecat.services.openai.realtime.llm import OpenAIRealtimeLLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner

load_dotenv(override=True)

# The swap. Everything else in this file is Pipecat's example as published.
DIALOG_URL = os.environ.get("DIALOG_REALTIME_URL", "wss://api.studio.poly.ai/v1/realtime")
DIALOG_KEY = os.environ["POLY_API_KEY"]
DIALOG_MODEL = "dialog-rsn-1"
# "server": Dialog-RSN-1 synthesises the reply and streams its audio. "client": it streams text and
# the pipeline's own TTS speaks it.
TTS = os.environ.get("DIALOG_TTS", "server")

INSTRUCTIONS = """You are a helpful and friendly assistant for a restaurant guide.
You can look up the weather and recommend a restaurant. Always call a tool when one fits.
You are in a voice conversation: keep replies to one or two short sentences."""


async def get_current_weather(params: FunctionCallParams, location: str, format: str):
    """Get the current weather.

    Args:
        location: The city and state, e.g. "San Francisco, CA".
        format: The temperature unit to use. Must be either "celsius" or "fahrenheit".
    """
    temperature = 75 if format == "fahrenheit" else 24
    await params.result_callback({"conditions": "nice", "temperature": temperature, "format": format})


async def get_restaurant_recommendation(params: FunctionCallParams, location: str):
    """Get a restaurant recommendation.

    Args:
        location: The city and state, e.g. "San Francisco, CA".
    """
    await params.result_callback({"name": "The Golden Dragon"})


TOOLS = [get_current_weather, get_restaurant_recommendation]


def build_llm() -> OpenAIRealtimeLLMService:
    """Pipecat's stock realtime service and session config, connected to Dialog-RSN-1."""
    return OpenAIRealtimeLLMService(
        api_key=DIALOG_KEY,
        base_url=DIALOG_URL,
        settings=OpenAIRealtimeLLMService.Settings(
            model=DIALOG_MODEL,
            system_instruction=INSTRUCTIONS,
            session_properties=SessionProperties(
                audio=AudioConfiguration(
                    input=AudioInput(
                        transcription=InputAudioTranscription(),
                        turn_detection=SemanticTurnDetection(),
                        noise_reduction=InputAudioNoiseReduction(type="near_field"),
                    )
                ),
                output_modalities=["audio"] if TTS == "server" else ["text"],
            ),
        ),
    )


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    llm = build_llm()
    speech = []
    if TTS == "client":
        speech = [
            CartesiaTTSService(
                api_key=os.environ["CARTESIA_API_KEY"],
                settings=CartesiaTTSService.Settings(voice="86e30c1d-714b-4074-a1f2-1cb6b552fb49"),
            )
        ]
    context = LLMContext([{"role": "developer", "content": "Say hello!"}], TOOLS)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(context)

    pipeline = Pipeline(
        [
            transport.input(),
            user_aggregator,
            llm,
            *speech,
            transport.output(),
            assistant_aggregator,
        ]
    )
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(enable_metrics=True),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
        observers=[TranscriptionLogObserver()],
    )
    runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)
    await runner.add_workers(worker)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await runner.cancel()

    await runner.run()


async def bot(runner_args: RunnerArguments):
    transport = await create_transport(
        runner_args,
        {"webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True)},
    )
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
