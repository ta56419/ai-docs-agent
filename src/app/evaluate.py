from __future__ import annotations

import json
from pathlib import Path

from app.agent import KnowledgeBase

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / "data" / "evaluation.json").read_text(encoding="utf-8"))


def main() -> None:
    kb = KnowledgeBase.from_directory(ROOT / "data")
    passed = 0
    for case in CASES:
        hits = kb.search(case["question"], top_k=3)
        found = any(
            hit.source == case["expected_source"]
            and hit.title == case["expected_title"]
            and case["expected_phrase"].casefold() in hit.content.casefold()
            for hit in hits
        )
        passed += int(found)
        print(f"{'PASS' if found else 'FAIL'} | {case['question']} | expected {case['expected_source']}")
    print(f"\nRetrieval hit@3: {passed}/{len(CASES)} ({passed / len(CASES):.0%})")
    if passed != len(CASES):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
