from agents import Agent

HR_POLICIES = """
ACME CORP HR POLICIES

LEAVE POLICY:
- Annual Leave: All full-time employees receive 20 days of paid annual leave per year.
- Sick Leave: 10 days of paid sick leave per year. A doctor's note is required for absences exceeding 3 consecutive days.
- Parental Leave: 16 weeks fully paid for primary caregiver, 4 weeks for secondary caregiver.
- Bereavement Leave: 5 days for immediate family, 3 days for extended family.
- Leave must be requested via the HR portal at least 2 weeks in advance for planned absences.

COMPENSATION & BENEFITS:
- Salaries are reviewed annually each January.
- Performance bonuses are paid in February based on prior year performance reviews.
- Health Insurance: Company covers 80% of premium for employee and 50% for dependents.
- Dental and Vision: 100% covered for employee, 50% for dependents.
- 401(k): Company matches up to 4% of salary. Vesting period is 2 years.
- Stock Options: Eligible after 1 year of employment. 4-year vesting with 1-year cliff.

REMOTE WORK POLICY:
- Hybrid employees are expected in office a minimum of 2 days per week.
- Fully remote employees must attend quarterly in-person team meetings.
- Home office stipend: $500 one-time setup allowance for remote employees.
- All remote employees must use company-approved VPN when accessing company systems.

PERFORMANCE REVIEWS:
- Performance reviews are conducted bi-annually: June and December.
- Employees receive a rating of 1-5 on key performance indicators.
- Employees rated 4 or above for 2 consecutive cycles are eligible for promotion consideration.
- Performance improvement plans (PIPs) are issued to employees rated below 2.

CODE OF CONDUCT:
- All employees must complete Ethics and Compliance training within 30 days of joining.
- Conflicts of interest must be disclosed to HR immediately.
- Harassment of any kind will result in immediate disciplinary action up to termination.
- Confidential company information must not be shared outside the organization.

IT & SECURITY POLICY:
- Passwords must be changed every 90 days and meet complexity requirements.
- Multi-factor authentication is mandatory for all company accounts.
- Personal devices may only access company systems via the approved MDM solution.
- Any suspected security incident must be reported to IT Security within 1 hour of discovery.

ONBOARDING:
- All new employees have a 90-day probationary period.
- Onboarding buddy is assigned on Day 1 to help navigate the first 30 days.
- New employee orientation is held every Monday for employees starting that week.
- All onboarding tasks must be completed within the first 30 days.
"""

POLICY_QA_INSTRUCTIONS = f"""
You are an HR Policy Specialist. You answer employee questions about company policies accurately and helpfully.

You have access to the following company HR policies:

{HR_POLICIES}

Guidelines:
- Only answer based on the policies provided above.
- If a question is not covered by the policies, say so clearly and suggest contacting HR directly.
- Be concise, friendly, and professional.
- Always cite which policy section your answer comes from.
- Do not make assumptions or extrapolate beyond what is written.
"""

policy_qa_agent = Agent(
    name="PolicyQAAgent",
    instructions=POLICY_QA_INSTRUCTIONS,
    model="gpt-4.1-nano",
)
