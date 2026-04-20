#!/usr/bin/env python3
"""
Debug script to trace the entire flow and see where traces are being created/lost.
"""
import asyncio
import uuid
import logging
from dotenv import load_dotenv
from agents import Runner
from agents.tracing import set_trace_processors
from hr_agents.orchestrator import orchestrator_agent
from tracing.langfuse_setup import get_langfuse_client, flush
from tracing.langfuse_processor import LangfuseTracingProcessor

# Enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

langfuse = get_langfuse_client()

async def debug_session():
    employee_id = "debug-" + str(uuid.uuid4())[:8]
    
    logger.info(f"Starting debug session: {employee_id}")
    
    # Create main session trace
    session_trace = langfuse.trace(
        name="debug-onboarding-session",
        user_id=employee_id,
        metadata={"session_type": "hr_onboarding_debug", "interface": "debug"},
    )
    logger.info(f"✓ Session trace created: {session_trace.id}")
    
    conversation_history = []
    user_input = "What is the remote work policy?"
    
    conversation_history.append({"role": "user", "content": user_input})
    
    # Create agent-turn span
    span = session_trace.span(
        name="agent-turn",
        input={"message": user_input},
        metadata={"employee_id": employee_id},
    )
    logger.info(f"✓ Agent-turn span created")
    
    try:
        # Create processor with debug logging
        logger.info("Creating LangfuseTracingProcessor...")
        processor = LangfuseTracingProcessor(span, langfuse_client=langfuse, user_input=user_input)
        logger.info("✓ Processor created, setting trace processors...")
        
        set_trace_processors([processor])
        logger.info("✓ Trace processors set")
        
        logger.info("Running orchestrator agent...")
        result = await Runner.run(
            orchestrator_agent,
            input=conversation_history,
        )
        logger.info("✓ Agent execution completed")
        
        response_text = result.final_output
        logger.info(f"Response: {response_text[:100]}...")
        
        # End the span
        span.end(output={"response": response_text}, level="DEFAULT")
        logger.info("✓ Agent-turn span ended")
        
        conversation_history = result.to_input_list()
        
    except Exception as e:
        logger.error(f"Error during agent execution: {str(e)}", exc_info=True)
        span.end(output={"error": str(e)}, level="ERROR")
    
    finally:
        set_trace_processors([])
        logger.info("Trace processors cleared")
    
    # Update session trace
    session_trace.update(
        output={"turns": 1},
        metadata={"completed": True},
    )
    logger.info("✓ Session trace updated")
    
    # Flush all traces
    logger.info("Flushing traces to Langfuse...")
    try:
        flush()
        logger.info("✅ ALL TRACES FLUSHED SUCCESSFULLY")
        logger.info(f"Session Trace ID: {session_trace.id}")
    except Exception as e:
        logger.error(f"Error flushing: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(debug_session())
