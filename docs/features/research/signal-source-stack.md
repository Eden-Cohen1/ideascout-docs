---
id: signal-source-stack
title: Signal source stack
sidebar_position: 1
---

# Signal source stack

This page documents the signal-source adapter layer introduced in ideascout PR #24, the resilience hardening shipped in PR #27, and the prompt-budget / NUL-safety follow-up shipped in PR #38.

## Purpose

Keep non-web evidence acquisition behind a stable `SignalSource` contract so the research pipeline can collect HN, Reddit, Product Hunt, GitHub, and Trends evidence without knowing each engine's quirks.

## Behavior

- Signal sources are registered in `ProvidersModule` under `SIGNAL_SOURCES`, with deterministic stand-ins in `MOCK_SIGNAL_SOURCES`.
- `ResearchPipeline` now tries to rebuild a run from persisted artifacts before resuming work. If the checkpoint state is missing or invalid, it falls back to a full restart rather than trusting partial data.
- `ResearchPipeline` emits `Resuming from <step>` when it skips completed work on a retry, and it keeps the run's progress aligned with the next unfinished step.
- The signal adapters use a shared `fetchWithTimeout` helper so a hung upstream cannot pin a worker indefinitely. The deadline is composed with the caller's abort signal, so caller cancellation still wins over the timeout.
- The timeout contract is environment-tunable: fetch/search/signal calls default to 30s, and LLM calls default to 180s.
- `ResearchProcessor` seeds `ctx.signals` from the registry before classification exists; `GatherStep` narrows that set later with `SignalRegistry.activeFor()` once classification and tier are known.
- `SignalRegistry.candidateSources()` returns the available real sources. It falls back to the mock pool only when no real source is available at all.
- Missing config for one signal source does not trigger a per-source mock fallback; it simply removes that source from the real pool.
- `qualityTierForSignal()` assigns a fixed provenance-based quality tier to signal evidence, and `SEARCH_PRICES` tracks the signal-source ids separately from web search providers.
- `RunBudget` now carries `perPageChars` and `perItemChars`, and the pipeline threads those caps through `competitorPrompt()` and `dimensionPrompt()` instead of relying on hidden defaults.
- `competitorPrompt()` renders the fetched corpus with a per-page cap and trims tail pages when the rendered prompt would exceed the model-context guard.
- `dimensionPrompt()` renders evidence with a per-item cap and trims tail evidence when the rendered prompt would exceed the model-context guard.
- `GatherStep` strips NUL bytes from search results, fetched pages, and signal collections before they reach the prompt/store pipeline, and `structuredWithCost()` plus `saveArtifact()` do the same for LLM output and persisted artifacts.
- `GatherStep` collects signal items, then turns each item into a synthetic `FetchedPage` plus an `EvidenceItem` so VERIFY/quote matching can see the signal text itself.
- Signal collection is query-driven. If the fast LLM call works, each engine gets tailored queries; otherwise the source-specific `defaultQueries()` fallback is used.
- `GatherStep` also emits a `COVERAGE` artifact after gap analysis and any bounded follow-up rounds.

Source-specific behavior:

- Hacker News: keyless and always available; short keyword queries; search terms are ANDed, so queries must stay short.
- Reddit: requires both `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`; uses client-credentials OAuth with token caching.
- Product Hunt: requires `PRODUCTHUNT_TOKEN`; active for DEEP runs and for QUICK runs only on consumer-social, productivity, and AI/ML ideas; pulls the newest posts and keyword-filters them client-side.
- GitHub: keyless search is always available; `GITHUB_TOKEN` only raises the rate limit; active for DEVTOOLS, AI/ML, SECURITY, and API_INFRA ideas; treats open-source repos as competition and moat evidence.
- Google Trends: requires `SERPAPI_API_KEY`; DEEP only; paid SerpAPI call; uses only the first query and emits one trajectory summary.
- All signal adapters share the same deadline behavior, so a stalled upstream is treated as a bounded failure instead of an indefinite worker hang.

## Why

Open question: the merged source PR does not link a Linear issue, so the product rationale for the timeout/resume hardening and the prompt-budget / NUL-safety follow-up is not documented in the source materials available to the docs agent.

## Edge cases & gotchas

- Mock fallback is registry-wide only. It is not a substitute for a single unconfigured adapter.
- HN and GitHub both AND their query terms, so long queries can silently return no hits.
- Trends is paid and DEEP-only; extra queries are ignored.
- Signal items are stored as synthetic pages, so VERIFY and quote matching see the signal text itself.
- Checkpoint resume is best-effort: missing or corrupt persisted artifacts force a full restart.
- Caller cancellation is not misreported as a timeout.
- Corpus and evidence caps are measured against the rendered prompt blocks, so prompt-format changes can shift what fits.
- Oversized corpora and evidence sets are trimmed from the tail and marked degraded instead of failing the run.
- `stripNul()` only recurses into plain objects, so Dates, Maps, and class instances are passed through untouched.
- Postgres still rejects raw `0x00`, so every external ingress has to stay on the scrubbed path.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/38
- Prior source PRs: https://github.com/Eden-Cohen1/ideascout/pull/24, https://github.com/Eden-Cohen1/ideascout/pull/27
- Source repo: https://github.com/Eden-Cohen1/ideascout

<!-- provenance: drafted from ideascout PR #38 -->
