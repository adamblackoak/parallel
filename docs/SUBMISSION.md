# SetWatch submission pack

Use this file as the final packaging source for the Google Cloud Agentic Cinema / Parallel-track submission. It is deliberately judge-facing: concise product story first, implementation proof second.

## One-line pitch

**SetWatch turns tomorrow's film or TV production plan into live, falsifiable external assumptions, checks them against the current web with Parallel Search, and returns a bounded GO / VERIFY / CHANGE decision before crews and equipment move.**

## Short description

Production plans go stale. Location access changes, transport breaks, public events appear, restrictions move and weather turns. SetWatch identifies the few external assumptions capable of disrupting a production day, researches them live through Parallel Search, and uses Gemini on Google ADK to translate current evidence into a short operational brief.

Every material finding separates evidence, inference, consequence and recommended action. Sources remain attached. A repeat run can distinguish changed conditions from the previous snapshot instead of producing another undifferentiated research dump.

Parallel is the indispensable live-evidence layer: without it, SetWatch can read a plan but cannot perform the pre-flight check the product exists to provide.

## What it does

1. A producer pastes a call-sheet extract or production plan and supplies the production date and location context.
2. SetWatch performs a mandatory Parallel Search against the live web before Gemini is allowed to evaluate the plan.
3. Gemini / Google ADK identifies consequential external assumptions and evaluates the Parallel evidence.
4. SetWatch returns a bounded **GO**, **VERIFY** or **CHANGE** board with evidence, inference, operational consequence, recommended action and source trail.
5. A later run can surface changed conditions separately from the previous snapshot.

## Why Parallel

Parallel is not decorative search in SetWatch. It is the mechanism that converts a static production artefact into a current operational decision surface.

The demonstrated chain should be obvious to a judge:

**production assumption -> live Parallel evidence -> changed factual position -> operational consequence -> GO / VERIFY / CHANGE**

The memorable demo moment should be a real contradiction or uncertainty where fresh Parallel evidence changes what the production team should do.

## Google Cloud implementation

- Google Agent Development Kit (`google-adk`)
- Gemini on Vertex AI / Google Cloud
- Parallel Search API (`parallel-web`)
- FastAPI web application
- Google Cloud Run deployment
- Secret Manager-compatible configuration
- Optional Firestore snapshot persistence

No non-Google AI model or agent framework is used.

## Suggested Devpost answers

### Inspiration

Film and TV production plans contain dozens of facts, but only a handful are external assumptions capable of derailing the day. Those assumptions can change after the call sheet is written and before the unit moves. SetWatch focuses live research on that moving edge.

### What it does

SetWatch turns a production plan into falsifiable external assumptions, researches those assumptions live through Parallel Search, and uses Gemini on Google ADK to return a bounded GO / VERIFY / CHANGE operational brief. Material findings retain their source trail and distinguish evidence from inference and recommended action. Re-running the same plan can surface what changed since the previous snapshot.

### How we built it

The web app runs on FastAPI and targets Google Cloud Run. Every live pre-flight begins with a mandatory Parallel Search call. The returned current-web evidence is then supplied to a Gemini agent built with Google ADK, which produces schema-validated findings. The runtime records partner traces and search identifiers so the hosted product can show that live Parallel evidence was actually used. Configuration is kept out of source and is compatible with Google Secret Manager.

### Challenges

The main design problem was preventing a capable language model from turning incomplete search evidence into false certainty. SetWatch therefore treats absence of contradictory results as insufficient proof, separates evidence from inference, and uses VERIFY when the evidence cannot support a stronger conclusion. A second challenge was making the partner integration consequential rather than ornamental, so the runtime now requires Parallel Search before Gemini can issue a live brief.

### Accomplishments

SetWatch is a functioning production-oriented agent rather than a chat wrapper: it has a bounded decision vocabulary, live source trails, explicit runtime partner evidence, failure behaviour that does not silently fake a live result, and a previous-run comparison designed for changing operational conditions.

### What we learned

The useful unit of live web research is not "everything related to this plan". It is the small set of external assumptions whose falsification would change an operational decision. That shift made Parallel Search materially more useful and made Gemini's role clearer: Parallel establishes the current evidence surface; Gemini maps that evidence to production consequence.

### What's next

The natural extension is scheduled re-checking as a production date approaches, followed by integrations with call-sheet and production-management systems so changed external conditions can be surfaced without requiring teams to manually re-enter the plan.

## Demo video: target 2:10 to 2:30

Start with a hard refresh, then click **Load scenario**. That action clears saved comparison
state, leaves comparison visibly off, and loads tomorrow's date. Do not enable comparison in
the main submission recording.

**0:00-0:20 — problem.** Show the loaded plan and say: "A call sheet is static, but the
outside world is not. Here, a central London unit has an early exterior, two 7.5-tonne trucks,
rail-dependent crew and limited rain cover. Crucially, the plan assumes no filming permit or
parking dispensation is required. SetWatch checks whether the live world supports that plan."

**0:20-0:35 — run.** Say: "It converts the plan into falsifiable external assumptions and
researches them through Parallel before Gemini is allowed to decide." Click **Run live
pre-flight**. Show two or three seconds of the live wait, then cut to the completed result.

**0:35-1:15 — decisive result.** Say: "The answer is CHANGE. The plan explicitly says no
permit or parking dispensation has been arranged, while the live City of London evidence says
those permissions are required. That is not generic web research; it changes what production
must do before dispatch." Show the permit/dispensation finding and its source.

**1:15-1:40 — disciplined reasoning.** Move across **Evidence, Inference, Consequence and
Action** and say: "SetWatch keeps retrieved evidence separate from inference, explains the
production consequence, and gives a bounded action. Where road, rail or weather evidence is
not specific enough to establish the exact operational threshold, it says VERIFY rather than
manufacturing certainty." Describe only the secondary findings actually visible in the run.

**1:40-2:05 — proof.** Show the attached links and Runtime evidence panel. Say: "Every live
run requires Parallel first. This is the recorded LIVE_PARALLEL_SEARCH trace, the real search
ID, the retrieved-result count and the exact queries. The output is schema-validated and its
evidence integrity is verified."

**2:05-end — close.** Say: "Parallel establishes the current evidence surface. Gemini on
Google ADK maps it to operational consequence, and SetWatch returns a bounded GO, VERIFY or
CHANGE decision on Google Cloud. The call sheet tells you what tomorrow is supposed to look
like. SetWatch checks whether the world still agrees."

The number and wording of secondary findings may change with the live web. Do not narrate a
specific rail, event or weather conclusion until it is visible. The permit/dispensation
contradiction is the stable demonstration anchor.

## Final submission gate

Before pressing Submit, verify all of these against the actual hosted build rather than memory:

- hosted URL loads without authentication;
- `/health` reports `mode: live` and `live_ready: true`;
- one fresh run shows a real Parallel partner trace / search id;
- one consequential finding contains a visible source trail;
- no silent demo fallback is possible in the hosted judging configuration;
- repo is public and licence is detected;
- README clean-start instructions still match the repository;
- video is <= 3 minutes and publicly accessible in the format required by the competition;
- the first 45 seconds show the problem, Parallel research and a changed operational answer;
- Devpost text does not claim safety certification, permit verification, legal clearance, guaranteed availability or comprehensive web coverage;
- final submission URL, repository URL and video URL are opened once from a logged-out/incognito context.

## Freeze rule

After a qualifying hosted run and successful submission-package check, do not add features unless they repair a demonstrated judging failure. From that point onward, changes should be limited to correctness, reliability, legibility and submission packaging.
