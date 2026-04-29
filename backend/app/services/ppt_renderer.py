from __future__ import annotations

from datetime import date
import importlib.util
import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
PPT_DIR = ROOT_DIR / "ppt"
PPT_APP_PATH = PPT_DIR / "app.py"
PPT_TEMPLATE_PATH = PPT_DIR / "caika-template.pptx"
GENERATED_DIR = ROOT_DIR / "backend" / "generated_ppt"
OUTPUT_DIR = GENERATED_DIR


def _slugify(value: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", str(value or "").strip())
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "generated-ppt"


def _load_ppt_module():
    if not PPT_APP_PATH.exists():
        raise RuntimeError(f"PPT generator entry not found: {PPT_APP_PATH}")

    spec = importlib.util.spec_from_file_location("simuboss_ppt_app", PPT_APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ppt/app.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _with_today_date(payload: dict) -> dict:
    today = date.today().isoformat()
    normalized = dict(payload)

    cover = dict(normalized.get("cover") or {})
    cover["date"] = today
    normalized["cover"] = cover

    ending = dict(normalized.get("ending") or {})
    ending["date"] = today
    normalized["ending"] = ending

    return normalized


def render_ppt_from_json(payload: dict, task_title: str = "generated-ppt") -> dict:
    if not isinstance(payload, dict):
        raise RuntimeError("PPT render payload must be a JSON object.")

    if not PPT_TEMPLATE_PATH.exists():
        raise RuntimeError(f"PPT template not found: {PPT_TEMPLATE_PATH}")

    module = _load_ppt_module()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    payload = _with_today_date(payload)

    base_name = _slugify(task_title)
    output_path = GENERATED_DIR / f"{base_name}.pptx"
    counter = 2
    while output_path.exists():
        output_path = GENERATED_DIR / f"{base_name}-{counter}.pptx"
        counter += 1

    generated_path = module.generate(PPT_TEMPLATE_PATH, payload, output_path)
    generated_file = Path(generated_path)

    return {
        "type": "ppt",
        "format": "pptx",
        "content": "",
        "fileName": generated_file.name,
        "downloadUrl": f"/runtime/files/{generated_file.name}",
        "path": str(generated_file),
        "summary": f"PPT generated: {generated_file.name}",
    }
