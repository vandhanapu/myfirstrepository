from datetime import datetime, timezone
from agents.tracing import TracingProcessor
import logging

logger = logging.getLogger(__name__)


class LangfuseTracingProcessor(TracingProcessor):
    def __init__(self, langfuse_parent, langfuse_client=None, user_input: str = ""):
        self._parent = langfuse_parent
        self._obs_map = {}
        self._user_input = user_input
        self._last_output = {}
        self._langfuse_client = langfuse_client
        logger.debug("LangfuseTracingProcessor initialized")

    def _get_parent(self, span):
        parent_id = span.parent_id
        if parent_id and parent_id in self._obs_map:
            return self._obs_map[parent_id]
        return self._parent

    def on_trace_start(self, trace):
        pass

    def on_trace_end(self, trace):
        pass

    def on_span_start(self, span):
        data = span.span_data
        parent = self._get_parent(span)
        span_name = data.name if hasattr(data, 'name') else 'unnamed'
        logger.info(f"📍 Span START: type={data.type}, name={span_name}, id={span.span_id}")

        if data.type == "agent":
            is_root = span.parent_id not in self._obs_map
            agent_input = {"message": self._user_input} if is_root and self._user_input else {"name": data.name}
            obs = parent.span(
                name=f"agent:{data.name}",
                input=agent_input,
            )
            logger.debug(f"  → Created agent span: agent:{data.name}")
        elif data.type == "response":
            obs = parent.generation(
                name="llm-response",
                input=data.input,
            )
            logger.debug(f"  → Created generation: llm-response")
        elif data.type == "handoff":
            obs = parent.span(
                name="handoff",
                input={"from_agent": data.from_agent, "to_agent": data.to_agent},
            )
            logger.debug(f"  → Created handoff span")
        elif data.type == "function":
            obs = parent.span(name=f"tool:{data.name}")
            logger.debug(f"  → Created tool span: tool:{data.name}")
        elif data.type == "generation":
            obs = parent.generation(
                name="llm-call",
                model=data.model,
                model_parameters=dict(data.model_config) if data.model_config else None,
                input=data.input,
            )
            logger.debug(f"  → Created generation: llm-call (model={data.model})")
        else:
            obs = parent.span(name=data.type)
            logger.debug(f"  → Created span: {data.type}")

        self._obs_map[span.span_id] = obs

    def on_span_end(self, span):
        obs = self._obs_map.pop(span.span_id, None)
        if not obs:
            logger.warning(f"⚠️ Observation not found for span {span.span_id}")
            return

        data = span.span_data
        span_name = data.name if hasattr(data, 'name') else 'unnamed'
        logger.info(f"✓ Span END: type={data.type}, name={span_name}, id={span.span_id}")

        if data.type == "response" and data.response:
            resp = data.response
            usage = None
            if hasattr(resp, "usage") and resp.usage:
                usage = {
                    "input": resp.usage.input_tokens,
                    "output": resp.usage.output_tokens,
                }
            output_text = None
            if resp.output:
                try:
                    output_text = [item.model_dump() for item in resp.output]
                except Exception:
                    output_text = str(resp.output)
            if span.parent_id:
                self._last_output[span.parent_id] = output_text
            obs.end(model=resp.model, output=output_text, usage=usage)

        elif data.type == "generation":
            usage = None
            if data.usage:
                usage = {
                    "input": data.usage.get("input_tokens", 0),
                    "output": data.usage.get("output_tokens", 0),
                }
            obs.end(output=data.output, usage=usage)

        elif data.type == "function":
            obs.update(input={"input": data.input} if data.input else None)
            obs.end(output={"output": str(data.output) if data.output else None})

        elif data.type == "agent":
            last_output = self._last_output.pop(span.span_id, None)
            obs.end(
                end_time=datetime.now(timezone.utc),
                output={"output": last_output} if last_output else None,
            )

        else:
            obs.end(end_time=datetime.now(timezone.utc))

    def shutdown(self):
        """Shutdown the processor and flush pending traces."""
        logger.info("Shutting down LangfuseTracingProcessor")
        self.force_flush()

    def force_flush(self):
        """Force flush all pending observations to Langfuse."""
        if self._langfuse_client:
            try:
                logger.info(f"Force flushing {len(self._obs_map)} pending observations to Langfuse")
                self._langfuse_client.flush()
                logger.info("✅ Force flush completed successfully")
            except Exception as e:
                logger.error(f"❌ Error during force flush: {str(e)}")
                raise
        else:
            logger.warning("Langfuse client not available for force flush")
