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

Open `http://127.0.0.1:8000/demo` for the visual API & Seller Agent comparison screen. Open `http://127.0.0.1:8000/docs` for interactive OpenAPI documentation.

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

## Buyer Agent v0.1 (new)

From the project folder, after activating your virtual environment and restarting the
server, visit `http://127.0.0.1:8000/demo` and choose **Buyer Agent · 四种接口**.

- **Interface:** Website (read visible HTML), JS File (read exported JS), REST API
  (GET three endpoints), or Seller Agent (POST to the seller dialogue endpoint).
- **Buyer mode = Free Mock:** offline, no LLM/API key; deterministic extraction of
  one well-formed sample reservation request. This confirms plumbing but is **NOT**
  a research result about LLM agents. Seller Agent mock is likewise rule-based.
- **Buyer mode = LLM:** one model call using the *selected interface's observed
  response*. Configure `OPENAI_API_KEY` locally; optional `BUYER_OPENAI_MODEL`
  controls the buyer model (default uses `OPENAI_MODEL` or `gpt-4.1-mini`).
- **Trace:** HTTP method, local route, HTTP status, bytes returned, approximate
  duration, observation length, final answer and token usage (LLM mode only).
- **Seller mode:** when the chosen interface is Seller Agent, select Mock or LLM;
  the latter also needs an API key and incurs further model cost.

The four data routes are served by the SAME local FastAPI app:
`GET /seller/website` returns the actual Website V0 HTML file,
`GET /seller/js-file/merchant.js` returns the JS module,
`GET /api/{restaurant,menu,availability}` returns independent REST responses,
and `POST /agent/message` invokes the Seller Agent. The buyer uses the local
HTTP/ASGI transport, so no external GitHub Pages availability is required.
It does NOT secretly read `data/merchant.json` for the Website/JS arms.

**Research limitation:** This is a one-shot, one-merchant pilot with fixed access
patterns and *unequal numbers of calls* across interfaces. The Website reader
strips HTML styling/scripts to visible text (it does not click buttons).
The LLM buyer receives a collected observation rather than autonomously choosing
multiple tool calls. Seller Agent Mock also preprocesses the consumer's query.
Consequently, timings and token totals are preliminary engineering diagnostics,
NOT a fair causal comparison of four fully autonomous interfaces. We should
later add a standardized tool budget, browser-navigation baseline, repeated tasks,
scoring rubric, and comparable seller-model conditions.

### Example test request

```bash
curl -X POST http://127.0.0.1:8000/buyer/run \
  -H 'Content-Type: application/json' \
  -d '{"task":"2026-12-04 19:00，4人，户外有座位吗？还有其他时间吗？","interface":"website","buyer_mode":"mock"}'
```

**To update an already-downloaded copy** on a Mac external drive: after stopping
Uvicorn with `Ctrl+C`, download the latest project (or apply the included update
patch), run `python -m pip install -r backend/requirements.txt` inside the existing
venv, restart `python -m uvicorn backend.app:app --reload`, and refresh `/demo`.
The external disk must remain connected while running the service.


## Unified four-interface console (updated 2026-11-17)

The `/demo` dashboard now has four separate **seller-facing** tabs: (1) **Website** embeds and interacts with the actual V0 HTML at `/seller/website`, (2) **JS File** directly fetches `/seller/js-file/merchant.js` and parses the module data for profile, menu and inventory queries, (3) **REST API** calls parameterized `/api/*` routes, and (4) **Seller Agent** posts natural-language tasks to `/agent/message` in Mock or paid LLM mode. A separate fifth **Buyer Agent** tab remains for cross-interface comparisons. The panel displays HTTP response data, timing and a local session-only request log.

For an existing external-drive installation, use the `casa_oliva_four_interface_dashboard_patch.zip` update pack provided in ChatGPT: run `apply_dashboard.py` from the `seller-interface-sandbox` directory. The patch only replaces `backend/demo.html` (with a backup) and **does not overwrite the working `backend/agent.py` Responses-API fix or any API credentials**. After installation, restart Uvicorn and refresh `http://127.0.0.1:8000/demo`. Mock Seller mode is free; LLM Seller and Buyer modes may incur third-party API charges.
