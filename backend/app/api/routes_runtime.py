from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_current_session
from app.schemas.runtime import RuntimeTaskRequest
from app.services.graph_runner import graph_runtime_service

router = APIRouter(prefix="/runtime", tags=["runtime"])


@router.post("/tasks/execute")
async def execute_task(payload: RuntimeTaskRequest, _session=Depends(get_current_session)):
    return StreamingResponse(
        graph_runtime_service.stream_execute(payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
