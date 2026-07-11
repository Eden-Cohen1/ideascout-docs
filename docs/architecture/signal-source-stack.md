---
id: signal-source-stack
title: Signal source stack
sidebar_position: 3
---

# Signal source stack

This page documents the signal-source adapter layer added in ideascout PR #24.

## Purpose

Keep non-web evidence acquisition behind a stable `SignalSource` contract so the research pipeline can collect HN, Reddit, Product Hunt, GitHub, and Trends evidence without knowing each engine's quirks.

## Behavior

- Signal sources are registered in `ProvidersModule` under `SIGNAL_SOURCES`, with deterministic stand-ins in `MOCK_SIGNAL_SOURCES`.
- `ResearchProcessor` seeds `ctx.signals` from the registry before classification exists; `GatherStep` narrows that set later with `SignalRegistry.activeFor()` once classification and tier are known.
- `SignalRegistry.candidateSources()` returns the available real sources. It falls back to the mock pool only when no real source is available at all.
- Missing config for one signal source does not trigger a per-source mock fallback; it simply removes that source from the real pool.
- `qualityTierForSignal()` assigns a fixed provenance-based quality tier to signal evidence, and `SEARCH_PRICES` now tracks the signal-source ids separately from web search providers.
- `GatherStep` collects signal items, then turns each item into a synthetic `FetchedPage` plus an `EvidenceItem` so VERIFY/quote matching can see the signal text itself.
- Signal collection is query-driven. If the fast LLM call works, each engine gets tailored queries; otherwise the source-specific `defaultQueries()` fallback is used.
- `GatherStep` also emits a `COVERAGE` artifact after gap analysis and any bounded follow-up rounds.

Source-specific behavior:

- Hacker News: keyless and always available; short keyword queries; search terms are ANDed, so queries must stay short.
- Reddit: requires both `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`; uses client-credentials OAuth with token caching.
- Product Hunt: requires `PRODUCTHUNT_TOKEN`; active for DEEP runs and for QUICK runs only on consumer-social, productivity, and AI/ML ideas; pulls the newest posts and keyword-filters them client-side.
- GitHub: keyless search is always available; `GITHUB_TOKEN` only raises the rate limit; active for DEVTOOLS, AI/ML, SECURITY, and API_INFRA ideas; treats open-source repos as competition and moat evidence.
- Google Trends: requires `SERPAPI_API_KEY`; DEEP only; paid SerpAPI call; uses only the first query and emits one trajectory summary.

## Why

Open question: the merged source PR does not link a Linear issue, so the product rationale for introducing the signal-source stack and the coverage-gap follow-up loop is not documented in the source materials available to the docs agent.

## Edge cases & gotchas

- Mock fallback is registry-wide only. It is not a substitute for a single unconfigured adapter.
- HN and GitHub both AND their query terms, so long queries can silently return no hits.
- Trends is paid and DEEP-only; extra queries are ignored.
- Signal items are stored as synthetic pages, so VERIFY and quote matching see the signal text itself.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/24
- Source repo: https://github.com/Eden-Cohen1/ideascout

<!-- provenance: drafted from ideascout PR #24 -->
