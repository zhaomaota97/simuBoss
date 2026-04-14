from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas.runtime import ExecutionPlan, PlanTask, RuntimeTaskRequest
from app.services.json_utils import extract_json_object
from app.services.llm_client import deepseek_client


class GraphState(TypedDict):
    request: RuntimeTaskRequest
    plan: ExecutionPlan
    timeline: list[dict]
    worker_results: list[dict]
    final_result: str


def _default_plan_for(task: str, manager_name: str) -> ExecutionPlan:
    return ExecutionPlan(
        summary=f"目标是完成“{task}”，并以最小必要复杂度推进执行。",
        deliverable=f"针对“{task}”的最终交付结果。",
        tasks=[
            PlanTask(
                id="t1",
                title=task,
                assigneeId="worker-default",
                assigneeName=manager_name,
                task=f"直接完成“{task}”，并整理结果。",
                dependsOn=[],
                reason="默认兜底计划：由单个执行单元完成。",
            )
        ],
        risks=[],
        openQuestions=[],
    )


async def planner_node(state: GraphState) -> GraphState:
    request = state["request"]
    if request.approved_plan:
        timeline = state["timeline"] + [
            {
                "stage": "planner",
                "actor": request.manager_name,
                "message": f"已接收审批通过的计划，共 {len(request.approved_plan.tasks)} 个子任务。",
            }
        ]
        return {
            **state,
            "plan": request.approved_plan,
            "timeline": timeline,
        }

    system_prompt = (
        "你是一个严谨的团队经理。"
        "请把任务拆解为一个结构化执行计划。"
        "简单任务优先只拆成 1 个子任务，不要为了完整性过度拆解。"
        "你必须只输出 JSON 对象，不要输出 markdown、解释或代码块。"
    )
    user_prompt = f"""
总任务：{request.task}
经理：{request.manager_name}

请输出 JSON，字段结构必须为：
{{
  "summary": "目标理解",
  "deliverable": "最终交付物",
  "tasks": [
    {{
      "id": "t1",
      "title": "子任务标题",
      "assigneeId": "worker-1",
      "assigneeName": "执行者名称",
      "task": "要执行的具体内容",
      "dependsOn": [],
      "reason": "为什么分给他"
    }}
  ],
  "risks": [],
  "openQuestions": []
}}
"""
    try:
        raw = await deepseek_client.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        plan = ExecutionPlan.model_validate(extract_json_object(raw))
    except Exception:
        plan = _default_plan_for(request.task, request.manager_name)
        timeline = state["timeline"] + [
            {
                "stage": "planner_fallback",
                "actor": request.manager_name,
                "message": "计划生成失败，已退回到默认单任务计划。",
            }
        ]
        return {**state, "plan": plan, "timeline": timeline}

    timeline = state["timeline"] + [
        {
            "stage": "planner",
            "actor": request.manager_name,
            "message": f"已生成执行计划，共 {len(plan.tasks)} 个子任务。",
        }
    ]
    return {
        **state,
        "plan": plan,
        "timeline": timeline,
    }


async def worker_node(state: GraphState) -> GraphState:
    request = state["request"]
    plan = state["plan"]
    timeline = list(state["timeline"])
    worker_results: list[dict] = []
    deliveries_by_task_id: dict[str, str] = {}

    for task in plan.tasks:
        dependency_blocks = []
        for dependency_id in task.depends_on:
            dependency_result = deliveries_by_task_id.get(dependency_id)
            if dependency_result:
                dependency_blocks.append(f"- {dependency_id}: {dependency_result}")

        dependency_text = "\n".join(dependency_blocks) if dependency_blocks else "无前置依赖交付。"
        system_prompt = (
            "你是一名可靠的执行工人。"
            "请直接做事，不要向用户反问或索要额外信息。"
            "在信息不足时，做出最合理的假设并继续推进。"
            "输出最终执行结果正文。"
        )
        user_prompt = f"""
总任务：{request.task}
当前子任务：{task.title}
执行人：{task.assignee_name or task.assignee_id}
任务说明：
{task.task}

前置依赖交付：
{dependency_text}

请直接完成当前子任务，并输出你的交付结果。
"""

        timeline.append(
            {
                "stage": "worker",
                "actor": task.assignee_name or task.assignee_id,
                "message": f"开始执行 {task.id} - {task.title}",
            }
        )
        result_text = await deepseek_client.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )
        deliveries_by_task_id[task.id] = result_text
        worker_results.append(
            {
                "task_id": task.id,
                "assignee_id": task.assignee_id,
                "assignee_name": task.assignee_name or task.assignee_id,
                "title": task.title,
                "result": result_text,
                "depends_on": task.depends_on,
            }
        )
        timeline.append(
            {
                "stage": "worker_done",
                "actor": task.assignee_name or task.assignee_id,
                "message": f"已完成 {task.id} - {task.title}",
            }
        )

    return {
        **state,
        "timeline": timeline,
        "worker_results": worker_results,
    }


async def synthesizer_node(state: GraphState) -> GraphState:
    request = state["request"]
    plan = state["plan"]
    worker_results = state["worker_results"]

    result_lines = []
    for item in worker_results:
        result_lines.append(
            f"子任务：{item['title']}\n执行人：{item['assignee_name']}\n交付：{item['result']}"
        )

    system_prompt = (
        "你是一名负责最终汇总交付的经理。"
        "请基于子任务结果整理成一份清晰、可直接交付给上级的最终结果。"
        "不要重复无关解释。"
    )
    user_prompt = f"""
总任务：{request.task}
计划摘要：{plan.summary}
目标交付：{plan.deliverable}

子任务执行结果：
{chr(10).join(result_lines)}

请输出最终交付内容。
"""
    final_result = await deepseek_client.chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.2,
    )
    timeline = state["timeline"] + [
        {
            "stage": "synthesizer",
            "actor": request.manager_name,
            "message": "已汇总全部子任务结果并生成最终交付。",
        }
    ]
    return {
        **state,
        "timeline": timeline,
        "final_result": final_result,
    }


def build_task_graph():
    graph = StateGraph(GraphState)
    graph.add_node("planner", planner_node)
    graph.add_node("workers", worker_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "workers")
    graph.add_edge("workers", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()
