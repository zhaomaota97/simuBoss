from typing import Literal

from pydantic import BaseModel, Field


AssetKind = Literal["knowledge", "template", "deliverable"]


class PlanTask(BaseModel):
    id: str
    title: str
    assignee_id: str = Field(alias="assigneeId")
    assignee_name: str = Field(default="", alias="assigneeName")
    task: str
    depends_on: list[str] = Field(default_factory=list, alias="dependsOn")
    reason: str = ""

    model_config = {"populate_by_name": True}


class ExecutionPlan(BaseModel):
    summary: str
    deliverable: str
    tasks: list[PlanTask]
    risks: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list, alias="openQuestions")

    model_config = {"populate_by_name": True}


class TimelineEvent(BaseModel):
    stage: str
    actor: str
    message: str


class WorkerResult(BaseModel):
    task_id: str
    assignee_id: str
    assignee_name: str
    title: str
    result: str
    depends_on: list[str] = Field(default_factory=list)


class RuntimeTaskRequest(BaseModel):
    task: str
    manager_id: str = Field(default="manager-root", alias="managerId")
    manager_name: str = Field(default="默认经理", alias="managerName")
    approved_plan: ExecutionPlan | None = Field(default=None, alias="approvedPlan")
    context: dict = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class RuntimeTaskResponse(BaseModel):
    status: Literal["completed", "failed"]
    root_task: str = Field(alias="rootTask")
    plan: ExecutionPlan
    timeline: list[TimelineEvent]
    worker_results: list[WorkerResult] = Field(alias="workerResults")
    final_result: str = Field(alias="finalResult")

    model_config = {"populate_by_name": True}
