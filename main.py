import asyncio
import uuid
import logging
from dotenv import load_dotenv
from agents import Runner
from agents.tracing import set_trace_processors
from hr_agents.orchestrator import orchestrator_agent
from tracing.langfuse_setup import get_langfuse_client, score_response, flush
from tracing.langfuse_processor import LangfuseTracingProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

langfuse = get_langfuse_client()
logger.info("✅ Langfuse client initialized in main.py")


async def run_onboarding_session(employee_id: str | None = None):
    if not employee_id:
        employee_id = str(uuid.uuid4())[:8]

    session_trace = langfuse.trace(
        name="onboarding-session",
        user_id=employee_id,
        metadata={"session_type": "hr_onboarding"},
    )

    print(f"\nHR Onboarding Assistant — Session ID: {employee_id}")
    print("Type 'exit' to end the session.\n")

    conversation_history = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit", "bye"):
            print("Assistant: Goodbye! Best of luck with your onboarding.")
            break

        if not user_input:
            continue

        conversation_history.append({"role": "user", "content": user_input})

        span = session_trace.span(
            name="agent-turn",
            input={"message": user_input},
            metadata={"employee_id": employee_id},
        )

        try:
            processor = LangfuseTracingProcessor(span, langfuse_client=langfuse)
            set_trace_processors([processor])

            result = await Runner.run(
                orchestrator_agent,
                input=conversation_history,
            )

            set_trace_processors([])
            response_text = result.final_output
            span.end(output={"response": response_text}, level="DEFAULT")
            conversation_history = result.to_input_list()
            print(f"\nAssistant: {response_text}\n")
            logger.debug(f"Agent turn completed successfully")

        except Exception as e:
            set_trace_processors([])
            span.end(output={"error": str(e)}, level="ERROR")
            logger.error(f"Error during agent turn: {str(e)}")
            print(f"\nAssistant: I encountered an error. Please try again. ({e})\n")

    session_trace.update(
        output={"turns": len([m for m in conversation_history if m.get("role") == "user"])},
        metadata={"completed": True},
    )
    logger.info("✅ Onboarding session completed. Flushing traces...")

    try:
        flush()
        logger.info("✅ All traces flushed successfully to Langfuse")
    except Exception as e:
        logger.error(f"❌ Failed to flush traces: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_onboarding_session())
