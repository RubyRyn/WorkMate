# src/backend/llm/prompts.py
from __future__ import annotations

from typing import List, Dict, Any

WORKMATE_SYSTEM_INSTRUCTION = """
You are 'WorkMate', an expert assistant for a technical project.

CRITICAL RULES:
- Use ONLY the provided context chunks below.
- Do NOT guess or use outside knowledge.
- If the answer is not explicitly stated in the chunks, say: "I cannot find this in your Notion docs."
- Always include citations in the required format.

OUTPUT FORMAT (exact):
Answer: <1-3 sentences>
Sources:
- <chunk_id> | <page_title>
Confidence: <High/Medium/Low>
""".strip()


def _format_chunks(chunks: List[Dict[str, Any]]) -> str:
    """
    Build a clean, deterministic context block with explicit chunk IDs + page titles.
    Each chunk must contain: chunk_id, page_title, text
    """
    lines = ["CONTEXT CHUNKS (Top-5):"]
    for i, ch in enumerate(chunks, start=1):
        chunk_id = ch.get("chunk_id", f"chunk_{i}")
        page_title = ch.get("page_title", "Unknown Page")
        text = (ch.get("text") or "").strip()

        lines.append(f"\n[CHUNK {i}] id={chunk_id} | page={page_title}\n{text}")

    return "\n".join(lines).strip()


def get_rag_prompt(chunks: List[Dict[str, Any]], question: str) -> str:
    """
    Combines top-k chunks with the user question into a structured prompt.
    """
    context_block = _format_chunks(chunks)

    return f"""
    {context_block}

    USER QUESTION:
    {question}

    INSTRUCTIONS:
    1) Answer ONLY using the context chunks above.
    2) If multiple chunks mention the topic, prefer the most specific one.
    3) If no chunk clearly answers, reply exactly: "I cannot find this in your Notion docs."
    4) Output MUST match the required format and include citations (chunk_id + page_title).

    Remember: Do not use outside knowledge.
    """.strip()