# Casa Oliva Seller-side Interface Sandbox — JS / API / Seller Agent v0.1

This repo extension complements **Website V0** and preserves exactly the same 6 menu entries, 16 mock availability slots, Hong Kong fictional address, supplied phone, USD menu prices and Hong Kong time zone. All data are **fictional for research**; calls or bookings are not performed. There is no reservation or payment action.

## The four comparison groups

| Mode | Implementation | Hosting |
| --- | --- | --- |
| Website V0 (existing) | HTML webpage with displayed data and fixed availability table | GitHub Pages |
| JS / data file | `js-file/merchant.js` + `js-file/merchant.json` | GitHub Pages; public static feed |
| REST API | `backend/app.py`: `/api/restaurant`, `/api/menu`, `/api/availability` | Run locally or deploy on a Python-capable host; **not GitHub Pages** |
| Seller Agent | `POST /agent/message`: `mock` and `llm` modes; same data tools | Run locally or deploy on Python-capable host; **not GitHub Pages** |

**Important:** The `mock` mode is a rule-based demonstrator, not an LLM agent. Real LLM tool-calling requires `mode=llm` and `OPENAI_API_KEY` on the server. Never put the key in browser JavaScript or a public GitHub repository.

## Public static file URLs (once GitHub Pages publishes)

- Website V0: `https://evelyn-wen.github.io/seller-interface-sandbox/website-v0/`
- Static feed page: `https://evelyn-wen.github.io/seller-interface-sandbox/js-file/`
- JavaScript ES module: `https://evelyn-wen.github.io/seller-interface-sandbox/js-file/merchant.js`
- Plain JSON feed: `https://evelyn-wen.github.io/seller-interface-sandbox/js-file/merchant.json`

## Run the API and Seller Agent on your own computer

```bash
# From this repository's root (the folder that contains `backend/` and `data/`):
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --reload
```

Navigate to `http://127.0.0.1:8000/docs` for the interactive OpenAPI documentation.

Try the API:

```bash
curl http://127.0.0.1:8000/api/restaurant
curl 'http://127.0.0.1:8000/api/menu?vegetarian=true'
curl 'http://127.0.0.1:8000/api/availability?date=2026-12-04&time=19:00&party_size=4&seating=outdoor'
```

Try Seller Agent mock mode (no API key required):

```bash
curl -X POST 'http://127.0.0.1:8000/agent/message' \
  -H 'Content-Type: application/json' \
  -d '{"mode":"mock","message":"2026-12-04 19:00, 4 guests, outdoor seating. Any alternative?"}'
```

To use a real LLM Seller Agent, set an environment variable **locally**:

```bash
export OPENAI_API_KEY='YOUR_PRIVATE_KEY'  # never commit this
export OPENAI_MODEL='gpt-4.1-mini'
```

Then call `/agent/message` with `"mode": "llm"`; this mode uses LLM-driven function calls to the same `get_restaurant`, `get_menu`, and `check_availability` capabilities as the REST service. LLM model usage may incur charges. If no key is configured, it returns HTTP 503 rather than pretending it used AI.

## Testing

```bash
pip install pytest httpx
python -m pytest -q tests
```

## Research methodology notes

- Information parity: every interface refers to `data/merchant.json`, which is reconstructed from V0 HTML. Since website and static feed are snapshots, update them together if you change facts.
- LLM vs deterministic computation: the API directly filters by exact conditions; the Agent interprets natural language and must make tool calls in LLM mode. They measure different properties.
- API is a **real HTTP service**, not a renamed static JSON file. GitHub Pages serves the static file only, never this Python backend.
- All 16 capacity entries are **maximum party size for that time/seat option**, not seats left. Status `fully_booked` means zero capacity. No transaction state changes.
- V0 demo dates are Dec 4–6, 2026, so an unspecified query date is not treated as live availability.
- Security: do not expose an unauthenticated paid LLM endpoint publicly. Add API keys, rate limits, and a budget limit before public deployment.
