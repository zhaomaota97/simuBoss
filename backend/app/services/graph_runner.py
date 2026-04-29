import asyncio
import json
import traceback
from collections.abc import AsyncGenerator

from app.schemas.runtime import (
    ExecutionPlan,
    PlanTask,
    RuntimeDeliverable,
    RuntimeTaskRequest,
    RuntimeTaskResponse,
)
from app.services.document_parser import parse_word_base64
from app.services.json_utils import extract_json_object
from app.services.llm_client import deepseek_client
from app.services.ppt_renderer import render_ppt_from_json


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


class GraphRuntimeService:
    def _timeline_entry(self, stage: str, actor: str, message: str) -> dict:
        return {"stage": stage, "actor": actor, "message": message}

    def _is_direct_worker_execution(self, request: RuntimeTaskRequest) -> bool:
        return str(request.context.get("role", "")).lower() == "worker"

    def _task_input(self, request: RuntimeTaskRequest) -> dict:
        return request.context.get("taskInput") or {
            "kind": "text",
            "title": request.task,
            "text": request.task,
        }

    def _manager_config(self, request: RuntimeTaskRequest) -> dict:
        return request.context.get("managerConfig") or {}

    def _assignee_config(self, request: RuntimeTaskRequest, task: PlanTask) -> dict:
        configs = request.context.get("assigneeConfigs") or {}
        return configs.get(str(task.assignee_id), {})

    def _summarize(self, text: str, limit: int = 140) -> str:
        normalized = " ".join(str(text or "").split()).strip()
        if len(normalized) <= limit:
            return normalized
        return f"{normalized[:limit]}..."

    def _make_text_deliverable(self, text: str) -> RuntimeDeliverable:
        return RuntimeDeliverable(
            type="text",
            format="markdown",
            content=text,
            summary=self._summarize(text),
        )

    def _ppt_content_schema_guidance(self) -> str:
        return """
如果当前任务目标是输出 PPT 渲染 JSON，你必须只输出一个 JSON 对象，不要输出解释文字，不要输出 Markdown。

这份 JSON 必须使用新的模板原生结构，顶层固定为：
{
  "cover": {"title": "封面标题", "subtitle": "封面副标题", "date": "日期"},
  "sections": [
    {
      "id": "01",
      "title": "章节标题",
      "pages": [
        {"layout": "...", "...": "..."}
      ]
    }
  ],
  "ending": {"name": "结尾署名", "date": "日期"}
}

注意：
1. 不要再输出 slides、module、three_cols、steps、numbered_list、four_grid 这些旧字段或旧页型。
2. sections 最多 5 个，每个 section 会自动生成章节封面页。
3. pages 中 layout 只能是以下之一：

A. focus_2
{
  "layout": "focus_2",
  "title": "页面标题",
  "items": [
    {"title": "模块1标题", "text": "模块1正文"},
    {"title": "模块2标题", "text": "模块2正文"}
  ]
}

B. levels_3 / numbered_3 / stacked_3
{
  "layout": "levels_3",
  "title": "页面标题",
  "items": [
    {"label": "1", "title": "条目1标题", "text": "条目1正文"},
    {"label": "2", "title": "条目2标题", "text": "条目2正文"},
    {"label": "3", "title": "条目3标题", "text": "条目3正文"}
  ]
}

C. insight_4 / balanced_4 / quadrant_4 / followup_4
{
  "layout": "insight_4",
  "title": "页面标题",
  "items": [
    {"title": "条目1标题", "text": "条目1正文"},
    {"title": "条目2标题", "text": "条目2正文"},
    {"title": "条目3标题", "text": "条目3正文"},
    {"title": "条目4标题", "text": "条目4正文"}
  ]
}

D. duo_detail / dual_story
{
  "layout": "duo_detail",
  "title": "页面标题",
  "items": [
    {"title": "左侧标题", "text": "左侧正文"},
    {"title": "右侧标题", "text": "右侧正文"}
  ]
}

E. process_4
{
  "layout": "process_4",
  "title": "页面标题",
  "steps": [
    {"label": "01", "title": "步骤1标题", "text": "步骤1正文"},
    {"label": "02", "title": "步骤2标题", "text": "步骤2正文"},
    {"label": "03", "title": "步骤3标题", "text": "步骤3正文"},
    {"label": "04", "title": "步骤4标题", "text": "步骤4正文"}
  ]
}

F. pair_cards_2 / compare_2 / followup_2
{
  "layout": "pair_cards_2",
  "title": "页面标题",
  "items": [
    {"label": "01", "title": "模块1标题", "text": "模块1正文"},
    {"label": "02", "title": "模块2标题", "text": "模块2正文"}
  ]
}

G. columns_3 / service_3 / followup_3
{
  "layout": "columns_3",
  "title": "页面标题",
  "items": [
    {"title": "列1标题", "text": "列1正文"},
    {"title": "列2标题", "text": "列2正文"},
    {"title": "列3标题", "text": "列3正文"}
  ]
}

H. advantage_4
{
  "layout": "advantage_4",
  "title": "页面标题",
  "items": [
    {"label": "01", "title": "优势1标题", "text": "优势1正文"},
    {"label": "02", "title": "优势2标题", "text": "优势2正文"},
    {"label": "03", "title": "优势3标题", "text": "优势3正文"},
    {"label": "04", "title": "优势4标题", "text": "优势4正文"}
  ]
}

4. 目标是尽可能充分使用模板已启用的全部版式能力，但前提是版式与内容匹配。不要为了凑数量硬塞页面；如果某种 layout 不适合当前材料，就不要强行使用。
5. 优先让每个 section 内出现不同类型的页面，避免整份 PPT 只反复使用少数几种 layout。
6. 请尽量满足下面的“版式家族覆盖率”：
   - 二分说明家族：focus_2 / duo_detail / dual_story 里至少用 1 种
   - 三项表达家族：levels_3 / numbered_3 / stacked_3 / columns_3 / service_3 / followup_3 里至少用 2 种不同 layout
   - 四项表达家族：insight_4 / balanced_4 / quadrant_4 / followup_4 里至少用 2 种不同 layout
   - 流程家族：process_4 至少用 1 次
   - 对比家族：pair_cards_2 / compare_2 至少用 1 种
   - 优势总结家族：advantage_4 至少用 1 次
7. 如果原始材料信息不足，允许你做合理归纳和轻度扩写来满足覆盖率，但不要编造具体事实、数字或案例。
"""

    def _default_plan_for(self, request: RuntimeTaskRequest) -> ExecutionPlan:
        return ExecutionPlan(
            summary=f"执行任务：{request.task}",
            deliverable=f"完成“{request.task}”的交付结果",
            tasks=[
                PlanTask(
                    id="t1",
                    title=request.task,
                    assigneeId=request.manager_id,
                    assigneeName=request.manager_name,
                    task=request.task,
                    dependsOn=[],
                    reason="直接执行当前任务",
                )
            ],
            risks=[],
            openQuestions=[],
        )

    def _source_material_text(self, request: RuntimeTaskRequest) -> str:
        if request.context.get("_sourceMaterial"):
            return request.context["_sourceMaterial"]

        task_input = self._task_input(request)
        kind = str(task_input.get("kind", "text")).lower()
        if kind == "word":
            base64_payload = str(task_input.get("base64", "")).strip()
            if not base64_payload:
                raise RuntimeError("Word 文件内容缺失，无法继续执行。")
            if not str(task_input.get("fileName", "")).lower().endswith(".docx"):
                raise RuntimeError("当前仅支持上传 .docx Word 文件。")
            parsed = parse_word_base64(base64_payload)
            request.context["_sourceMaterial"] = parsed
            return parsed

        text = str(task_input.get("text") or request.task or "").strip()
        request.context["_sourceMaterial"] = text
        return text

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

        if self._is_direct_worker_execution(request):
            return self._default_plan_for(request)

        system_prompt = (
            "你是一位严谨的团队经理。"
            "请把任务拆解成结构化执行计划。"
            "简单任务优先只拆成 1 个子任务，不要为了显得完整而过度拆解。"
            "你必须只输出 JSON 对象，不要输出 markdown、解释或代码块。"
        )
        user_prompt = f"""
总任务：{request.task}
经理：{request.manager_name}
原始材料：{self._source_material_text(request)[:8000]}

请输出 JSON，字段结构必须为：
{{
  "summary": "目标理解",
  "deliverable": "最终交付形态",
  "tasks": [
    {{
      "id": "t1",
      "title": "子任务标题",
      "assigneeId": "worker-1",
      "assigneeName": "执行人名称",
      "task": "完整执行指令",
      "dependsOn": [],
      "reason": "分配原因"
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
            fallback = self._default_plan_for(request)
            timeline.append(
                self._timeline_entry(
                    "planner_fallback",
                    request.manager_name,
                    "计划生成失败，已退回到默认单任务计划。",
                )
            )
            return fallback

    def _dependency_text(self, task: PlanTask, deliveries_by_task_id: dict[str, dict]) -> str:
        blocks = []
        for dependency_id in task.depends_on:
            dependency_result = deliveries_by_task_id.get(dependency_id)
            if dependency_result:
                blocks.append(
                    f"- {dependency_id} / {dependency_result.get('title', '')}: {dependency_result.get('text', '')}"
                )
        return "\n".join(blocks) if blocks else "无前置依赖交付。"

    def _find_renderer_payload(self, task: PlanTask, deliveries_by_task_id: dict[str, dict]) -> dict:
        for dependency_id in reversed(list(task.depends_on)):
            dependency_result = deliveries_by_task_id.get(dependency_id)
            if not dependency_result:
                continue
            raw_text = str(dependency_result.get("text", "")).strip()
            if not raw_text:
                continue
            try:
                parsed = extract_json_object(raw_text)
            except Exception:
                parsed = None
            if isinstance(parsed, dict):
                return parsed
        raise RuntimeError("没有找到可用于 PPT 渲染的最终 JSON 对象。")

    def _build_worker_prompt(
        self,
        request: RuntimeTaskRequest,
        task: PlanTask,
        dependency_text: str,
        source_material: str,
    ) -> str:
        extra_guidance = ""
        task_text = f"{task.title}\n{task.task}".lower()
        if "json" in task_text and ("ppt" in task_text or "渲染" in task_text):
            extra_guidance = f"\n\n{self._ppt_content_schema_guidance()}"
        return f"""
总任务：{request.task}
当前子任务：{task.title}
执行人：{task.assignee_name or task.assignee_id}
任务说明：{task.task}

原始材料：{source_material[:12000]}

前置依赖交付：
{dependency_text}

请直接完成当前子任务，并输出你的交付结果正文。{extra_guidance}"""

    async def _run_worker_task(
        self,
        request: RuntimeTaskRequest,
        task: PlanTask,
        dependency_text: str,
        deliveries_by_task_id: dict[str, dict],
    ) -> tuple[str, RuntimeDeliverable]:
        config = self._assignee_config(request, task)
        if config.get("executionMode") == "ppt_renderer":
            payload = self._find_renderer_payload(task, deliveries_by_task_id)
            deliverable = RuntimeDeliverable.model_validate(
                render_ppt_from_json(payload, task.title or request.task)
            )
            return deliverable.summary or f"已生成 {deliverable.file_name}", deliverable

        source_material = self._source_material_text(request)
        system_prompt = config.get("prompt") or (
            "你是一名可靠的执行工人。"
            "请直接做事，不要向用户反问或索要额外信息。"
            "在信息不足时，做出最合理的假设并继续推进。"
        )
        user_prompt = self._build_worker_prompt(
            request=request,
            task=task,
            dependency_text=dependency_text,
            source_material=source_material,
        )
        result_text = await deepseek_client.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        )
        return result_text, self._make_text_deliverable(result_text)

    async def _stream_worker_task(
        self,
        request: RuntimeTaskRequest,
        task: PlanTask,
        dependency_text: str,
    ) -> AsyncGenerator[str, None]:
        config = self._assignee_config(request, task)
        system_prompt = config.get("prompt") or (
            "你是一名可靠的执行工人。"
            "请直接做事，不要向用户反问或索要额外信息。"
            "在信息不足时，做出最合理的假设并继续推进。"
        )
        user_prompt = self._build_worker_prompt(
            request=request,
            task=task,
            dependency_text=dependency_text,
            source_material=self._source_material_text(request),
        )
        async for delta in deepseek_client.stream_chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.2,
        ):
            yield delta

    async def _run_synthesizer(
        self,
        request: RuntimeTaskRequest,
        plan: ExecutionPlan,
        worker_results: list[dict],
    ) -> tuple[str, RuntimeDeliverable | None]:
        manager_config = self._manager_config(request)
        if manager_config.get("deliverableType") == "ppt":
            ppt_result = next(
                (item for item in reversed(worker_results) if item.get("deliverable", {}).get("type") == "ppt"),
                None,
            )
            if ppt_result:
                return ppt_result["result"], RuntimeDeliverable.model_validate(ppt_result["deliverable"])

        result_lines = [
            f"子任务：{item['title']}\n执行人：{item['assignee_name']}\n交付：{item['result']}"
            for item in worker_results
        ]
        final_result = await deepseek_client.chat_completion(
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

请输出最终交付内容。""",
            temperature=0.2,
        )
        return final_result, self._make_text_deliverable(final_result)

    async def execute(self, request: RuntimeTaskRequest) -> RuntimeTaskResponse:
        timeline = [self._timeline_entry("received", request.manager_name, f"收到任务：{request.task}")]
        plan = await self._build_plan(request, timeline)
        worker_results: list[dict] = []
        deliveries_by_task_id: dict[str, dict] = {}

        for task in plan.tasks:
            dependency_text = self._dependency_text(task, deliveries_by_task_id)
            timeline.append(
                self._timeline_entry(
                    "worker",
                    task.assignee_name or task.assignee_id,
                    f"开始执行 {task.id} - {task.title}",
                )
            )
            result_text, deliverable = await self._run_worker_task(
                request,
                task,
                dependency_text,
                deliveries_by_task_id,
            )
            deliveries_by_task_id[task.id] = {
                "title": task.title,
                "text": result_text,
                "deliverable": deliverable.model_dump(by_alias=True),
            }
            worker_results.append(
                {
                    "task_id": task.id,
                    "assignee_id": task.assignee_id,
                    "assignee_name": task.assignee_name or task.assignee_id,
                    "title": task.title,
                    "result": result_text,
                    "depends_on": task.depends_on,
                    "deliverable": deliverable.model_dump(by_alias=True),
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
            final_deliverable = (
                RuntimeDeliverable.model_validate(worker_results[0]["deliverable"])
                if worker_results and worker_results[0].get("deliverable")
                else None
            )
        else:
            timeline.append(self._timeline_entry("synthesizer", request.manager_name, "开始汇总全部子任务结果。"))
            final_result, final_deliverable = await self._run_synthesizer(request, plan, worker_results)
            timeline.append(self._timeline_entry("synthesizer_done", request.manager_name, "已完成最终交付整理。"))

        return RuntimeTaskResponse(
            status="completed",
            rootTask=request.task,
            plan=plan,
            timeline=timeline,
            workerResults=worker_results,
            finalResult=final_result,
            finalDeliverable=final_deliverable.model_dump(by_alias=True) if final_deliverable else None,
        )

    async def stream_execute(self, request: RuntimeTaskRequest) -> AsyncGenerator[str, None]:
        try:
            timeline: list[dict] = []
            worker_results: list[dict] = []
            deliveries_by_task_id: dict[str, dict] = {}

            received = self._timeline_entry("received", request.manager_name, f"收到任务：{request.task}")
            timeline.append(received)
            yield _sse("timeline", {"entry": received})

            plan = await self._build_plan(request, timeline)
            yield _sse("plan", {"plan": plan.model_dump(by_alias=True)})
            if len(timeline) > 1:
                yield _sse("timeline", {"entry": timeline[-1]})

            for task in plan.tasks:
                dependency_text = self._dependency_text(task, deliveries_by_task_id)
                started = self._timeline_entry(
                    "worker",
                    task.assignee_name or task.assignee_id,
                    f"开始执行 {task.id} - {task.title}",
                )
                timeline.append(started)
                yield _sse("timeline", {"entry": started})

                result_text = ""
                deliverable = None
                config = self._assignee_config(request, task)

                if config.get("executionMode") != "ppt_renderer":
                    async for delta in self._stream_worker_task(request, task, dependency_text):
                        result_text += delta
                        yield _sse(
                            "chunk",
                            {
                                "stage": "worker",
                                "taskId": task.id,
                                "assigneeId": task.assignee_id,
                                "actor": task.assignee_name or task.assignee_id,
                                "delta": delta,
                                "fullText": result_text,
                                "title": task.title,
                            },
                        )
                    deliverable = self._make_text_deliverable(result_text)
                else:
                    result_text, deliverable = await self._run_worker_task(
                        request,
                        task,
                        dependency_text,
                        deliveries_by_task_id,
                    )

                worker_result = {
                    "task_id": task.id,
                    "assignee_id": task.assignee_id,
                    "assignee_name": task.assignee_name or task.assignee_id,
                    "title": task.title,
                    "result": result_text,
                    "depends_on": task.depends_on,
                    "deliverable": deliverable.model_dump(by_alias=True) if deliverable else None,
                }
                deliveries_by_task_id[task.id] = {
                    "title": task.title,
                    "text": result_text,
                    "deliverable": worker_result["deliverable"],
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
                final_deliverable = (
                    RuntimeDeliverable.model_validate(worker_results[0]["deliverable"])
                    if worker_results and worker_results[0].get("deliverable")
                    else None
                )
            else:
                synth_started = self._timeline_entry("synthesizer", request.manager_name, "开始汇总全部子任务结果。")
                timeline.append(synth_started)
                yield _sse("timeline", {"entry": synth_started})

                final_result, final_deliverable = await self._run_synthesizer(request, plan, worker_results)
                if final_deliverable and final_deliverable.type == "text":
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

                synth_done = self._timeline_entry("synthesizer_done", request.manager_name, "已完成最终交付整理。")
                timeline.append(synth_done)
                yield _sse("timeline", {"entry": synth_done})

            response = RuntimeTaskResponse(
                status="completed",
                rootTask=request.task,
                plan=plan,
                timeline=timeline,
                workerResults=worker_results,
                finalResult=final_result,
                finalDeliverable=final_deliverable.model_dump(by_alias=True) if final_deliverable else None,
            )
            yield _sse("completed", {"result": response.model_dump(by_alias=True)})
        except Exception as exc:
            traceback.print_exc()
            yield _sse("error", {"message": str(exc)})


graph_runtime_service = GraphRuntimeService()
