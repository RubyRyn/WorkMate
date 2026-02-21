
from google import genai
from google.genai import types

from .config import DEFAULT_GEMINI_MODEL_ID, get_required_env
from .prompts import WORKMATE_SYSTEM_INSTRUCTION, get_rag_prompt


class GeminiClient:
    """Gemini client wrapper for WorkMate LLM calls."""

    def __init__(self, model_id: str | None = None):
        api_key = get_required_env("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id or DEFAULT_GEMINI_MODEL_ID

    def ask_workmate(self, notion_context: str, user_question: str) -> str:
        """Generate an answer using ONLY the provided Notion context."""
        final_prompt = get_rag_prompt(notion_context, user_question)

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                system_instruction=WORKMATE_SYSTEM_INSTRUCTION
            ),
        )

        # Safety: always return a string
        return getattr(response, "text", "") or ""
