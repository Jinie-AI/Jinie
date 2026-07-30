"""
llm_client.py

Thin, domain-agnostic wrapper around Groq's free, OpenAI-compatible
chat completions API (https://console.groq.com). This file knows
nothing about SRS/requirements — it only knows how to authenticate,
send a chat completion request, and return the raw text response with
basic retry/timeout handling. Any module in Jinie that needs an LLM
call (not just requirement.py) can reuse this client.

Setup (free, no credit card required):
    1. pip install requests python-dotenv --break-system-packages
    2. Go to https://console.groq.com, sign up with email/Google
    3. API Keys (left sidebar) -> Create API Key -> copy it (starts gsk_...)
    4. Add to backend/.env:
        GROQ_API_KEY=gsk_your_key_here
        GROQ_MODEL=llama-3.3-70b-versatile   # optional, this is the default
"""

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
_DEFAULT_TIMEOUT_SECONDS = 30
_MAX_RETRIES = 2


class LLMAPIError(Exception):
    """Raised when the Groq API call fails after all retries are exhausted."""


class LLMClient:
    """Minimal client for Groq's free, OpenAI-compatible chat completions endpoint."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or _DEFAULT_MODEL
        if not self.api_key:
            logger.warning(
                "LLMClient initialized without a GROQ_API_KEY. "
                "Get a free key at https://console.groq.com and set it in backend/.env."
            )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        trace_id: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:
        """
        Sends a chat completion request to Groq and returns the raw
        text content of the model's reply.

        `messages` follows the standard OpenAI-style chat format:
            [{"role": "system", "content": "..."},
             {"role": "user", "content": "..."}]

        Raises LLMAPIError if the request fails after retries or the
        API key is missing.
        """
        if not self.api_key:
            raise LLMAPIError("GROQ_API_KEY is not set; cannot call the LLM API.")

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

        last_error: Optional[Exception] = None
        for attempt in range(1, _MAX_RETRIES + 2):  # initial try + retries
            try:
                logger.debug(
                    "trace_id=%s | llm_client.py | attempt=%d | calling model=%s",
                    trace_id, attempt, self.model,
                )
                response = requests.post(
                    _GROQ_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=_DEFAULT_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                logger.info(
                    "trace_id=%s | llm_client.py | request succeeded on attempt=%d",
                    trace_id, attempt,
                )
                return content

            except requests.exceptions.HTTPError as exc:
                last_error = exc
                status = exc.response.status_code if exc.response is not None else "unknown"
                logger.warning(
                    "trace_id=%s | llm_client.py | HTTP error on attempt=%d | status=%s",
                    trace_id, attempt, status,
                )
                if status in (401, 403):
                    break  # auth errors won't be fixed by retrying
                if status == 429:
                    logger.warning(
                        "trace_id=%s | llm_client.py | rate limited by Groq free tier, backing off",
                        trace_id,
                    )
                time.sleep(0.5 * attempt)

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                last_error = exc
                logger.warning(
                    "trace_id=%s | llm_client.py | network error on attempt=%d | error=%s",
                    trace_id, attempt, str(exc),
                )
                time.sleep(0.5 * attempt)

            except (KeyError, IndexError, ValueError) as exc:
                last_error = exc
                logger.warning(
                    "trace_id=%s | llm_client.py | malformed response on attempt=%d | error=%s",
                    trace_id, attempt, str(exc),
                )
                time.sleep(0.5 * attempt)

        logger.error(
            "trace_id=%s | llm_client.py | all attempts exhausted | last_error=%s",
            trace_id, str(last_error),
        )
        raise LLMAPIError(f"Groq API call failed after retries: {last_error}") from last_error


# Backwards-compatible aliases (in case other files still import the old names)
GrokClient = LLMClient
GrokAPIError = LLMAPIError