import json
import asyncio
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

    async def _post_with_retry(
        self,
        *,
        stream: bool,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        response_format: dict[str, Any] | None,
    ):
        last_error: Exception | None = None
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                async with httpx.AsyncClient(
                    base_url=self._settings.deepseek_base_url.rstrip("/"),
                    timeout=httpx.Timeout(180.0 if stream else 90.0, connect=20.0),
                ) as client:
                    if stream:
                        return client.stream(
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
                                response_format=response_format,
                                stream=True,
                            ),
                        )

                    return await client.post(
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
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as exc:
                last_error = exc
                if attempt >= max_attempts:
                    break
                await asyncio.sleep(0.8 * attempt)

        error_name = type(last_error).__name__ if last_error else "NetworkError"
        raise RuntimeError(f"DeepSeek request failed after {max_attempts} attempts: {error_name}")

    async def chat_completion(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        self._ensure_api_key()
        response = await self._post_with_retry(
            stream=False,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            response_format=response_format,
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
        last_error: Exception | None = None
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                async with httpx.AsyncClient(
                    base_url=self._settings.deepseek_base_url.rstrip("/"),
                    timeout=httpx.Timeout(180.0, connect=20.0),
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
                            raise RuntimeError(
                                f"DeepSeek request failed: {detail.decode('utf-8', errors='ignore')}"
                            )

                        async for line in response.aiter_lines():
                            if not line or not line.startswith("data: "):
                                continue
                            payload = line[6:].strip()
                            if payload == "[DONE]":
                                return

                            try:
                                parsed = json.loads(payload)
                            except json.JSONDecodeError:
                                continue

                            delta = parsed.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                        return
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as exc:
                last_error = exc
                if attempt >= max_attempts:
                    break
                await asyncio.sleep(0.8 * attempt)

        error_name = type(last_error).__name__ if last_error else "NetworkError"
        raise RuntimeError(f"DeepSeek stream request failed after {max_attempts} attempts: {error_name}")


deepseek_client = DeepSeekClient()
