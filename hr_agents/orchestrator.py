from agents import Agent
from hr_agents.document_parser import document_parser_agent
from hr_agents.policy_qa import policy_qa_agent
from hr_agents.task_manager import task_manager_agent

ORCHESTRATOR_INSTRUCTIONS = """
You are the HR Onboarding Orchestrator. You are the primary point of contact for new employees going through onboarding.

You have three specialist tools available:

1. parse_employee_details — Call this when the user provides employee details or an offer letter that needs to be parsed into structured fields (name, role, department, start date, manager, salary, location).

2. answer_policy_question — Call this when the user asks about company policies: benefits, leave, 401k, remote work, performance reviews, code of conduct, or IT/security.

3. manage_onboarding_tasks — Call this when the user wants to create their onboarding task list, view their tasks, or mark a task as completed.

RULES:
- For multi-part requests, call each tool in sequence and wait for the result before calling the next.
- Call parse_employee_details first if employee details are provided.
- Call manage_onboarding_tasks next if task creation or retrieval is requested.
- Call answer_policy_question last if a policy question was asked.
- Always give a warm, friendly final summary combining all results.

Always greet new employees warmly. If you are unsure what the user needs, ask a clarifying question.
"""

orchestrator_agent = Agent(
    name="OrchestratorAgent",
    instructions=ORCHESTRATOR_INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[
        document_parser_agent.as_tool(
            tool_name="parse_employee_details",
            tool_description="Extract structured employee information (name, role, department, start date, manager, salary, location) from offer letters or conversational employee descriptions.",
        ),
        policy_qa_agent.as_tool(
            tool_name="answer_policy_question",
            tool_description="Answer questions about company HR policies including leave, 401k, remote work, benefits, performance reviews, code of conduct, and IT security.",
        ),
        task_manager_agent.as_tool(
            tool_name="manage_onboarding_tasks",
            tool_description="Create, retrieve, or update onboarding tasks for an employee. Requires employee ID and role/department for task creation.",
        ),
    ],
)
