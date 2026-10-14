# Gemini 3 migration preparation — 14 October 2026

## Boundary

Comparator: main `b8ef9635f56ada9e8b6371836d8754ff06417b29`.
This branch prepares an opt-in migration. It does not change the default model,
`.env.example`, deployment script, submission material, Cloud Run, IAM or project
cache policy. Results are scheduled for 16 October at 20:00 BST; the existing
17 October checkpoint remains the review point. Confirm judging has concluded
before separately authorising any deployment. A code merge alone is not deployment authority.

## Smallest credible candidate

Test `gemini-3.5-flash-lite` on the existing global GenerateContent/ADK path.
It is a recommended GA target in Google's 15 September notice and supports
function calling and JSON output. Use MEDIUM thinking for both agents, because
Google warns that its default MINIMAL can terminate multi-step tool use early.
This is a candidate, not an established quality-equivalent replacement.
3.1 Flash-Lite is cheaper but not selected without comparative evidence;
3.8 Flash is a stronger fallback if Lite fails the decision-quality gate.
No Interactions API rewrite, hosted-search substitution or prompt redesign is needed.

Both agents continue to share GEMINI_MODEL. The optional `.env.gemini3.example`
is not auto-loaded: copy its values into an isolated test process/environment.
The existing deploy script still explicitly sets 2.5 Flash; do not use it to
activate this candidate. Environment configuration is read at process startup,
so changing a variable requires a fresh process.

Gemini 3 requests omit legacy sampling controls and use thinking_level instead
of thinking_budget. The original 2.5 temperature/seed settings remain intact.
Model output is stochastic: old seed settings never guaranteed identical results.
Only non-thought final text is extracted for result parsing. Signed Content/Part
objects remain untouched inside ADK; no manual signature copy, merge, bypass
signature or history reconstruction is introduced. Citation repair is a fresh
independent session with candidate JSON and recorded sources, not a continuation
of the principal model's reasoning history.

## Dependencies and observed verification

Original constraints were google-adk>=2.8,<3 and google-genai>=2.22,<3.
They already resolve to usable SDKs. Pin the directly tested pair, ADK 2.12.0 and
GenAI 2.30.1, so future installs do not silently change this compatibility boundary.
No claim is made that older allowed versions fail. Transitive dependencies are
not fully locked. Local Python: 3.12; CI continues to target 3.11.

Baseline: 20 tests passed. Candidate: 27 tests passed in each of the default and candidate-model environments, including the existing
schema, source-binding, repair, demo and API tests. `pip check` passed.
The new offline tests exercise the real ADK runner with a synthetic model:
parallel calls, a second sequential step, matching tool IDs/names/counts,
complete signed parts including empty-text parts, SDK JSON round-trip, final
thought filtering, candidate config and preserved submission default.
These prove local history handling, not service acceptance or model quality.
Warnings: Starlette's httpx deprecation; ADK experimental function declaration
JSON schema warning. No live Google or Parallel requests were made.

## Live gates — NOT completed

Use only synthetic data until the test project's effective cache policy is reviewed.
No Google Cloud credentials or Parallel key were configured for this work.

1. Confirm test-project model entitlement/global availability and effective cacheConfig
   with read-only Cloud access. Confirm the deployed revision/config separately;
   repository defaults do not establish actual deployed state or activity eligibility.
2. In an isolated, billed test process: `python -m scripts.live_gemini3_smoke`.
   This probes actual Gemini tool continuation and repair-agent JSON. It must
   complete two ordered tool calls without thought-signature/ID errors.
   Also exercise parallel function calling against the live service if it occurs
   in representative workloads; the offline parallel test is not live proof.
3. Run `python -m scripts.live_agent_smoke` with the candidate environment and
   Parallel key. Verify exact recorded sources, schema, GO/VERIFY/CHANGE boundary,
   mandatory search and additional searches. Exercise citation repair explicitly.
4. Compare 2.5 and candidate on identical retained evidence packets and production
   plans: contradicted prerequisites -> CHANGE; missing/ambiguous evidence -> VERIFY;
   no material contradiction -> bounded GO. Include fabricated URLs, malformed JSON,
   empty findings, upstream failure, and repeated runs. Review semantic support,
   not just syntactic citation membership. Retained claim-source research on other
   branches is outside this patch and is not implied closed.
5. Measure latency, input/output/thinking tokens, search count and repair frequency.
   Existing RunMeta lacks token/cost telemetry; retain SDK/provider usage records
   during evaluation. Preserve current HTTP error handling and UI behaviour.
   No automatic model fallback/retry was added; no new search/tool budget was added.
6. Confirm results, cache-policy decision and deployment approval separately. Retain
   old image/revision and environment for rollback. Rollback to 2.5 depends on actual
   activity eligibility and is unavailable after final retirement.

## Caching and cost

InMemoryRunner is session storage, not a Cloud implicit-cache policy. There is no
explicit cache configuration in this application. Google's 25 September notice
says eligible Gemini 3 implicit caches become durable from 15 October, encrypted
and project-partitioned, retained up to 24 hours without additional durable-cache
fees. Disabled implicit caching remains disabled. Global endpoints do not provide
Data Residency Zones. The preference for ephemeral caching is not evidence that
the project's effective policy is EPHEMERAL.

Before sending real plans to Gemini 3, inspect the effective policy. Preserving
memory-only storage may require a separately authorised project cacheConfig
change (`retentionConfig.retentionType=EPHEMERAL`, with the intended disableCache
state preserved). Do not blindly enable caching with disableCache=false when
it is currently disabled. No PATCH command is run by this branch or its tests.

Listed standard global text rates, USD per million tokens (14 October):

| Model | Uncached input | Output, including reasoning |
| --- | ---: | ---: |
| 2.5 Flash | 0.30 | 2.50 |
| 3.5 Flash-Lite | 0.30 | 2.50 |
| 3.5 Flash | 1.50 | 9.00 |
| 3.8 Flash | 0.75 through Dec 31; 1.50 from Jan 1 | 3.75 through Dec 31; 7.50 from Jan 1 |

Equal token rates do not establish equal run costs: MEDIUM thinking, complete
reasoning history, additional tool steps and repair can increase consumption.
Function declarations count toward input tokens on 3.5+. Parallel and Cloud Run
charges remain separate. No claim of savings or acceptable latency is made.

The lifecycle notice explicitly lists setwatch-agentic-cinema as affected.
20 October is public retirement, not full shutdown: active means a call to the
specific model during 22 July–20 October. Qualifying existing traffic can continue;
that eligibility has not been checked here. Full global 2.5 Flash shutdown is
31 March 2027. Do not invoke the service merely to change activity status here.

## Sources inspected

- [Google model lifecycle notice](https://mail.google.com/mail/u/0/#all/1a0a62f068d9f64d), 15 September 2026.
- [Google durable caching notice](https://mail.google.com/mail/u/0/#all/1a0d5f89de83290d), 25 September 2026.
- [3.5 Flash-Lite model](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash-lite)
- [3.5 migration controls and tool response conventions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-3-5-flash)
- [Thought signatures](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/thinking/thought-signatures)
- [Pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
