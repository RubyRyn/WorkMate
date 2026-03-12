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
    1) Answer ONLY using the context chunks above.
    2) If multiple chunks mention the topic, prefer the most specific one.
    3) If no chunk clearly answers, reply exactly: "I cannot find this in your Notion docs."
    4) Output MUST include inline citations for the source of its findings in the exact format: [Document name, section, paragraph] (section and paragraph are optional if not provided).{debug_instruction}

    Remember: Do not use outside knowledge.
    """.strip()


def get_rag_prompt_with_history(
    chunks: List[Dict[str, Any]],
    question: str,
    conversation_history: List[Dict[str, str]],
    debug: bool = False,
) -> str:
    """
    Builds a RAG prompt that includes previous conversation messages for context.
    Limits to the last 6 messages (3 exchanges) to avoid token overflow.
    Falls back to get_rag_prompt if conversation_history is empty.
    """
    if not conversation_history:
        return get_rag_prompt(chunks, question, debug)

    # Limit to last 6 messages
    recent = conversation_history[-6:]

    history_lines = ["CONVERSATION HISTORY:"]
    for msg in recent:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history_lines.append(f"{role_label}: {msg['content']}")

    history_block = "\n".join(history_lines)
    context_block = _format_chunks(chunks)

    debug_instruction = ""
    if debug:
        debug_instruction = "\n    5) DEBUG MODE ACTIVE: In addition to the standard citation, also append the chunk ID, e.g., [Document name, section, paragraph, Chunk ID: <id>]."

    return f"""
    {history_block}

    {context_block}

    CURRENT QUESTION:
    {question}

    INSTRUCTIONS:
    1) Answer ONLY using the context chunks above.
    2) If multiple chunks mention the topic, prefer the most specific one.
    3) If no chunk clearly answers, reply exactly: "I cannot find this in your Notion docs."
    4) Output MUST include inline citations for the source of its findings in the exact format: [Document name, section, paragraph] (section and paragraph are optional if not provided).{debug_instruction}
    5) Use the conversation history for context about what the user is referring to, but still only answer from the context chunks.

    Remember: Do not use outside knowledge.
    """.strip()
