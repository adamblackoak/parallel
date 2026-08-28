# SetWatch architecture

## Design objective

SetWatch is not a general research assistant. It is a bounded production pre-flight system: identify live external assumptions in a film/TV plan, research only the material ones, and convert evidence into operational consequence.

The architecture therefore optimises for four things:

1. **live evidence is load-bearing** — Parallel Search is called at runtime;
2. **reasoning is bounded** — Gemini is constrained to a production-risk decision vocabulary;
3. **uncertainty remains visible** — weak evidence resolves to `VERIFY`, not false confidence;
4. **consequence outranks information volume** — low-value facts should not dominate the board.

## Runtime path

```text
Browser
  |
  | POST /api/check
  v
FastAPI / Cloud Run
  |
  v
Google ADK InMemoryRunner
  |
  v
SetWatch Gemini agent
  |
  +---- identify externally variable assumptions
  |
  +---- tool call: parallel_live_search(...)
            |
            v
       Parallel Search API
            |
            +---- current URLs
            +---- titles
            +---- excerpts
            +---- publication dates when available
  |
  v
Gemini evidence synthesis
  |
  +---- evidence
  +---- inference
  +---- consequence
  +---- recommended action
  +---- GO / VERIFY / CHANGE
  |
  v
JSON response -> web risk board
```

## Why Parallel is structurally necessary

Without a live web layer, a production-risk agent can only reason over the static call sheet and its model memory. That is precisely the wrong failure mode for the problem: the system exists because the external world changes after a plan is drafted.

`app/parallel_search.py` therefore exposes Parallel Search directly as an ADK tool. The agent instruction makes a Parallel tool call mandatory for every substantive check.

The returned `search_id` and source records remain available to the model during the run. The UI shows the evidence trail attached to each finding rather than asking the user to trust a model-only summary.

## Why the decision vocabulary is small

A film crew does not need another research report at call time. It needs to know what, if anything, must happen next.

- `GO`: no material contradiction found in the evidence reviewed.
- `VERIFY`: evidence is incomplete, ambiguous, stale, or needs human confirmation.
- `CHANGE`: live evidence materially conflicts with the plan or exposes a credible failure.

`GO` is deliberately not called `SAFE` or `CLEAR`: the system does not certify safety, rights, permits, or availability.

## Change detection

The browser stores the previous structured result locally and includes it in the next request. Gemini receives the previous snapshot as context and is instructed to report material changes in `change_note`.

This is intentionally simple for the first production slice. A later deployment can move snapshots to Firestore without changing the agent contract.

## Data handling

- No API keys are stored in the repository.
- `PARALLEL_API_KEY` is read from runtime environment configuration and should be injected with Google Secret Manager in Cloud Run.
- Production-plan text is passed to the model and search tooling only for the requested run.
- The current application does not persist production-plan text server-side.
- The browser's previous snapshot is local to that browser unless Firestore persistence is added.

## Failure posture

The system should fail visibly rather than quietly degrade:

- missing Parallel credentials -> live run fails;
- malformed agent output -> wrapper returns `VERIFY` plus the raw response for diagnosis;
- weak or conflicting evidence -> agent is instructed to choose `VERIFY`;
- demo mode -> visibly labelled `DEMO_NOT_LIVE` and never represented as a qualifying live integration.
