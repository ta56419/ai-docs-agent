# DocuAgent - grounded handbook assistant

A compact portfolio project that combines **retrieval-augmented generation (RAG)**, **LLM tool calling**, and a small, reproducible retrieval evaluation. The assistant searches a local Markdown handbook, can run a restricted arithmetic tool, and asks an OpenAI-compatible chat model to answer from retrieved passages with source citations.

> The included handbook is synthetic demo content. The retrieval score is lexical, not a vector embedding or a claim of semantic search quality. The evaluation checks retrieval against a tiny hand-written dataset; it does not measure end-to-end factuality of model answers.

## What it demonstrates

- Python agent loop with bounded tool calls and explicit tool schemas.
- RAG-style grounding over local Markdown documents, returning source names and relevance scores.
- OpenAI-compatible Chat Completions API integration using Python's standard library.
- A restricted calculator that parses arithmetic with `ast` and never calls `eval()`.
- Offline unit tests with a mocked model client, plus a transparent retrieval evaluation.
- No secrets in source control; credentials are read from environment variables.

## Requirements

- Python 3.10 or newer.
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

Add `.md` files under `data/`. Each Markdown heading becomes a searchable section. Keep customer information and confidential documents out of this public demo. The agent will only cite the source filename; review retrieved passages before using the project with real data.

## Evaluation

`python -m app.evaluate` runs eight fixed retrieval cases and reports hit@3. The suite is deliberately small and transparent so it can be extended with representative questions and expected evidence. Passing it is not a guarantee that a generated answer is correct.

## Design choices and limitations

- Retrieval uses token overlap and title matches to keep the project dependency-free and easy to inspect. For larger corpora, replace it with embeddings and a vector index, then compare retrieval quality on a larger labeled set.
- Model output is not independently fact-checked. The system prompt requests citations and grounded answers, but production use would need stronger validation, observability, access controls, and evaluations.
- Tool calls are limited to retrieval and basic arithmetic; the agent cannot execute shell commands or access arbitrary files.

## Project structure

```text
src/app/agent.py       Retrieval, model client, tool registry, agent loop
src/app/cli.py         Command-line interface and offline demo
src/app/evaluate.py    Retrieval evaluation runner
data/                  Synthetic handbook and evaluation cases
tests/                 Offline unit tests
```

## CV summary (after personal review)

**DocuAgent - Python, LLM tool calling, RAG, evaluation**: Built a handbook assistant that retrieves relevant passages from Markdown, exposes retrieval and safe arithmetic as tools, and returns answers with source-file citations. Added offline unit tests and an eight-case retrieval hit@3 evaluation.

Update this summary with your own changes and actual evaluation results before using it in a CV.

Current sample result: hit@3 is 8/8 on the eight included questions and one synthetic handbook. This small demo score is not a general quality guarantee.
