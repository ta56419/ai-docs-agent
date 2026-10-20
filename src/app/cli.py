from __future__ import annotations

import argparse
from pathlib import Path

from app.agent import KnowledgeAgent, KnowledgeBase, OpenAICompatibleClient

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions about the sample engineering handbook.")
    parser.add_argument("question", nargs="?", help="Question to ask")
    parser.add_argument("--demo", action="store_true", help="Show local retrieval without calling an LLM")
    args = parser.parse_args()

    kb = KnowledgeBase.from_directory(ROOT / "data")
    if args.demo:
        question = args.question or "How do I request remote work?"
        hits = kb.search(question)
        if not hits:
            print("No matching handbook passages found.")
            return
        for hit in hits:
            print(f"[{hit.source} | {hit.title} | score {hit.score:.2f}]\n{hit.content}\n")
        return
    if not args.question:
        parser.error("provide a question or use --demo")
    agent = KnowledgeAgent(OpenAICompatibleClient.from_environment(), kb)
    print(agent.answer(args.question))


if __name__ == "__main__":
    main()
