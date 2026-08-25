# Aster & Row Support Agent

## Setup instructions

```bash
git clone <repository-url>
cd ai-agent-intern-test
python -m pip install -r requirements.txt
copy .env.example .env
```

Set `OPENROUTER_API_KEY` in `.env`, then build the vector store and start the CLI:

```bash
python src/indexer.py
python src/cli.py
```

## React support console

Start the API and frontend in two PowerShell terminals from the repository root:

```powershell
python .\src\api_server.py
```

```powershell
Set-Location -LiteralPath '.\frontend'
npm install
node .\node_modules\vite\bin\vite.js
```

Open `http://localhost:5173`. The React console uses the same grounded `respond()` function as the CLI. The API listens on `http://127.0.0.1:8000`.

Python 3.11+ is required. Claude is used when an API key is configured; a grounded offline fallback keeps local evaluation usable without one.

## `.env.example`

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
DEBUG=0
```

## Architecture

`indexer.py` parses YAML front matter, splits Markdown at `##` and `###` headings, embeds each section with `all-MiniLM-L6-v2`, and idempotently upserts metadata-rich chunks into persisted ChromaDB at `.chroma/`.

`agent.py` maintains a ten-turn session, retrieves five chunks, excludes internal content, prefers active documents over superseded content, and sends retrieved passages in `<retrieved_document>` tags to Claude. `order_tool.py` loads the order snapshot once and returns only customer-safe fields, with status-aware stale-estimate protection for cancelled and returned orders.

Safety layers include strict grounding instructions, prompt-injection-resistant document tags, privacy-safe tool output, action refusal, missing-order clarification, conflict handoff, and structured debug logs. Set `DEBUG=1` to emit JSON lines without API keys or PII.

## Eval command

```bash
python src/eval_runner.py
```

The runner executes `evaluation/visible-cases.json` plus five custom cases covering prompt injection, privacy, superseded returns content, a Canada follow-up, and cancelled-order stale ETA handling. It prints per-case results and category summaries and exits nonzero on failure.

## Baseline Results

Placeholder: record the first evaluation run here.

## Final Results

Placeholder: record the final evaluation run here.

## Bug Diary

1. Reproduction: a cancelled order exposed an old delivery estimate. Root cause: stale operational fields remained in the snapshot. Fix: status-aware sanitization removes delivery data for cancelled and returned orders. Regression test: `cancelled-order-stale-eta`.
2. Reproduction: migration notes could outrank current policy. Root cause: retrieval did not distinguish document status. Fix: internal chunks are excluded and superseded chunks are fallback-only. Regression test: `retrieved-prompt-injection`.
3. Reproduction: a missing order ID could lead to an invented lookup. Root cause: order intent was handled without a required identifier. Fix: the agent asks for one order ID before calling the tool. Regression test: `missing-order-id`.

## Known Limitations

- Claude responses depend on API availability and model behavior.
- The offline fallback is intentionally narrow and is not a replacement for model evaluation.
- ChromaDB and the embedding model require an initial model download.
- The order tool follows the requested minimal public schema, so carrier and ETA values are not returned to the model.

## AI tools used

GitHub Copilot assisted with implementation and test-oriented reasoning. An early implementation assumed visible evaluation concepts were literal strings; that was incomplete, so the evaluator keeps deterministic assertions focused on explicit string expectations and the agent uses grounded response templates offline.
