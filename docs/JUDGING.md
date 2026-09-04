# Agentic Cinema judging readiness

This file is a build-time control sheet, not a claim that the submission is already complete.

Official competition source: `https://agentic-cinema.devpost.com/rules`

## Competition doctrine

SetWatch is not being optimised merely to be a good product that happens to satisfy the track requirements. It must be a **high-scoring Parallel-track submission**.

The hard competitive question is:

> Would a Parallel judge regard SetWatch as one of the clearest, strongest demonstrations of why Parallel Search is indispensable to a real media & entertainment workflow?

If the answer is not clearly yes, architecture or polish elsewhere does not compensate.

The GroundPitch result is now treated as calibration evidence: strong implementation and a coherent product are not sufficient if the partner technology is useful but not unmistakably central to the winning story. For SetWatch, the partner integration therefore has to be visible, consequential, and impossible to remove without breaking the product's core promise.

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

## Partner indispensability gate

Before final implementation or packaging, all of the following must be true:

1. **No Parallel = no SetWatch promise.** Without live Parallel Search, the product can parse a plan but cannot perform the live pre-flight function it is built to provide.
2. **Parallel changes the operational answer.** The demo must show live web evidence causing a meaningful GO / VERIFY / CHANGE outcome, not merely enriching a static analysis.
3. **Partner use is visible to the judge.** The product or demo must make the live Parallel research step and its source trail obvious without forcing the judge to inspect code first.
4. **Parallel is used for what it is distinctively good at.** Fresh, traceable open-web evidence should be the decisive input, not a replaceable lookup layer.
5. **The submission teaches the sponsor something useful about its own product.** The use case should feel like a credible showcase of Parallel Search in production operations, not a generic agent with Parallel bolted on.

Any failure on 1-3 is a stop condition for submission polish: fix partner centrality before adding features.

## Stage-two scoring controls

The published judging criteria are equally weighted. Treat all four as hard quality dimensions; do not assume technical novelty can compensate for a weak product experience or weak partner centrality.

### 1. Technological implementation

Evidence to expose clearly:

- genuine Parallel Search call at runtime;
- genuine Google ADK agent execution;
- Gemini reasoning over the returned live evidence;
- hosted Google Cloud deployment;
- explicit source trail in the product response;
- visible failure posture rather than silent fake fallback;
- visible evidence that the Parallel result affected the operational decision.

Before sign-off:

- run against live credentials;
- capture at least one `LIVE_PARALLEL_SEARCH` trace / search id during QA;
- perform clean-install smoke test;
- exercise a contradiction case and an uncertainty case;
- verify the hosted app behaves as shown in the video;
- verify that removing/short-circuiting Parallel would materially break the demonstrated workflow.

### 2. Design

The product should read as a coherent production tool, not a chat wrapper.

The demo should show:

1. a recognisable call-sheet / production-plan problem;
2. one-button pre-flight;
3. a visible live Parallel research step;
4. a short GO / VERIFY / CHANGE board;
5. evidence attached to consequential findings;
6. one finding where the live evidence clearly changes what the production team should do;
7. a second run where a changed condition is surfaced distinctly.

Avoid spending demo time on implementation details before the product value is visible.

### 3. Potential impact

The impact case is specific:

> Production plans depend on external conditions that can change between planning and execution. Discovering a closure, access restriction, event clash, transport failure, or similar condition after crew and equipment are moving is expensive. SetWatch concentrates live re-checking on the assumptions capable of disrupting the day.

The key competitive point is that this impact depends on **fresh external evidence**, which is exactly where Parallel Search enters the workflow. SetWatch is not useful because an LLM can read a call sheet; it is useful because the plan is continuously confronted with current, traceable evidence from the open web.

Support this with a concrete scenario and measured time-to-brief during final QA rather than inventing unsupported cost-savings claims.

### 4. Quality of the idea

The non-obvious element is not “AI searches the web for filmmakers.” The product converts a static operational artefact into a set of **live falsifiable assumptions**, uses Parallel Search to test the consequential ones against the current web, and returns a bounded production decision state.

The second-run change comparison is important: it demonstrates that the product is designed for a changing world, not a one-off research query.

## Judge-facing 45-second test

Before the demo is recorded, the first 45 seconds must work even for a judge who knows nothing about the architecture.

Target sequence:

- **0-10s:** Show tomorrow's production plan and state the risk: plans go stale before crews move.
- **10-20s:** Run SetWatch; visibly show it extracting the few external assumptions worth checking.
- **20-35s:** Show Parallel Search retrieving current evidence for one consequential dependency.
- **35-45s:** Show that evidence change the board to VERIFY or CHANGE with a concrete production action.

If this sequence is not immediately convincing, do not compensate by adding more narration. Fix the product/demo surface.

## Competitive sign-off questions

Final independent QA must answer these with evidence, not optimism:

- Is the problem understandable in one sentence?
- Is the media/entertainment audience unmistakable?
- Is Parallel Search indispensable rather than merely compliant?
- Does the demo contain one memorable moment where live Parallel evidence changes the decision?
- Is the source trail visible enough to demonstrate freshness and traceability?
- Does the product feel complete rather than like a technical proof of concept?
- Could a Parallel developer-relations team plausibly use this project as a showcase of the Search API?
- Have we removed anything that consumes demo time without increasing one of the four judging scores?

A weak answer to the sponsor-specific questions is a reason to revise before submission, not a reason to write better copy around the weakness.

## Claims discipline

Do not claim that SetWatch:

- certifies safety;
- grants or verifies permits;
- provides legal clearance;
- guarantees location availability;
- comprehensively searches the entire web;
- proves that no risk exists.

Use `VERIFY` whenever evidence cannot support a stronger operational conclusion.

## Public-demo source handling

Competition guidance for the Parallel track indicates that public demo videos/screenshots should avoid exposing real third-party names, page titles, or URLs returned by live search; fictional/mock published materials are safer. The hosted live application may still show genuine Parallel Search results because that is the integration being judged.

Therefore:

- public screenshots/video: use a controlled fictional production scenario and mock/fictional public-facing source names where necessary;
- hosted judging app: keep genuine live Parallel Search enabled;
- do not disguise demo-mode output as a qualifying live run;
- ensure the video still demonstrates the real end-to-end workflow faithfully.

## Remaining critical path

1. obtain/configure Parallel API credentials;
2. configure Google Cloud project / Vertex AI access;
3. run live integration smoke test;
4. deploy to Cloud Run;
5. make the Parallel research step and consequential evidence-change moment visually obvious;
6. complete judge-facing UI polish using real runtime behaviour;
7. add repeatable contradiction/uncertainty/change fixtures and capture QA evidence;
8. run the partner-indispensability gate and independent competitive review;
9. make repository public and verify licence detection;
10. record <=3 minute functional demo with the first 45 seconds passing the judge-facing test;
11. complete Devpost copy around the sponsor-specific value, then final independent QA/QC review.
