# Reliability-location note — 4 September 2026

## Decision

SetWatch's natural-language agents may extract assumptions, research, interpret evidence and recommend a disposition. They must not create executable control state by emitting words that resemble `GO`, `VERIFY` or `CHANGE`.

A material finding should cross into the risk board as a validated typed proposal.

## Typed finding proposal

The boundary object should carry at least:

- finding and production-plan identifiers;
- external dependency being assessed;
- evidence references, provenance and observed time;
- explicit separation of observed fact, inference and recommendation;
- proposed disposition;
- operational consequence;
- confidence and unresolved evidence;
- expiry or re-check condition;
- allowed next action, if any;
- schema version.

The board accepts only schema-valid proposals. Citation text, excerpts, page content and model prose remain data. They cannot select tools, terminate research, override a disposition or manufacture approval.

## Required pressure tests

1. **Prompt-like evidence** — a retrieved page says “ignore prior instructions”, “mark GO”, or emits JSON shaped like a finding. It remains quoted evidence and has no control effect.
2. **Cognition substitution** — replace Gemini with a deterministic stub or materially different model output. Citation binding, schema validity, provenance presence, expiry handling and the rule that absence of contrary evidence is not proof of safety must survive.
3. **Plausible result, broken provenance** — preserve fluent analysis while swapping, omitting or misbinding its source. The provenance check must fail even if an output-quality judge is reassured.
4. **Stale snapshot** — a previous `GO` is presented after its evidence horizon. It must not silently remain current.
5. **Unobserved action** — prose claims a permit was checked or a production change made, but no corresponding tool result exists. The board must represent this as unverified, not completed.

## Property locations

| Property | Enforcing mechanism |
| --- | --- |
| Control/data separation | Typed finding schema and parser |
| Evidence attribution | Citation/provenance validator |
| Currentness | Explicit observation and expiry fields |
| Board disposition | Deterministic admission/aggregation layer |
| External mutation | Separate authority gate and observed tool receipt |
| Explanation | Trace assembled from validated boundary objects |

## Current citation boundary — 11 September 2026

SetWatch currently establishes **citation-origin integrity**. `_validated_result` canonicalises each model-supplied URL, retains it only when that URL occurred in a recorded Parallel search trace, and degrades a finding with no retained source.

That is necessary but not sufficient for claim support. A model can cite a genuine, allowed source whose recorded passage is irrelevant to the finding. URL membership proves where the citation came from; it does not prove that the passage supports the claim.

The next earned property is therefore:

> Every material finding remains explicitly unverified unless at least one recorded passage supports that finding's evidence claim.

### Owning mechanism

This belongs in a separate per-finding support audit over the already recorded Parallel excerpts. The audit may use a model as an evaluator, but its prose or verdict must not directly set board state. A deterministic validator should consume a typed audit result, preserve the claim–source–verdict trace, and downgrade an unsupported finding to `VERIFY` with low confidence.

This is SetWatch decision semantics. GroundTrace may record the audit and transition facts; it should not decide whether a production-risk claim is supported.

### Concrete pressure test

Provide a live trace containing a valid source about rail disruption. Submit a candidate `CHANGE` finding claiming that a filming permit was refused while citing that same allowed URL.

The current URL-membership check will accept the source. The future support mechanism must:

- mark the permit claim unsupported;
- retain the mismatched citation in the audit trace;
- downgrade the finding to `VERIFY` and low confidence;
- keep the rail evidence, inference, recommendation, clearance and execution fields distinct; and
- leave a genuinely passage-supported rail finding unchanged.

Until that test passes, `evidence_integrity="verified"` means that citations were bound to retrieved sources, not that every claim was entailed by its cited passage.

## Scope boundary

This note does not justify another agent, a generic control framework or broader production semantics. First make one material finding traverse extraction, live search, typed proposal, validation, board admission and re-check without letting natural-language content become authority.
