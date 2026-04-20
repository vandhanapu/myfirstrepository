from agents import Agent, function_tool
from tools.task_tools import create_onboarding_tasks, get_task_list, update_task_status


@function_tool
def tool_create_onboarding_tasks(employee_id: str, role: str, department: str) -> str:
    """Create a personalized onboarding task list for a new employee based on their role and department."""
    return create_onboarding_tasks(employee_id, role, department)


@function_tool
def tool_get_task_list(employee_id: str) -> str:
    """Retrieve the current onboarding task list and completion status for an employee."""
    return get_task_list(employee_id)


@function_tool
def tool_update_task_status(employee_id: str, task_title: str, status: str) -> str:
    """Update the completion status of a specific onboarding task. Status must be 'pending' or 'completed'."""
    return update_task_status(employee_id, task_title, status)


TASK_MANAGER_INSTRUCTIONS = """
You are an Onboarding Task Manager. You help new employees track and manage their onboarding checklist.

You can:
- Create a personalized onboarding task list based on the employee's role and department
- Retrieve the current status of all onboarding tasks
- Mark tasks as completed when the employee reports finishing them

Always confirm task creation with a summary. When showing tasks, group them by status (pending vs completed).
Be encouraging and supportive — starting a new job can be overwhelming.
"""

task_manager_agent = Agent(
    name="TaskManagerAgent",
    instructions=TASK_MANAGER_INSTRUCTIONS,
    model="gpt-4.1-nano",
    tools=[tool_create_onboarding_tasks, tool_get_task_list, tool_update_task_status],
)
