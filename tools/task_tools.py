from pydantic import BaseModel
import json

_task_store: dict[str, list[dict]] = {}


class Task(BaseModel):
    employee_id: str
    title: str
    description: str
    due_day: int
    status: str = "pending"


def create_onboarding_tasks(employee_id: str, role: str, department: str) -> str:
    base_tasks = [
        {"title": "Complete I-9 Form", "description": "Submit identity verification documents to HR", "due_day": 1, "status": "pending"},
        {"title": "Set up company email", "description": "Configure your company email account and signature", "due_day": 1, "status": "pending"},
        {"title": "Review Employee Handbook", "description": "Read the full employee handbook and acknowledge receipt", "due_day": 3, "status": "pending"},
        {"title": "Complete Security Training", "description": "Finish mandatory cybersecurity awareness training", "due_day": 5, "status": "pending"},
        {"title": "Meet with Manager", "description": "30-minute intro meeting with your direct manager", "due_day": 2, "status": "pending"},
        {"title": "Enroll in Benefits", "description": "Select health, dental, and vision coverage options", "due_day": 7, "status": "pending"},
        {"title": "Set up 2FA", "description": "Enable two-factor authentication on all company accounts", "due_day": 1, "status": "pending"},
    ]

    role_tasks = {
        "engineering": [
            {"title": "Request dev environment access", "description": "Submit IT ticket for repo and cloud access", "due_day": 2, "status": "pending"},
            {"title": "Complete code review walkthrough", "description": "Pair with senior engineer on first PR review", "due_day": 5, "status": "pending"},
        ],
        "sales": [
            {"title": "CRM system training", "description": "Complete Salesforce onboarding module", "due_day": 3, "status": "pending"},
            {"title": "Shadow a sales call", "description": "Observe a live customer call with your team lead", "due_day": 5, "status": "pending"},
        ],
        "hr": [
            {"title": "HRIS system access", "description": "Get credentials for the HR Information System", "due_day": 2, "status": "pending"},
            {"title": "Review compliance policies", "description": "Read all HR compliance and data protection policies", "due_day": 4, "status": "pending"},
        ],
    }

    tasks = base_tasks + role_tasks.get(department.lower(), [])
    _task_store[employee_id] = tasks

    return json.dumps({
        "employee_id": employee_id,
        "role": role,
        "department": department,
        "total_tasks": len(tasks),
        "tasks": tasks,
    })


def get_task_list(employee_id: str) -> str:
    tasks = _task_store.get(employee_id, [])
    if not tasks:
        return json.dumps({"error": f"No tasks found for employee {employee_id}"})

    pending = [t for t in tasks if t["status"] == "pending"]
    completed = [t for t in tasks if t["status"] == "completed"]

    return json.dumps({
        "employee_id": employee_id,
        "total": len(tasks),
        "completed": len(completed),
        "pending": len(pending),
        "tasks": tasks,
    })


def update_task_status(employee_id: str, task_title: str, status: str) -> str:
    tasks = _task_store.get(employee_id, [])
    if not tasks:
        return json.dumps({"error": f"No tasks found for employee {employee_id}"})

    for task in tasks:
        if task["title"].lower() == task_title.lower():
            task["status"] = status
            _task_store[employee_id] = tasks
            return json.dumps({"success": True, "task": task_title, "new_status": status})

    return json.dumps({"error": f"Task '{task_title}' not found"})
