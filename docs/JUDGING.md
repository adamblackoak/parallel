# Agentic Cinema judging readiness

This file is a build-time control sheet, not a claim that the submission is already complete.

Official competition source: `https://agentic-cinema.devpost.com/rules`

## Stage-one eligibility gates

| Requirement | Current implementation | Submission action |
|---|---|---|
| New project created during contest period | New `parallel` repository / SetWatch project | Preserve commit history showing creation during contest period |
| Media & entertainment workflow | Film/TV production pre-flight risk checking | Demonstrate with a production-plan scenario |
| Google Cloud AI only | Google ADK + Gemini | Keep non-Google AI dependencies out of runtime and repo |
| Google Cloud runtime use visible in source | `google-adk` imported and executed in `app/agent.py` / `app/runtime.py` | Deploy against Vertex AI / Google Cloud credentials |
| Parallel runtime use visible in source | `parallel-web` imported and `client.search(...)` called in `app/parallel_search.py` | Configure live `PARALLEL_API_KEY`; show qualifying run |
| Web / Android / iOS | FastAPI web app | Host on Cloud Run and submit live URL |
| Public open-source repository | Apache-2.0 `LICENSE` present | **Repository is intentionally private during build; make public before submission** |
| Complete run instructions | README + env template + Dockerfile | Verify from a clean environment |
| Demo video <= 3 minutes | Not yet recorded | Record after hosted live run is stable |
| Public YouTube/Vimeo demo | Not yet uploaded | Complete during packaging |
| English | UI and repo are English | Keep final video/submission English |

## Stage-two scoring controls

The published judging criteria are equally weighted. We should treat all four as hard quality dimensions, not assume technical novelty can compensate for a weak product experience.

### 1. Technological implementation

Evidence to expose clearly:

- genuine Parallel Search call at runtime;
- genuine Google ADK agent execution;
- Gemini reasoning over the returned live evidence;
- hosted Google Cloud deployment;
- explicit source trail in the product response;
- visible failure posture rather than silent fake fallback.

Before sign-off:

- run against live credentials;
- capture at least one `LIVE_PARALLEL_SEARCH` trace / search id during QA;
- perform clean-install smoke test;
- exercise a contradiction case and an uncertainty case;
- verify the hosted app behaves as shown in the video.

### 2. Design

The product should read as a coherent production tool, not a chat wrapper.

The demo should show:

1. a recognisable call-sheet / production-plan problem;
2. one-button pre-flight;
3. a short GO / VERIFY / CHANGE board;
4. evidence attached to consequential findings;
5. a second run where a changed condition is surfaced distinctly.

Avoid spending demo time on implementation details before the product value is visible.

### 3. Potential impact

The impact case is specific:

> Production plans depend on external conditions that can change between planning and execution. Discovering a closure, access restriction, event clash, transport failure, or similar condition after crew and equipment are moving is expensive. SetWatch concentrates live re-checking on the assumptions capable of disrupting the day.

We should support this with a concrete scenario and measured time-to-brief during final QA, rather than inventing unsupported cost-savings claims.

### 4. Quality of the idea

The non-obvious element is not “AI searches the web for filmmakers.” The product converts a static operational artefact into a set of **live falsifiable assumptions**, researches only the consequential ones, and returns a bounded production decision state.

The second-run change comparison is important: it demonstrates that the product is designed for a changing world, not a one-off research query.

## Claims discipline

Do not claim that SetWatch:

- certifies safety;
- grants or verifies permits;
- provides legal clearance;
- guarantees location availability;
- comprehensively searches the entire web;
- proves that no risk exists.

Use `VERIFY` whenever evidence cannot support a stronger operational conclusion.

## Remaining critical path

1. obtain/configure Parallel API credentials;
2. configure Google Cloud project / Vertex AI access;
3. run live integration smoke test;
4. deploy to Cloud Run;
5. complete judge-facing UI polish using real runtime behaviour;
6. add repeatable evaluation fixtures and capture QA evidence;
7. make repository public and verify licence detection;
8. record <=3 minute functional demo;
9. complete Devpost copy and final independent QA/QC review.
