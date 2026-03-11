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
Confidence: <High/Medium/Low>
""".strip()


def _format_chunks(chunks: List[Dict[str, Any]]) -> str:
    """
    Build a clean, deterministic context block with explicit chunk IDs + page titles + section + paragraph.
    Each chunk must contain: chunk_id, page_title, text, (optionally section, paragraph)
    """
    if not chunks:
        return "CONTEXT CHUNKS:\n(None provided)"

    lines = ["CONTEXT CHUNKS:"]
    for i, ch in enumerate(chunks, start=1):
        chunk_id = ch.get("chunk_id", f"chunk_{i}")
        page_title = ch.get("page_title", "Unknown Page")
        section = ch.get("section", "")
        paragraph = ch.get("paragraph", "")
        text = (ch.get("text") or "").strip()

        meta_info = f"id={chunk_id} | page={page_title}"
        if section:
            meta_info += f" | section={section}"
        if paragraph:
            meta_info += f" | paragraph={paragraph}"

        lines.append(f"\n[CHUNK {i}] {meta_info}\n{text}")

    return "\n".join(lines).strip()


def get_rag_prompt(
    chunks: List[Dict[str, Any]], question: str, debug: bool = False
) -> str:
    """
    Combines top-k chunks with the user question into a structured prompt.
    """
    context_block = _format_chunks(chunks)

    debug_instruction = ""
    if debug:
        debug_instruction = "\n    5) DEBUG MODE ACTIVE: In addition to the standard citation, also append the chunk ID, e.g., [Document name, section, paragraph, Chunk ID: <id>]."

    return f"""
    {context_block}

    USER QUESTION:
    {question}

    INSTRUCTIONS:
    1) Answer ONLY using the information explicitly stated in the CONTEXT CHUNKS above.
    2) If multiple chunks mention the topic, prefer the most specific one.
    3) CRITICAL: If the CONTEXT CHUNKS do not contain the answer, or if the CONTEXT CHUNKS say "(None provided)", you MUST reply exactly: "I cannot find this in your Notion docs." DO NOT invent features, ideas, or files.
    4) Output MUST include inline citations for the source of its findings in the exact format: [Document name, section, paragraph] (section and paragraph are optional if not provided).{debug_instruction}

    Remember: Do not guess. Do not use outside knowledge.
    """.strip()
