WORKMATE_SYSTEM_INSTRUCTION = """
You are 'WorkMate', an expert assistant for a technical project.
Your goal is to answer questions using ONLY the provided Notion context.
If the information is not present, say: 'I cannot find this in your Notion docs.'
""".strip()


def get_rag_prompt(context: str, question: str) -> str:
    """Combines Notion context with a user question into a structured prompt."""
    return f"""
CONTEXT FROM NOTION:
{context}

---
USER QUESTION:
{question}

INSTRUCTIONS:
1. Answer concisely based ONLY on the context above.
2. Cite the source page title.
3. If there is a deadline or task, highlight it.
""".strip()
