# src/backend/llm/gemini_client.py
from __future__ import annotations

from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types

from .config import DEFAULT_GEMINI_MODEL_ID, get_required_env
from .prompts import WORKMATE_SYSTEM_INSTRUCTION, get_rag_prompt


class GeminiClient:
    """
    Gemini client wrapper for WorkMate LLM calls.
    """

    def __init__(self, model_id: Optional[str] = None):
        api_key = get_required_env("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id or DEFAULT_GEMINI_MODEL_ID

    def ask_workmate(self, chunks: List[Dict[str, Any]], user_question: str) -> str:
        """
        Generate an answer using ONLY the provided top-k context chunks.
        """
        final_prompt = get_rag_prompt(chunks, user_question)

        # Keep outputs grounded + stable
        cfg = types.GenerateContentConfig(
            system_instruction=WORKMATE_SYSTEM_INSTRUCTION,
            temperature=0.2,
            max_output_tokens=350,
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
            return f"Answer: Sorry — I hit an error calling the LLM.\nSources:\n- (none)\nConfidence: Low\n\nError: {e}"