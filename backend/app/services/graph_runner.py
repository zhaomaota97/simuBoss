import json
import traceback
from collections.abc import AsyncGenerator

from app.schemas.runtime import ExecutionPlan, PlanTask, RuntimeTaskRequest, RuntimeTaskResponse
from app.services.json_utils import extract_json_object
from app.services.llm_client import deepseek_client


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


class GraphRuntimeService:
    def _timeline_entry(self, stage: str, actor: str, message: str) -> dict:
        return {"stage": stage, "actor": actor, "message": message}

    def _is_direct_worker_execution(self, request: RuntimeTaskRequest) -> bool:
        return str(request.context.get("role", "")).lower() == "worker"

    def _default_plan_for(self, task: str, manager_name: str) -> ExecutionPlan:
        return ExecutionPlan(
            summary=f"执行任务：{task}",
            deliverable=f"完成“{task}”的交付结果",
            tasks=[
                PlanTask(
                    id="t1",
                    title=task,
                    assigneeId="worker-default",
                    assigneeName=manager_name,
                    task=task,
                    dependsOn=[],
                    reason="直接执行当前任务",
                )
            ],
            risks=[],
            openQuestions=[],
        )

    async def _build_plan(self, request: RuntimeTaskRequest, timeline: list[dict]) -> ExecutionPlan:
        if request.approved_plan:
            if not self._is_direct_worker_execution(request):
                timeline.append(
                    self._timeline_entry(
                        "planner",
                        request.manager_name,
                        f"已接收审批通过的计划，共 {len(request.approved_plan.tasks)} 个子任务。",
                    )
                )
            return request.approved_plan

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
            timeline.append(
                self._timeline_entry(
                    "planner",
                    request.manager_name,
                    f"已生成执行计划，共 {len(plan.tasks)} 个子任务。",
                )
            )
            return plan
        except Exception:
            plan = self._default_plan_for(request.task, request.manager_name)
            timeline.append(
                self._timeline_entry(
                    "planner_fallback",
                    request.manager_name,
                    "计划生成失败，已退回到默认单任务计划。",
                )
            )
            return plan

    async def _run_worker_task(
        self,
        request: RuntimeTaskRequest,
        task: PlanTask,
        dependency_text: str,
    ) -> str:
        return await deepseek_client.chat_completion(
            system_prompt=(
                "你是一名可靠的执行工人。"
                "请直接做事，不要向用户反问或索要额外信息。"
                "在信息不足时，做出最合理的假设并继续推进。"
                "输出最终执行结果正文。"
            ),
            user_prompt=f"""
总任务：{request.task}
当前子任务：{task.title}
执行人：{task.assignee_name or task.assignee_id}
任务说明：
{task.task}

前置依赖交付：
{dependency_text}

请直接完成当前子任务，并输出你的交付结果。
""",
            temperature=0.2,
        )

    async def _stream_worker_task(
        self,
        request: RuntimeTaskRequest,
        task: PlanTask,
        dependency_text: str,
    ) -> AsyncGenerator[str, None]:
        async for delta in deepseek_client.stream_chat_completion(
            system_prompt=(
                "你是一名可靠的执行工人。"
                "请直接做事，不要向用户反问或索要额外信息。"
                "在信息不足时，做出最合理的假设并继续推进。"
                "输出最终执行结果正文。"
            ),
            user_prompt=f"""
总任务：{request.task}
当前子任务：{task.title}
执行人：{task.assignee_name or task.assignee_id}
任务说明：
{task.task}

前置依赖交付：
{dependency_text}

请直接完成当前子任务，并输出你的交付结果。
""",
            temperature=0.2,
        ):
            yield delta

    async def _run_synthesizer(
        self,
        request: RuntimeTaskRequest,
        plan: ExecutionPlan,
        worker_results: list[dict],
    ) -> str:
        result_lines = [
            f"子任务：{item['title']}\n执行人：{item['assignee_name']}\n交付：{item['result']}"
            for item in worker_results
        ]
        return await deepseek_client.chat_completion(
            system_prompt=(
                "你是一名负责最终汇总交付的经理。"
                "请基于子任务结果整理成一份清晰、可直接交付给上级的最终结果。"
                "不要重复无关解释。"
            ),
            user_prompt=f"""
总任务：{request.task}
计划摘要：{plan.summary}
目标交付：{plan.deliverable}

子任务执行结果：
{chr(10).join(result_lines)}

请输出最终交付内容。
""",
            temperature=0.2,
        )

    async def execute(self, request: RuntimeTaskRequest) -> RuntimeTaskResponse:
        timeline = [self._timeline_entry("received", request.manager_name, f"收到任务：{request.task}")]
        plan = await self._build_plan(request, timeline)
        worker_results: list[dict] = []
        deliveries_by_task_id: dict[str, str] = {}

        for task in plan.tasks:
            dependency_blocks = []
            for dependency_id in task.depends_on:
                dependency_result = deliveries_by_task_id.get(dependency_id)
                if dependency_result:
                    dependency_blocks.append(f"- {dependency_id}: {dependency_result}")
            dependency_text = "\n".join(dependency_blocks) if dependency_blocks else "无前置依赖交付。"

            timeline.append(
                self._timeline_entry(
                    "worker",
                    task.assignee_name or task.assignee_id,
                    f"开始执行 {task.id} - {task.title}",
                )
            )
            result_text = await self._run_worker_task(request, task, dependency_text)
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
                self._timeline_entry(
                    "worker_done",
                    task.assignee_name or task.assignee_id,
                    f"已完成 {task.id} - {task.title}",
                )
            )

        if self._is_direct_worker_execution(request):
            final_result = worker_results[0]["result"] if worker_results else ""
        else:
            timeline.append(self._timeline_entry("synthesizer", request.manager_name, "开始汇总全部子任务结果。"))
            final_result = await self._run_synthesizer(request, plan, worker_results)
            timeline.append(self._timeline_entry("synthesizer_done", request.manager_name, "已汇总全部子任务结果并生成最终交付。"))

        return RuntimeTaskResponse(
            status="completed",
            rootTask=request.task,
            plan=plan,
            timeline=timeline,
            workerResults=worker_results,
            finalResult=final_result,
        )

    async def stream_execute(self, request: RuntimeTaskRequest) -> AsyncGenerator[str, None]:
        try:
            timeline: list[dict] = []
            worker_results: list[dict] = []
            deliveries_by_task_id: dict[str, str] = {}

            received = self._timeline_entry("received", request.manager_name, f"收到任务：{request.task}")
            timeline.append(received)
            yield _sse("timeline", {"entry": received})

            plan = await self._build_plan(request, timeline)
            yield _sse("plan", {"plan": plan.model_dump(by_alias=True)})
            if len(timeline) > 1:
                yield _sse("timeline", {"entry": timeline[-1]})

            for task in plan.tasks:
                dependency_blocks = []
                for dependency_id in task.depends_on:
                    dependency_result = deliveries_by_task_id.get(dependency_id)
                    if dependency_result:
                        dependency_blocks.append(f"- {dependency_id}: {dependency_result}")
                dependency_text = "\n".join(dependency_blocks) if dependency_blocks else "无前置依赖交付。"

                started = self._timeline_entry(
                    "worker",
                    task.assignee_name or task.assignee_id,
                    f"开始执行 {task.id} - {task.title}",
                )
                timeline.append(started)
                yield _sse("timeline", {"entry": started})

                result_text = ""
                if self._is_direct_worker_execution(request):
                    async for delta in self._stream_worker_task(request, task, dependency_text):
                        result_text += delta
                        yield _sse(
                            "chunk",
                            {
                                "stage": "worker",
                                "taskId": task.id,
                                "actor": task.assignee_name or task.assignee_id,
                                "delta": delta,
                                "fullText": result_text,
                                "title": task.title,
                            },
                        )
                else:
                    result_text = await self._run_worker_task(request, task, dependency_text)
                    streamed_text = ""
                    for delta in [result_text[i : i + 24] for i in range(0, len(result_text), 24)] or [""]:
                        streamed_text += delta
                        yield _sse(
                            "chunk",
                            {
                                "stage": "worker",
                                "taskId": task.id,
                                "actor": task.assignee_name or task.assignee_id,
                                "delta": delta,
                                "fullText": streamed_text,
                                "title": task.title,
                            },
                        )
                        await asyncio.sleep(0)

                deliveries_by_task_id[task.id] = result_text
                worker_result = {
                    "task_id": task.id,
                    "assignee_id": task.assignee_id,
                    "assignee_name": task.assignee_name or task.assignee_id,
                    "title": task.title,
                    "result": result_text,
                    "depends_on": task.depends_on,
                }
                worker_results.append(worker_result)
                yield _sse("worker_result", worker_result)

                done = self._timeline_entry(
                    "worker_done",
                    task.assignee_name or task.assignee_id,
                    f"已完成 {task.id} - {task.title}",
                )
                timeline.append(done)
                yield _sse("timeline", {"entry": done})

            if self._is_direct_worker_execution(request):
                final_result = worker_results[0]["result"] if worker_results else ""
            else:
                synth_started = self._timeline_entry("synthesizer", request.manager_name, "开始汇总全部子任务结果。")
                timeline.append(synth_started)
                yield _sse("timeline", {"entry": synth_started})

                final_result = await self._run_synthesizer(request, plan, worker_results)
                streamed_final = ""
                for delta in [final_result[i : i + 24] for i in range(0, len(final_result), 24)] or [""]:
                    streamed_final += delta
                    yield _sse(
                        "chunk",
                        {
                            "stage": "synthesizer",
                            "actor": request.manager_name,
                            "delta": delta,
                            "fullText": streamed_final,
                        },
                    )
                    await asyncio.sleep(0)

                synth_done = self._timeline_entry("synthesizer_done", request.manager_name, "已汇总全部子任务结果并生成最终交付。")
                timeline.append(synth_done)
                yield _sse("timeline", {"entry": synth_done})

            response = RuntimeTaskResponse(
                status="completed",
                rootTask=request.task,
                plan=plan,
                timeline=timeline,
                workerResults=worker_results,
                finalResult=final_result,
            )
            yield _sse("completed", {"result": response.model_dump(by_alias=True)})
        except Exception as exc:
            traceback.print_exc()
            yield _sse("error", {"message": str(exc)})


graph_runtime_service = GraphRuntimeService()
