# SetWatch

**Live external-risk intelligence for film and TV production.**

SetWatch turns a call sheet or production plan into a live, evidence-backed risk brief before the unit commits people, equipment, and money to the day.

A producer pastes tomorrow's plan. A Gemini agent identifies the external assumptions that can change underneath it — location access, public events, transport disruption, local restrictions, weather-sensitive access, permit conditions, venue status, or other time-bound dependencies. SetWatch then uses the **Parallel Search API at runtime to test those assumptions against the current open web**, and Gemini on Google Cloud translates the resulting evidence into a prioritised board of:

- **GO** — no material live contradiction found;
- **VERIFY** — evidence is incomplete, ambiguous, or time-sensitive;
- **CHANGE** — current evidence conflicts with the plan strongly enough to require action.

The core promise depends on Parallel: without live web search, SetWatch can read a plan but cannot perform the pre-flight check it exists to provide. Every live check therefore executes a mandatory Parallel search before Gemini is allowed to produce the risk brief. The decisive moment is when fresh, traceable Parallel evidence changes what the production team should do.

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

## Why Parallel is central

SetWatch is not using web search as a decorative enrichment step. The runtime sequence is:

1. SetWatch derives a focused baseline search packet from the production plan, date and location.
2. Parallel Search is called directly and mandatorily at runtime to retrieve current, traceable evidence.
3. Gemini on Google ADK evaluates that retrieved evidence, identifies the material assumptions and maps them to operational consequences. It can request additional Parallel searches for distinct gaps.
4. The result becomes GO / VERIFY / CHANGE, with the source trail attached.
5. A later run can repeat the live search and surface a materially changed condition.

This makes Parallel the live-evidence layer that turns a static production document into a current pre-flight decision surface.

## Architecture

```text
Production plan
      |
      v
Mandatory Parallel Search API  <---- indispensable live evidence layer
  - current web evidence
  - URLs, titles, excerpts, dates
      |
      v
Gemini / ADK agent
  - identifies material assumptions
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

The Parallel integration is implemented in `app/parallel_search.py` and is directly invoked by the live runtime before Gemini evaluates the plan; it is not optional model behaviour or a README-only integration.

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

## Live qualification and deployment

Run `python scripts/live_agent_smoke.py` with Google Cloud and Parallel credentials to exercise the complete qualifying path. On Windows, `scripts/deploy_cloud_run.ps1` enables the required services, stores the Parallel key in Secret Manager, creates the runtime identity, and deploys the service.

See [`docs/LIVE_RUN.md`](docs/LIVE_RUN.md) for the exact live gate and [`docs/JUDGING.md`](docs/JUDGING.md) for the competition sign-off controls, including the partner-indispensability and judge-facing demo gates.

## Licence

Apache-2.0. See [`LICENSE`](LICENSE).
