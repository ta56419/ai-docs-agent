# DocuAgent - grounded handbook assistant

A portfolio project combining **retrieval-augmented generation (RAG)**, **SQLite FTS5/BM25 search**, **LLM tool calling**, and a reproducible retrieval evaluation. The assistant searches a small corpus of local Markdown policies and runbooks, can run a restricted arithmetic tool, and asks an OpenAI-compatible chat model to answer from retrieved passages with source citations.

> The included handbook is synthetic demo content. FTS5/BM25 is keyword retrieval, not a vector embedding or a claim of semantic search quality. The evaluation checks retrieval against a small hand-written dataset; it does not measure end-to-end factuality of model answers.

## What it demonstrates

- Python agent loop with bounded tool calls and explicit tool schemas.
- SQLite FTS5 full-text search with BM25 ranking and title weighting over chunked Markdown documents.
- RAG-style grounding that returns source names and relevance scores to the model as evidence.
- OpenAI-compatible Chat Completions API integration using Python's standard library.
- A restricted calculator that parses arithmetic with `ast` and never calls `eval()`.
- Offline unit tests with a mocked model client, plus a transparent retrieval evaluation.
- No secrets in source control; credentials are read from environment variables.

## Requirements

- Python 3.10 or newer.
- Python built with SQLite FTS5 enabled (standard in the official Python builds used by GitHub Actions).
- An API key for live model answers. The local retrieval demo, evaluation, and tests do not need an API key or third-party packages.

## Run locally (PowerShell)

```powershell
cd ai-docs-agent
$env:PYTHONPATH = "src"
python -m app.cli --demo "How do I request remote work?"
python -m app.evaluate
python -m unittest discover -s tests -v
```

For live LLM answers, set an API key in the current shell and ask a question:

```powershell
$env:OPENAI_API_KEY = "your-key"
python -m app.cli "What should I do after a suspected security incident?"
```

Optional settings:

- `OPENAI_MODEL` (default: `gpt-4o-mini`)
- `OPENAI_BASE_URL` (default: `https://api.openai.com/v1`; may point to an OpenAI-compatible endpoint)

Do not put an API key in a committed file. `.env.example` is documentation only; the app reads environment variables directly.

## Add your own knowledge

Add `.md` files under `data/`. Each Markdown heading becomes a searchable section. Keep customer information and confidential documents out of this public demo. The agent cites the relative source path; review retrieved passages before using the project with real data.

## Evaluation

`python -m app.evaluate` runs 19 fixed retrieval cases across four synthetic documents and reports hit@3 against both the expected section and evidence phrase. The current sample result is **19/19**. This is a small, hand-written retrieval benchmark, not a guarantee of answer correctness or a general performance claim. GitHub Actions runs the unit tests and this evaluation on Python 3.11, 3.12, and 3.13.

## Design choices and limitations

- Retrieval uses FTS5's BM25 ranking with a title boost. It is keyword search, not semantic embeddings; for larger or paraphrase-heavy corpora, compare it with an embedding-based index on a larger labeled set.
- Model output is not independently fact-checked. The system prompt requests citations and grounded answers, but production use would need stronger validation, observability, access controls, and evaluations.
- Tool calls are limited to retrieval and basic arithmetic; the agent cannot execute shell commands or access arbitrary files.

## Project structure

```text
src/app/agent.py       SQLite FTS5 retrieval, model client, tool registry, agent loop
src/app/cli.py         Command-line interface and offline demo
src/app/evaluate.py    Retrieval evaluation runner
data/                  Synthetic handbook, runbooks, policies, and evaluation cases
tests/                 Offline unit tests
.github/workflows/     CI checks on three Python versions
```

## CV summary (after personal review)

**DocuAgent - Python, SQLite FTS5/BM25, LLM tool calling, RAG**: Built a handbook assistant that retrieves and ranks relevant Markdown sections, exposes retrieval and safe arithmetic as tools, and returns answers with source citations. Added 10 offline unit tests and a 19-question retrieval hit@3 evaluation (19/19 on the included synthetic corpus).

Update this summary with your own changes and actual evaluation results before using it in a CV.

