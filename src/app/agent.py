from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

TOKEN_RE = re.compile(r"[\w+#.-]+", re.UNICODE)


def tokenize(text: str) -> set[str]:
    """Normalize text into a lightweight, dependency-free token set."""
    return {token.casefold() for token in TOKEN_RE.findall(text) if len(token) > 1}


@dataclass(frozen=True)
class Document:
    source: str
    title: str
    content: str


@dataclass(frozen=True)
class SearchHit:
    source: str
    title: str
    content: str
    score: float


class KnowledgeBase:
    """Paragraph-based retrieval with transparent lexical relevance scoring."""

    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents

    @classmethod
    def from_directory(cls, directory: Path) -> "KnowledgeBase":
        docs: list[Document] = []
        for path in sorted(directory.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            title = path.stem.replace("_", " ").title()
            current_title = title
            for block in re.split(r"\n\s*\n", text):
                block = block.strip()
                if not block:
                    continue
                if block.startswith("#"):
                    current_title = re.sub(r"^#+\s*", "", block.splitlines()[0]).strip()
                    body = "\n".join(block.splitlines()[1:]).strip()
                    if body:
                        docs.append(Document(path.name, current_title, body))
                else:
                    docs.append(Document(path.name, current_title, block))
        return cls(docs)

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        hits: list[SearchHit] = []
        for doc in self.documents:
            body_tokens = tokenize(doc.content)
            title_tokens = tokenize(doc.title)
            overlap = query_tokens & body_tokens
            score = len(overlap) / max(len(query_tokens), 1)
            score += 0.25 * len(query_tokens & title_tokens)
            if score > 0:
                hits.append(SearchHit(doc.source, doc.title, doc.content, score))
        return sorted(hits, key=lambda hit: (-hit.score, hit.source, hit.title))[:top_k]


class ChatClient(Protocol):
    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]: ...


class OpenAICompatibleClient:
    """Minimal Chat Completions client using only Python's standard library."""

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float = 45) -> None:
        if not api_key:
            raise ValueError("Set OPENAI_API_KEY before starting the live agent.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @classmethod
    def from_environment(cls) -> "OpenAICompatibleClient":
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {"model": self.model, "messages": messages, "tools": tools, "tool_choice": "auto", "temperature": 0}
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"Model API returned HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"Could not reach the model API: {exc}") from exc
        try:
            return data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("The model API returned an unexpected response.") from exc


TOOL_SPECS = [
    {"type": "function", "function": {"name": "search_knowledge", "description": "Search the supplied handbook. Use this before answering factual questions about it.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"], "additionalProperties": False}}},
    {"type": "function", "function": {"name": "calculate", "description": "Calculate a basic arithmetic expression when a numeric answer is needed.", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"], "additionalProperties": False}}},
]


def safe_calculate(expression: str) -> float | int:
    """Evaluate basic arithmetic without eval(), names, attributes, or calls."""
    import ast
    import operator

    allowed: dict[type, Any] = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow, ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def visit(node: ast.AST) -> float | int:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in allowed:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 8:
                raise ValueError("Exponent is too large.")
            result = allowed[type(node.op)](left, right)
            if isinstance(result, (int, float)) and abs(result) > 10**12:
                raise ValueError("Result is too large.")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
            return allowed[type(node.op)](visit(node.operand))
        raise ValueError("Only basic arithmetic is allowed.")

    return visit(ast.parse(expression, mode="eval"))


class KnowledgeAgent:
    def __init__(self, client: ChatClient, knowledge_base: KnowledgeBase, max_tool_rounds: int = 4) -> None:
        self.client = client
        self.knowledge_base = knowledge_base
        self.max_tool_rounds = max_tool_rounds

    def _run_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "search_knowledge":
            hits = self.knowledge_base.search(str(arguments.get("query", "")), top_k=3)
            return {"results": [{"source": h.source, "title": h.title, "content": h.content, "score": round(h.score, 3)} for h in hits]}
        if name == "calculate":
            return {"result": safe_calculate(str(arguments.get("expression", "")))}
        return {"error": f"Unknown tool: {name}"}

    def answer(self, question: str) -> str:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": "You are a careful handbook assistant. For handbook facts, call search_knowledge first and answer only from retrieved passages. If the handbook does not contain the answer, say so. Cite the source filename in square brackets. Use calculate for arithmetic. Never claim a tool succeeded unless its result is present."},
            {"role": "user", "content": question},
        ]
        for _ in range(self.max_tool_rounds + 1):
            message = self.client.complete(messages, TOOL_SPECS)
            calls = message.get("tool_calls") or []
            if not calls:
                return str(message.get("content") or "I could not produce an answer.").strip()
            messages.append({"role": "assistant", "content": message.get("content"), "tool_calls": calls})
            for call in calls:
                function = call.get("function", {})
                name = function.get("name", "")
                try:
                    arguments = json.loads(function.get("arguments", "{}"))
                    if not isinstance(arguments, dict):
                        raise ValueError("Tool arguments must be an object.")
                    result = self._run_tool(name, arguments)
                except (json.JSONDecodeError, ValueError, TypeError) as exc:
                    result = {"error": f"Invalid tool arguments: {exc}"}
                messages.append({"role": "tool", "tool_call_id": call.get("id", "missing-id"), "content": json.dumps(result, ensure_ascii=False)})
        return "I stopped because the tool-call limit was reached. Please try a more specific question."
