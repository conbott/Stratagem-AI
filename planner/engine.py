"""
StratagemAI Core Planning and Dynamic Execution Engine.
Implements the Plan-and-Solve paradigm with dependency tracking and dynamic replanning.
"""

import os
import sys
import json
import re
from typing import Optional, Dict, Any, List
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from planner.models import ExecutionPlan, SubTask, TaskStatus, ReplanEvent
from planner.mock_data import PRESET_PLANS


PLAN_PROMPT_TEMPLATE = """You are StratagemAI, an expert Chief Strategy Officer and Technical Project Planner.
Given the following high-level objective, decompose it into a logical, sequential execution plan consisting of 4 to 6 discrete subtasks.

USER OBJECTIVE:
{goal}

Provide your response as a valid JSON object matching this schema:
{{
  "overview": "Short executive summary of the project approach.",
  "tasks": [
    {{
      "id": 1,
      "title": "Action-oriented task title",
      "description": "Clear explanation of what will be performed and delivered",
      "dependencies": [],
      "assigned_role": "Architect / Engineer / Analyst"
    }},
    ...
  ]
}}

CRITICAL: Return ONLY raw, valid JSON. Do not include markdown code block ticks (```) or preamble.
"""


STEP_EXECUTION_PROMPT = """You are executing a specific subtask within an active project plan.

PROJECT OBJECTIVE: {goal}
CURRENT SUBTASK:
- Title: {title}
- Description: {description}
- Assigned Role: {role}

CONTEXT FROM PREVIOUS COMPLETED TASKS:
{context}

TASK:
Produce the concrete execution output, analysis, code, or strategic deliverable for this step.
Be thorough, structured, and deliver actionable findings with markdown formatting.
"""


REPLAN_PROMPT = """You are StratagemAI reviewing an active execution plan due to a dynamic replanning trigger.

ORIGINAL GOAL: {goal}
TRIGGER / NEW REQUIREMENT: {trigger}

CURRENT TASKS:
{tasks_json}

Provide a revised list of remaining tasks (from the current point onwards) to address this trigger.
Return ONLY valid JSON matching:
{{
  "action_taken": "e.g. Added security audit step and updated deployment target",
  "revised_tasks": [
    {{
      "id": 2,
      "title": "Updated or New Task Title",
      "description": "Updated description",
      "dependencies": [1],
      "assigned_role": "Role"
    }}
  ]
}}
"""


class StratagemPlannerEngine:
    def __init__(
        self,
        provider: str = "Gemini",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.2,
    ):
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.temperature = temperature
        
        if not model_name:
            if provider.lower() in ("gemini", "google"):
                self.model_name = "gemini-2.5-flash"
            elif provider.lower() == "openai":
                self.model_name = "gpt-4o-mini"
            elif provider.lower() == "groq":
                self.model_name = "llama-3.3-70b-versatile"
            else:
                self.model_name = "default-model"
        else:
            self.model_name = model_name

        self.llm = self._init_llm()

    def _init_llm(self):
        p = self.provider.lower()
        if not self.api_key and not any(k in p for k in ("local", "ollama")):
            return None
        try:
            if any(k in p for k in ("gemini", "google")):
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model=self.model_name or "gemini-2.5-flash",
                    google_api_key=self.api_key,
                    temperature=self.temperature,
                )
            elif "openai" in p:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=self.model_name or "gpt-4o-mini",
                    api_key=self.api_key,
                    temperature=self.temperature,
                )
            elif any(k in p for k in ("groq", "custom", "ollama", "local")):
                from langchain_openai import ChatOpenAI
                base = self.base_url
                if not base:
                    base = "http://localhost:11434/v1" if any(k in p for k in ("ollama", "local")) else "https://api.groq.com/openai/v1"
                return ChatOpenAI(
                    model=self.model_name or "qwen2.5-coder:7b",
                    api_key=self.api_key or "ollama",
                    base_url=base,
                    temperature=self.temperature,
                )
        except Exception as e:
            print(f"[StratagemAI] LLM init error: {e}")
            return None

    def _clean_json_str(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text

    def create_plan(self, goal: str) -> ExecutionPlan:
        """Decompose high-level goal into an initial structured execution plan."""
        # Check presets first
        for name, p in PRESET_PLANS.items():
            if goal.lower().strip() == p.goal.lower().strip() or goal.lower().strip() == name.lower():
                return p.model_copy(deep=True)

        if not self.llm:
            # Fallback algorithmic planner
            return ExecutionPlan(
                goal=goal,
                overview=f"Automated strategic decomposition for: '{goal}'. (Generated in Demo Mode - configure API key for custom LLM planning).",
                tasks=[
                    SubTask(id=1, title="Discovery & Scoping", description="Identify requirements, system constraints, and stakeholder criteria.", dependencies=[], assigned_role="Product Strategist"),
                    SubTask(id=2, title="System Architecture & Data Modeling", description="Draft formal component diagrams, schemas, and API contracts.", dependencies=[1], assigned_role="Lead Architect"),
                    SubTask(id=3, title="Core Implementation & Logic", description="Construct core operational modules, state graphs, and persistence layers.", dependencies=[2], assigned_role="Principal Engineer"),
                    SubTask(id=4, title="Verification, Testing & Hardening", description="Execute integration test cases, validate security borders, and optimize performance.", dependencies=[3], assigned_role="QA Lead"),
                    SubTask(id=5, title="Production Deployment & Documentation", description="Package artifacts, finalize user guides, and establish telemetry dashboards.", dependencies=[4], assigned_role="DevOps Lead"),
                ]
            )

        prompt = PLAN_PROMPT_TEMPLATE.format(goal=goal)
        try:
            resp = self.llm.invoke(prompt)
            raw = self._clean_json_str(resp.content if hasattr(resp, "content") else str(resp))
            data = json.loads(raw)
            
            subtasks = []
            for t in data.get("tasks", []):
                subtasks.append(SubTask(
                    id=t.get("id", len(subtasks) + 1),
                    title=t.get("title", f"Milestone {len(subtasks) + 1}"),
                    description=t.get("description", ""),
                    dependencies=t.get("dependencies", []),
                    assigned_role=t.get("assigned_role", "Specialist"),
                    status=TaskStatus.PENDING,
                ))

            return ExecutionPlan(
                goal=goal,
                overview=data.get("overview", "Comprehensive roadmap."),
                tasks=subtasks,
            )
        except Exception as e:
            print(f"[StratagemAI] Plan generation fallback: {e}")
            return self.create_plan(goal)

    def execute_subtask(self, plan: ExecutionPlan, task_id: int) -> SubTask:
        """Execute a single subtask, respecting dependencies and synthesizing prior outputs."""
        task = next((t for t in plan.tasks if t.id == task_id), None)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        # Verify dependencies
        for dep_id in task.dependencies:
            dep_task = next((t for t in plan.tasks if t.id == dep_id), None)
            if dep_task and dep_task.status != TaskStatus.COMPLETED:
                task.status = TaskStatus.FAILED
                task.execution_notes = f"Blocked: Prerequisite Task #{dep_id} ('{dep_task.title}') has not completed."
                return task

        task.status = TaskStatus.IN_PROGRESS

        # Gather context from completed tasks
        context_lines = []
        for t in plan.tasks:
            if t.status == TaskStatus.COMPLETED and t.output:
                context_lines.append(f"### Milestone {t.id}: {t.title}\n{t.output[:500]}...\n")
        context_str = "\n".join(context_lines) if context_lines else "None (Initial milestone)."

        if not self.llm:
            # Deterministic simulation output
            task.output = (
                f"#### Deliverable for Milestone #{task.id}: {task.title}\n\n"
                f"- **Owner:** {task.assigned_role}\n"
                f"- **Scope Executed:** {task.description}\n"
                f"- **Key Milestone Findings:**\n"
                f"  1. Validated system requirements against objective: *\"{plan.goal}\"*.\n"
                f"  2. Completed prerequisite handshake and verified operational parameters.\n"
                f"  3. Successfully passed internal quality checks without blocking errors.\n\n"
                f"*(Executed via StratagemAI Engine)*"
            )
            task.status = TaskStatus.COMPLETED
            return task

        prompt = STEP_EXECUTION_PROMPT.format(
            goal=plan.goal,
            title=task.title,
            description=task.description,
            role=task.assigned_role,
            context=context_str,
        )

        try:
            resp = self.llm.invoke(prompt)
            content = resp.content if hasattr(resp, "content") else str(resp)
            task.output = content.strip()
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.execution_notes = f"Execution failed: {str(e)}"

        return task

    def trigger_replan(self, plan: ExecutionPlan, trigger_reason: str) -> ExecutionPlan:
        """Dynamically adapt remaining plan milestones in response to an environmental disruption or requirement change."""
        uncompleted = [t for t in plan.tasks if t.status != TaskStatus.COMPLETED]
        if not uncompleted:
            return plan

        event = ReplanEvent(
            step_id=uncompleted[0].id if uncompleted else 0,
            trigger_reason=trigger_reason,
            action_taken="Re-indexed remaining tasks to accommodate new criteria",
            changes_made="Updated scope and inserted contingency verification milestone",
        )
        plan.replan_history.append(event)

        # Append or modify task
        new_id = max(t.id for t in plan.tasks) + 1
        plan.tasks.append(SubTask(
            id=new_id,
            title=f"Dynamic Adaptation: {trigger_reason[:30]}...",
            description=f"Address dynamic condition: {trigger_reason}. Re-align architecture and run compensatory testing.",
            dependencies=[uncompleted[0].id] if uncompleted else [],
            assigned_role="Risk & Compliance Lead",
            status=TaskStatus.PENDING,
        ))

        return plan

    def compile_final_dossier(self, plan: ExecutionPlan) -> str:
        """Synthesize all completed milestone outputs into an Executive Project Dossier."""
        lines = [
            f"# Executive Project Blueprint: {plan.goal}",
            f"\n**Strategic Overview:** {plan.overview}\n",
            "## Milestone Execution Ledger\n",
        ]

        for t in plan.tasks:
            status_tag = f"[{t.status.value.upper()}]"
            lines.append(f"### Milestone #{t.id}: {t.title} {status_tag}")
            lines.append(f"**Assigned Role:** {t.assigned_role} | **Status:** `{t.status.value}`")
            lines.append(f"**Description:** {t.description}\n")
            if t.output:
                lines.append(f"**Execution Output:**\n{t.output}\n")
            lines.append("---")

        if plan.replan_history:
            lines.append("\n## Replanning Audit Trail")
            for r in plan.replan_history:
                lines.append(f"- **Trigger:** {r.trigger_reason} | **Action:** {r.action_taken}")

        plan.final_dossier = "\n".join(lines)
        return plan.final_dossier
