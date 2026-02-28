# test_llm_service_manual.py
# Manual runner for top-5 chunk prompt testing
# Do NOT commit secrets. Keep GEMINI_API_KEY in .env

from src.backend.llm import GeminiClient


def main():
    client = GeminiClient()

    # ✅ Manual Top-5 chunks (simulate what Chroma will return)
    # Later: replace this with actual Chroma retrieval results.
    chunks = [
        {
            "chunk_id": "c1",
            "page_title": "Project Overview",
            "text": "WorkMate is an AI-assisted knowledge system for Notion. It answers questions using retrieved Notion content.",
        },
        {
            "chunk_id": "c2",
            "page_title": "Release Checklist",
            "text": "Emmanuel will handle deployment on Saturday at 10 AM. Steps: tag release, build image, deploy to AWS.",
        },
        {
            "chunk_id": "c3",
            "page_title": "Sprint Planning",
            "text": "Backend tasks assigned. Deployment was not discussed.",
        },
        {
            "chunk_id": "c4",
            "page_title": "Incident Log",
            "text": "Emergency rollback executed last Friday due to failing migrations. Follow-up pending.",
        },
        {
            "chunk_id": "c5",
            "page_title": "Team Meeting Notes",
            "text": "Rutvik mentioned CI/CD improvements. Nila discussed chunking strategies for Notion blocks.",
        },
    ]

    question = "Who is responsible for deployment and when?"

    print("=" * 22, "WORKMATE TOP-5 MANUAL TEST", "=" * 22)
    print(f"\nQUESTION: {question}\n")

    answer = client.ask_workmate(chunks, question)

    print("RESPONSE:\n")
    print(answer)
    print("\n" + "-" * 70)


if __name__ == "__main__":
    main()