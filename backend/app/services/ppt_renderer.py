import importlib.util
import re
from datetime import datetime
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[3]
PPT_DIR = REPO_ROOT / "ppt"
OUTPUT_DIR = REPO_ROOT / "outputs" / "ppt"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", str(value or "")).strip("-")
    return slug[:64] or "ppt-output"


def _load_renderer_module() -> ModuleType:
    module_path = PPT_DIR / "app.py"
    spec = importlib.util.spec_from_file_location("simuboss_ppt_renderer", module_path)
    if not spec or not spec.loader:
        raise RuntimeError("PPT renderer module could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_ppt_from_json(content_data: dict, task_title: str) -> dict:
    renderer = _load_renderer_module()
    template_path = PPT_DIR / renderer.TEMPLATE
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = f"{_slugify(task_title)}-{timestamp}.pptx"
    output_path = OUTPUT_DIR / file_name

    renderer.generate(template_path, content_data, output_path)

    return {
        "type": "ppt",
        "format": "pptx",
        "fileName": file_name,
        "downloadUrl": f"/runtime/files/{file_name}",
        "path": str(output_path),
        "summary": f"已生成 PPT 文件：{file_name}",
    }
