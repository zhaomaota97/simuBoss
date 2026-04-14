import json


def extract_json_object(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty JSON payload.")

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")

    snippet = text[start : end + 1]
    parsed = json.loads(snippet)
    if not isinstance(parsed, dict):
        raise ValueError("Model output did not contain a JSON object.")
    return parsed
