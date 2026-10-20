import json
import unittest
from pathlib import Path

from app.agent import Document, KnowledgeAgent, KnowledgeBase, safe_calculate


class FakeClient:
    def __init__(self, messages):
        self.messages = list(messages)
        self.calls = []

    def complete(self, messages, tools):
        self.calls.append((messages, tools))
        return self.messages.pop(0)


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase.from_directory(Path(__file__).parents[1] / "data")

    def test_retrieves_remote_work_passage(self):
        hits = self.kb.search("remote work days manager approval", top_k=3)
        self.assertTrue(hits)
        self.assertIn("three days each week", hits[0].content)

    def test_empty_or_unmatched_query_has_no_hits(self):
        self.assertEqual([], self.kb.search("!!!"))
        self.assertEqual([], self.kb.search("quantum banana"))

    def test_top_k_must_be_positive(self):
        with self.assertRaises(ValueError):
            self.kb.search("remote", top_k=0)


class ToolTests(unittest.TestCase):
    def test_calculator_supports_arithmetic(self):
        self.assertEqual(14, safe_calculate("2 + 3 * 4"))
        self.assertEqual(-2, safe_calculate("-(3 - 1)"))

    def test_calculator_rejects_code_execution(self):
        for expression in ("__import__('os').system('whoami')", "x + 1", "2 ** 100"):
            with self.subTest(expression=expression), self.assertRaises((ValueError, TypeError)):
                safe_calculate(expression)

    def test_agent_executes_tool_then_returns_answer(self):
        client = FakeClient([
            {"tool_calls": [{"id": "call-1", "function": {"name": "search_knowledge", "arguments": json.dumps({"query": "remote work days"})}}]},
            {"content": "The handbook allows remote work up to three days each week with manager approval [engineering_handbook.md]."},
        ])
        agent = KnowledgeAgent(client, KnowledgeBase([Document("engineering_handbook.md", "Remote work", "Employees may work remotely up to three days each week with their manager's approval.")]))
        answer = agent.answer("How many remote days?")
        self.assertIn("three days each week", answer)
        self.assertEqual(2, len(client.calls))
        self.assertEqual("tool", client.calls[1][0][-1]["role"])

    def test_agent_stops_after_tool_round_limit(self):
        response = {"tool_calls": [{"id": "call-1", "function": {"name": "search_knowledge", "arguments": '{"query":"remote"}'}}]}
        client = FakeClient([response] * 4)
        agent = KnowledgeAgent(client, KnowledgeBase([]), max_tool_rounds=2)
        self.assertIn("tool-call limit", agent.answer("remote?"))
        self.assertEqual(3, len(client.calls))


if __name__ == "__main__":
    unittest.main()
