# HR Onboarding Assistant — Project Reference

## Overview
Demonstrates agent orchestration, tracing, monitoring, and observability using OpenAI Agents SDK and Langfuse.

---

## Tech Stack
| Tool | Purpose |
|------|---------|
| OpenAI Agents SDK (`openai-agents`) | Multi-agent orchestration (agents-as-tools pattern) |
| Langfuse (`<3.0.0`) | Tracing, monitoring, observability, scoring |
| OpenAI GPT-4o-mini | Orchestrator LLM |
| OpenAI GPT-4.1-nano | Specialist agent LLMs |
| Streamlit | Web UI |
| Python 3.11+ | Runtime |
| python-dotenv | Environment variable management |
| pydantic | Task data model |

---

## Project Structure
```
Trace/
├── hr_agents/
│   ├── __init__.py
│   ├── orchestrator.py       ← Routes user queries to specialist agents via .as_tool()
│   ├── document_parser.py    ← Extracts structured data from HR documents
│   ├── policy_qa.py          ← Answers HR policy questions (policies embedded in prompt)
│   └── task_manager.py       ← Creates and tracks onboarding tasks
├── tools/
│   ├── __init__.py
│   └── task_tools.py         ← Task CRUD functions backed by in-memory dict
├── tracing/
│   ├── __init__.py
│   ├── langfuse_setup.py     ← Langfuse client init, score_response, flush helpers
│   └── langfuse_processor.py ← Custom TracingProcessor bridging OpenAI SDK → Langfuse
├── app.py                    ← Streamlit web interface
├── main.py                   ← CLI interface for terminal testing
├── requirements.txt
├── Dockerfile                ← Container image definition for Streamlit app
├── docker-compose.yml        ← Local container orchestration for app runtime
├── .dockerignore             ← Excludes local/virtualenv files from Docker build context
├── .env.example              ← Copy to .env and fill in keys
└── PROJECT_REFERENCE.md      ← This file
```

---

## Agent Architecture

The orchestrator uses the **agents-as-tools** pattern (`.as_tool()`), not handoffs.
Each specialist agent is exposed as a named tool the orchestrator can call.

```
User Input
    └── OrchestratorAgent (gpt-4o-mini)
          ├── tool: parse_employee_details  → DocumentParserAgent (gpt-4.1-nano)
          │     └── Extracts: name, role, dept, start date, manager, salary, location
          ├── tool: answer_policy_question  → PolicyQAAgent (gpt-4.1-nano)
          │     └── Answers from HR policies embedded in system prompt
          └── tool: manage_onboarding_tasks → TaskManagerAgent (gpt-4.1-nano)
                ├── tool: tool_create_onboarding_tasks
                ├── tool: tool_get_task_list
                └── tool: tool_update_task_status
                
```

### Orchestrator tool names
| Tool name | Description |
|-----------|-------------|
| `parse_employee_details` | Extract structured employee info from offer letters |
| `answer_policy_question` | Answer leave, 401k, remote work, benefits, IT policy questions |
| `manage_onboarding_tasks` | Create, view, or update onboarding tasks for an employee |

### Task storage
Tasks are stored in an **in-memory dict** (`_task_store` in `tools/task_tools.py`).
Role-specific tasks exist for: `engineering`, `sales`, `hr`. All other departments get base tasks only.

---

## Tracing Architecture

### Two-layer tracing approach
1. **Langfuse Trace + Span** (manual) — created in `app.py` / `main.py` per session and per agent turn
2. **`LangfuseTracingProcessor`** (custom) — hooks into OpenAI Agents SDK's `TracingProcessor` interface via `set_trace_processors()`, bridges all internal SDK spans (agent, response, function, handoff, generation) into Langfuse observations nested under the active span

### `LangfuseTracingProcessor` span mapping
| SDK span type | Langfuse observation |
|--------------|----------------------|
| `agent` | `span` named `agent:<name>` |
| `response` | `generation` named `llm-response` (captures token usage) |
| `generation` | `generation` named `llm-call` (captures model + usage) |
| `function` | `span` named `tool:<name>` (captures input/output) |
| `handoff` | `span` named `handoff` (from/to agent) |

### Observability coverage
- Each user session → Langfuse **Trace** with `user_id` and `session_type` metadata
- Each user message → **Span** (`agent-turn`) capturing input, output, and employee_id
- All internal agent/tool activity → nested observations via `LangfuseTracingProcessor`
- Errors → span ended with `level="ERROR"` and error string in output
- User feedback → Langfuse **Score** (`user-feedback`: 1.0 thumbs up, 0.0 thumbs down)
- Token usage → captured automatically from `response.usage` in the processor

---

## Setup Instructions

### 1. Create virtual environment
```bash
python -m venv venv
```

### 2. Activate virtual environment
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
# Then edit .env with your API keys
```

### 5. Get API Keys
- **OpenAI:** https://platform.openai.com/api-keys
- **Langfuse:** https://cloud.langfuse.com → Create account → Project → Settings → API Keys

### 6. Run the app
```bash
# Streamlit UI (recommended for demo)
streamlit run app.py

# CLI mode (for testing)
python main.py
```

### 7. Run with Docker
```bash
# Build and run with Docker Compose
docker compose up --build

# Stop containers
docker compose down
```

Then open: http://localhost:8501

---

## Key Learning Concepts Covered

1. **Agents-as-tools pattern** — Specialist agents exposed via `.as_tool()`, orchestrator calls them like function tools
2. **Custom TracingProcessor** — `LangfuseTracingProcessor` implements the SDK's `TracingProcessor` interface to capture all internal spans
3. **Two-layer observability** — Outer manual trace/span in app code + inner automatic spans from the SDK processor
4. **Function tools** — Task manager uses `@function_tool` decorated functions backed by in-memory storage
5. **Session tracking** — Each session has a unique trace with `user_id`; conversation history passed as input list
6. **Error observability** — Errors end the span with `level="ERROR"` and are visible in Langfuse
7. **User feedback loop** — Scores submitted from Streamlit sidebar linked to the session trace
8. **Multi-turn conversation** — `result.to_input_list()` preserves conversation history across turns

---

## Sample Interactions to Demo

### Document Parsing
```
Offer Letter for Sarah Johnson
Role: Software Engineer
Department: Engineering
Start Date: 2026-04-01
Manager: David Chen
Annual Salary: $120,000
Location: Hybrid (New York Office)
```

### Policy Questions
- "How many vacation days do I get per year?"
- "What is the remote work policy?"
- "How does the 401k matching work?"
- "What happens if I get sick for more than 3 days?"

### Task Management
- "Create my onboarding tasks. My ID is EMP001, I am a Software Engineer in Engineering."
- "Show me my onboarding tasks for EMP001"
- "Mark the Set up company email task as completed for EMP001"

---

## Langfuse Dashboard — What to Show Students
1. **Traces tab** — list of all sessions, click into any to see full trace tree
2. **Span details** — `agent-turn` span wraps all nested agent/tool/generation observations
3. **Generation observations** — model name, input/output, token usage per LLM call
4. **Scores tab** — filter traces by `user-feedback` score (1.0 / 0.0)
5. **Users tab** — per-employee session history (keyed by auto-generated `employee_id`)

---

## Potential Extensions (Advanced)
- Add LLM-as-judge scoring to automatically evaluate policy answer quality
- Replace in-memory `_task_store` with a real database (SQLite or Postgres)
- Upload real PDF HR documents and use OpenAI file_search tool
- Add a Langfuse prompt management integration
- Add multi-turn memory with thread persistence
- Deploy to AWS/GCP with a proper database for task storage
