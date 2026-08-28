# SetWatch

**Live external-risk intelligence for film and TV production.**

SetWatch turns a call sheet or production plan into a live, evidence-backed risk brief before the unit commits people, equipment, and money to the day.

A producer pastes tomorrow's plan. A Gemini agent identifies the external assumptions that can change underneath it — location access, public events, transport disruption, local restrictions, weather-sensitive access, permit conditions, venue status, or other time-bound dependencies. SetWatch researches those assumptions through the **Parallel Search API at runtime**, evaluates the evidence with **Gemini on Google Cloud**, and returns a prioritised board of:

- **GO** — no material live contradiction found;
- **VERIFY** — evidence is incomplete, ambiguous, or time-sensitive;
- **CHANGE** — current evidence conflicts with the plan strongly enough to require action.

Every material finding carries its source trail. A re-check can compare the new evidence with the previous snapshot so the user sees **what changed**, rather than receiving another undifferentiated research dump.

## Why this exists

Production planning is full of assumptions that are true when the call sheet is drafted and false when the trucks roll. The expensive failure is often not lack of information; it is failing to re-check the right external dependency at the right moment, then failing to translate a changed fact into an operational consequence.

SetWatch is deliberately narrow: it is a pre-flight agent for the live edge of a production plan.

## Hackathon track

Built as a new project for **Google Cloud Agentic Cinema: The Blockbuster Hackathon — Parallel track**.

Runtime stack:

- Google Agent Development Kit (`google-adk`)
- Gemini on Vertex AI / Google Cloud
- Parallel Search API (`parallel-web`)
- FastAPI web application
- Google Cloud Run deployment target
- Optional Firestore snapshot persistence
- Google Secret Manager-compatible environment configuration

No non-Google AI model or agent framework is used.

## Architecture

```text
Production plan
      |
      v
Gemini / ADK agent
  - extracts live assumptions
  - decides what must be researched
      |
      v
Parallel Search API  <---- required live partner integration
  - current web evidence
  - URLs, titles, excerpts, dates
      |
      v
Gemini / ADK agent
  - evidence discipline
  - operational consequence
  - GO / VERIFY / CHANGE
      |
      +----> citation-backed risk board
      |
      +----> snapshot + change comparison
```

The agent is instructed to distinguish **evidence**, **inference**, and **recommended action**. Absence of contrary search results is never treated as proof that a dependency is safe.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env
```

Configure `.env`, then:

```bash
uvicorn app.main:app --reload
```

Open `http://localhost:8000`.

### Required runtime configuration

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_USE_VERTEXAI=true
GEMINI_MODEL=gemini-2.5-flash
PARALLEL_API_KEY=...
```

The Parallel integration is implemented in `app/parallel_search.py` and is actually invoked by the agent tool at runtime; it is not a README-only integration.

## Cloud Run

```bash
gcloud run deploy setwatch \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_VERTEXAI=true
```

Provide `PARALLEL_API_KEY` through Secret Manager rather than committing it.

## Development mode

For UI development without paid API calls:

```bash
SETWATCH_DEMO_MODE=true uvicorn app.main:app --reload
```

Demo mode is visibly labelled in the UI and never masquerades as a qualifying live run. The submitted/hosted judging configuration must use the live Parallel and Google Cloud integrations.

## Tests

```bash
pytest
```

## Submission readiness

See [`docs/JUDGING.md`](docs/JUDGING.md) for the explicit competition requirements and evidence we intend to expose to judges.

## Licence

Apache-2.0. See [`LICENSE`](LICENSE).
