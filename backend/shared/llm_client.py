from __future__ import annotations

import logging
import os
import time
from typing import Optional, List, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
_DEFAULT_TIMEOUT_SECONDS = 60
_MAX_RETRIES = 1


class LLMAPIError(Exception):
    """Raised when the Groq API call fails."""


class LLMClient:

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or _DEFAULT_MODEL

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        trace_id: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:

        if not self.api_key:
            raise LLMAPIError(
                "GROQ_API_KEY is not set."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        for attempt in range(1, _MAX_RETRIES + 1):

            try:
                logger.info(
                    "trace_id=%s | calling Groq | attempt=%d",
                    trace_id,
                    attempt,
                )

                response = requests.post(
                    _GROQ_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=_DEFAULT_TIMEOUT_SECONDS,
                )

                # IMPORTANT:
                # Never sleep for the enormous retry-after returned
                # by Groq's free tier.
                if response.status_code == 429:
                    logger.warning(
                        "trace_id=%s | Groq rate limit reached (HTTP 429)",
                        trace_id,
                    )

                    raise LLMAPIError(
                        "Groq free-tier rate limit reached (HTTP 429)."
                    )

                if response.status_code in (401, 403):
                    raise LLMAPIError(
                        f"Groq authentication failed (HTTP {response.status_code})."
                    )

                response.raise_for_status()

                data = response.json()

                content = data["choices"][0]["message"]["content"]

                if not content:
                    raise LLMAPIError(
                        "Groq returned an empty response."
                    )

                logger.info(
                    "trace_id=%s | Groq request succeeded",
                    trace_id,
                )

                return content

            except LLMAPIError:
                raise

            except requests.exceptions.Timeout as exc:
                logger.warning(
                    "trace_id=%s | Groq timeout: %s",
                    trace_id,
                    exc,
                )

                if attempt >= _MAX_RETRIES:
                    raise LLMAPIError(
                        "Groq request timed out."
                    ) from exc

                time.sleep(1)

            except requests.exceptions.ConnectionError as exc:
                logger.warning(
                    "trace_id=%s | Groq connection error: %s",
                    trace_id,
                    exc,
                )

                if attempt >= _MAX_RETRIES:
                    raise LLMAPIError(
                        "Could not connect to Groq."
                    ) from exc

                time.sleep(1)

            except requests.exceptions.RequestException as exc:
                logger.warning(
                    "trace_id=%s | Groq request failed: %s",
                    trace_id,
                    exc,
                )

                raise LLMAPIError(
                    f"Groq request failed: {exc}"
                ) from exc

            except (KeyError, IndexError, ValueError) as exc:
                raise LLMAPIError(
                    f"Malformed Groq response: {exc}"
                ) from exc

        raise LLMAPIError(
            "Groq request failed after retries."
        )


GrokClient = LLMClient
GrokAPIError = LLMAPIError