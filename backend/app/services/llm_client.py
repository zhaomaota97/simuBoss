import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config import get_settings


class DeepSeekClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    def _build_payload(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        response_format: dict[str, Any] | None,
        stream: bool,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self._settings.deepseek_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "stream": stream,
        }
        if response_format:
            payload["response_format"] = response_format
        return payload

    def _ensure_api_key(self) -> None:
        if not self._settings.deepseek_api_key:
            raise RuntimeError("DeepSeek API key is not configured for the backend.")

    async def chat_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        self._ensure_api_key()

        async with httpx.AsyncClient(
            base_url=self._settings.deepseek_base_url.rstrip("/"),
            timeout=httpx.Timeout(90.0, connect=15.0),
        ) as client:
            response = await client.post(
                "/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json=self._build_payload(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    response_format=response_format,
                    stream=False,
                ),
            )

        if response.status_code >= 400:
            try:
                detail = response.json()
            except json.JSONDecodeError:
                detail = response.text
            raise RuntimeError(f"DeepSeek request failed: {detail}")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def stream_chat_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> AsyncGenerator[str, None]:
        self._ensure_api_key()

        async with httpx.AsyncClient(
            base_url=self._settings.deepseek_base_url.rstrip("/"),
            timeout=httpx.Timeout(180.0, connect=15.0),
        ) as client:
            async with client.stream(
                "POST",
                "/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json=self._build_payload(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    response_format=None,
                    stream=True,
                ),
            ) as response:
                if response.status_code >= 400:
                    detail = await response.aread()
                    raise RuntimeError(f"DeepSeek request failed: {detail.decode('utf-8', errors='ignore')}")

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    payload = line[6:].strip()
                    if payload == "[DONE]":
                        break

                    try:
                        parsed = json.loads(payload)
                    except json.JSONDecodeError:
                        continue

                    delta = parsed.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        yield delta


deepseek_client = DeepSeekClient()
