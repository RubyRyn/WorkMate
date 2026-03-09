# src/backend/llm/gemini_client.py
from __future__ import annotations

import logging
import re
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types

from .config import DEFAULT_GEMINI_MODEL_ID, get_required_env
from .prompts import WORKMATE_SYSTEM_INSTRUCTION, get_rag_prompt

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Gemini client wrapper for WorkMate LLM calls.
    """

    def __init__(self, model_id: Optional[str] = None):
        api_key = get_required_env("GEMINI_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id or DEFAULT_GEMINI_MODEL_ID

    def ask_workmate(
        self, chunks: List[Dict[str, Any]], user_question: str, debug: bool = False
    ) -> str:
        """
        Generate an answer using ONLY the provided top-k context chunks.
        """
        final_prompt = get_rag_prompt(chunks, user_question, debug)

        # Keep outputs grounded + stable
        cfg = types.GenerateContentConfig(
            system_instruction=WORKMATE_SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=1024,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=final_prompt,
                config=cfg,
            )
            return getattr(response, "text", "") or ""
        except Exception as e:
            # Friendly message for MVP; later add structured logging + retries
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                retry_match = re.search(r"retryDelay['\"]:\s*['\"](\d+)s?['\"]", error_str)
                retry_secs = retry_match.group(1) if retry_match else "unknown"
                logger.warning(
                    f"⚠️  Gemini rate limit hit (model: {self.model_id}). "
                    f"Retry after: {retry_secs}s"
                )
                return f"I'm currently unable to respond due to API rate limits. Please try again in about {retry_secs} seconds."
            logger.error(f"❌ Gemini error: {e}")
            return "Sorry, something went wrong while generating a response. Please try again."
