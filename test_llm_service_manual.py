
import time
from src.backend.llm import GeminiClient


def main():
    client = GeminiClient()

    test_scenarios = [
        {
            "label": "Basic Retrieval",
            "context": "Page: Project Overview. WorkMate is an AI-assisted knowledge system for Notion.",
            "question": "What is WorkMate?",
        },
        {
            "label": "Task Extraction",
            "context": "Page: Meeting Notes. Emmanuel to fix Docker by Monday. Nila to start CSS on Friday.",
            "question": "What are the upcoming deadlines?",
        },
    ]

    print(f"{'='*20} WORKMATE TEST SUITE {'='*20}\n")

    for test in test_scenarios:
        print(f"TEST CATEGORY: {test['label']}")
        print(f"QUESTION: {test['question']}")
        response = client.ask_workmate(test["context"], test["question"])
        print(f"RESPONSE:\n{response}")
        print("-" * 50)
        time.sleep(2)


if __name__ == "__main__":
    main()
