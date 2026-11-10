"""
Pydantic Models and Data Schemas for StratagemAI Planning Engine.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class SubTask(BaseModel):
    id: int = Field(description="Unique incremental integer ID for the task step.")
    title: str = Field(description="Concise action-oriented title of the milestone.")
    description: str = Field(description="Detailed objective, criteria of completion, and deliverables.")
    dependencies: List[int] = Field(default_factory=list, description="IDs of preceding subtasks that must be completed.")
    assigned_role: str = Field(default="Specialist", description="Role archetype (e.g. Architect, Data Engineer, Reviewer).")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current lifecycle state.")
    output: Optional[str] = Field(default=None, description="Artifact or execution output produced by this step.")
    execution_notes: Optional[str] = Field(default=None, description="Observations, warnings, or replanning remarks.")


class ReplanEvent(BaseModel):
    step_id: int
    trigger_reason: str
    action_taken: str
    changes_made: str


class ExecutionPlan(BaseModel):
    goal: str
    overview: str
    tasks: List[SubTask] = Field(default_factory=list)
    replan_history: List[ReplanEvent] = Field(default_factory=list)
    final_dossier: Optional[str] = None
    status: str = "INITIALIZED"
