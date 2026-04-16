# src/backend/llm/gemini_client.py
from __future__ import annotations

import logging
import re
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types

from .config import DEFAULT_GEMINI_MODEL_ID
from . import prompts

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Gemini client wrapper for WorkMate LLM calls.
    """

    def __init__(self, model_id: Optional[str] = None):
        import os
        api_key = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No Gemini API key found. Set GEMINI_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY.")
            
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id or DEFAULT_GEMINI_MODEL_ID

    def filter_chunks(
        self, chunks: List[Dict[str, Any]], user_question: str
    ) -> List[Dict[str, Any]]:
        """
        LLM Re-ranking: Asks Gemini to filter out irrelevant chunks before generation.
        Uses sequential chunk_N IDs (chunk_1, chunk_2, ...) for the filter prompt so
        the LLM and the matching logic agree on the same ID format.
        """
        if not chunks:
            return []

        # Remap chunks to sequential IDs for the filter prompt so the LLM
        # returns predictable IDs like "chunk_1, chunk_3" instead of UUIDs.
        sequential_id_map: Dict[str, Dict[str, Any]] = {}
        remapped_chunks = []
        for i, chunk in enumerate(chunks, start=1):
            seq_id = f"chunk_{i}"
            sequential_id_map[seq_id] = chunk
            remapped_chunks.append({**chunk, "chunk_id": seq_id})

        prompt = prompts.get_filter_prompt(remapped_chunks, user_question)
        cfg = types.GenerateContentConfig(
            system_instruction=prompts.FILTER_SYSTEM_INSTRUCTION,
            temperature=0.0,
            max_output_tokens=100,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=cfg,
            )
            output = getattr(response, "text", "") or ""
            print(f"Re-ranker Output: {output}")

            if "NONE" in output.upper():
                print("Re-ranker kept 0 chunks.")
                return []

            # Match returned IDs (e.g. "chunk_1, chunk_3") back to original chunks.
            output_parts = [p.strip() for p in output.split(",") if p.strip()]
            filtered_chunks = []
            seen = set()
            for part in output_parts:
                # Exact match: "chunk_3"
                if part in sequential_id_map and part not in seen:
                    filtered_chunks.append(sequential_id_map[part])
                    seen.add(part)
                    continue
                # Plain number match: LLM returned "3" instead of "chunk_3"
                candidate = f"chunk_{part}"
                if candidate in sequential_id_map and candidate not in seen:
                    filtered_chunks.append(sequential_id_map[candidate])
                    seen.add(candidate)

            print(f"Re-ranker kept {len(filtered_chunks)}/{len(chunks)} chunks.")

            # Fallback: if nothing matched but LLM didn't say NONE, return all chunks.
            if not filtered_chunks:
                return chunks
            return filtered_chunks

        except Exception as e:
            logger.warning(f"Re-ranking failed (falling back to all chunks): {e}")
            return chunks

    def ask_workmate(
        self,
        chunks: List[Dict[str, Any]],
        user_question: str,
        debug: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate an answer using ONLY the provided top-k context chunks.
        """
        if conversation_history:
            final_prompt = prompts.get_rag_prompt_with_history(
                chunks, user_question, conversation_history, debug
            )
        else:
            final_prompt = prompts.get_rag_prompt(chunks, user_question, debug)

        # Keep outputs grounded + stable
        cfg = types.GenerateContentConfig(
            system_instruction=prompts.WORKMATE_SYSTEM_INSTRUCTION,
            temperature=0.0,
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

    async def ask_workmate_stream(
        self,
        chunks: List[Dict[str, Any]],
        user_question: str,
        debug: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Async generator that streams the answer using Gemini's streaming API.
        Yields text chunks as they arrive.
        """
        if conversation_history:
            final_prompt = prompts.get_rag_prompt_with_history(
                chunks, user_question, conversation_history, debug
            )
        else:
            final_prompt = prompts.get_rag_prompt(chunks, user_question, debug)

        cfg = types.GenerateContentConfig(
            system_instruction=prompts.WORKMATE_SYSTEM_INSTRUCTION,
            temperature=0.0,
            max_output_tokens=1024,
        )

        try:
            response = self.client.models.generate_content_stream(
                model=self.model_id,
                contents=final_prompt,
                config=cfg,
            )
            for chunk in response:
                text = getattr(chunk, "text", "") or ""
                if text:
                    yield text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                retry_match = re.search(r"retryDelay['\"]:\s*['\"](\d+)s?['\"]", error_str)
                retry_secs = retry_match.group(1) if retry_match else "unknown"
                logger.warning(
                    f"⚠️  Gemini rate limit hit (model: {self.model_id}). "
                    f"Retry after: {retry_secs}s"
                )
                yield f"I'm currently unable to respond due to API rate limits. Please try again in about {retry_secs} seconds."
            else:
                logger.error(f"❌ Gemini error: {e}")
                yield "Sorry, something went wrong while generating a response. Please try again."
