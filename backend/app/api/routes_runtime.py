from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.api.dependencies import get_current_session
from app.schemas.runtime import RuntimeTaskRequest
from app.services.graph_runner import graph_runtime_service
from app.services.ppt_renderer import OUTPUT_DIR

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


@router.get("/files/{file_name}")
async def get_runtime_file(file_name: str, _session=Depends(get_current_session)):
    file_path = (OUTPUT_DIR / Path(file_name).name).resolve()
    output_root = OUTPUT_DIR.resolve()
    if output_root not in file_path.parents or not file_path.exists():
        raise HTTPException(status_code=404, detail="Runtime file not found.")
    return FileResponse(path=file_path, filename=file_path.name)
