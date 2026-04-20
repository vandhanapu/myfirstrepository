import streamlit as st
import asyncio
import uuid
import time
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
logger.info("✅ Langfuse client initialized in app.py")

st.set_page_config(page_title="HR Onboarding Assistant", page_icon="🏢", layout="centered")

st.title("HR Onboarding Assistant")
st.caption("Powered by OpenAI Agents SDK + Langfuse Observability")

if "employee_id" not in st.session_state:
    st.session_state.employee_id = str(uuid.uuid4())[:8]

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "trace_id" not in st.session_state:
    trace = langfuse.trace(
        name="onboarding-session",
        user_id=st.session_state.employee_id,
        metadata={"session_type": "hr_onboarding", "interface": "streamlit"},
    )
    st.session_state.trace_id = trace.id
    st.session_state.trace = trace

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Welcome! I'm your HR Onboarding Assistant. Your session ID is **{st.session_state.employee_id}**.\n\nI can help you with:\n- Parsing your offer letter\n- Answering policy questions\n- Managing your onboarding checklist\n\nHow can I help you today?",
        }
    ]

with st.sidebar:
    st.header("Session Info")
    st.write(f"**Employee ID:** `{st.session_state.employee_id}`")
    st.write(f"**Trace ID:** `{st.session_state.trace_id}`")
    st.divider()
    st.subheader("Quick Prompts")
    quick_prompts = [
        "How many vacation days do I get?",
        "What is the remote work policy?",
        "Show me my onboarding tasks",
        "How does the 401k match work?",
        "What happens during performance reviews?",
    ]
    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True):
            st.session_state.pending_prompt = prompt

    st.divider()
    st.subheader("Feedback")
    if st.button("👍 Helpful", use_container_width=True):
        score_response(st.session_state.trace_id, "user-feedback", 1.0, "Thumbs up")
        st.success("Thanks for the feedback!")
    if st.button("👎 Not Helpful", use_container_width=True):
        score_response(st.session_state.trace_id, "user-feedback", 0.0, "Thumbs down")
        st.warning("Feedback recorded.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask about policies, tasks, or paste your offer letter...")

if "pending_prompt" in st.session_state:
    user_input = st.session_state.pending_prompt
    del st.session_state.pending_prompt

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    span = st.session_state.trace.span(
        name="agent-turn",
        input={"message": user_input},
        metadata={"employee_id": st.session_state.employee_id},
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                processor = LangfuseTracingProcessor(span, langfuse_client=langfuse, user_input=user_input)
                set_trace_processors([processor])

                result = asyncio.run(
                    Runner.run(
                        orchestrator_agent,
                        input=st.session_state.conversation_history,
                    )
                )

                response_text = result.final_output
                span.end(output={"response": response_text}, level="DEFAULT")
                st.session_state.trace.update(
                    input=user_input,
                    output=response_text,
                )
                st.session_state.conversation_history = result.to_input_list()
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.markdown(response_text)

            except Exception as e:
                error_msg = f"Something went wrong: {str(e)}"
                span.end(output={"error": str(e)}, level="ERROR")
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.error(error_msg)

    set_trace_processors([])
    
    # Add delay to ensure traces are flushed before Streamlit reruns
    time.sleep(0.5)
    
    try:
        flush()
        logger.info("✅ Traces flushed successfully in app.py")
    except Exception as e:
        logger.error(f"❌ Failed to flush traces: {str(e)}")
        st.error(f"Warning: Could not flush traces to Langfuse. Check your credentials.")
