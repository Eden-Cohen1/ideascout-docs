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
- `SignalRegistry.candidateSources()` returns the available real sources. It falls back to the mock pool only when no real source is available at all.
- Missing config for one signal source does not trigger a per-source mock fallback; it simply removes that source from the real pool.
- `GatherStep` uses the active signal sources after classification to collect signal items, then turns each item into a synthetic `FetchedPage` plus an `EvidenceItem`.
- Signal collection is query-driven. If the fast LLM call works, each engine gets tailored queries; otherwise the source-specific `defaultQueries()` fallback is used.
- `GatherStep` also emits a `COVERAGE` artifact after gap analysis and any bounded follow-up rounds.

Source-specific behavior:

- Hacker News: keyless and always available; short keyword queries; search terms are ANDed, so queries must stay short.
- Reddit: requires both `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`; uses client-credentials OAuth with token caching.
- Product Hunt: requires `PRODUCTHUNT_TOKEN`; active for DEEP runs and for QUICK runs only on consumer-social, productivity, and AI/ML ideas; pulls the newest posts and keyword-filters them client-side.
- GitHub: keyless search is always available; `GITHUB_TOKEN` only raises the rate limit; active for DEVTOOLS, AI/ML, SECURITY, and API_INFRA ideas; treats open-source repos as competition and moat evidence.
- Google Trends: requires `SERPAPI_API_KEY`; DEEP only; paid SerpAPI call; uses only the first query and emits one trajectory summary.

## Why

PR #24 expands evidence quality by routing the research pipeline to signal sources where the evidence already lives, instead of relying on web search alone. It also pulls the coverage-gap follow-up loop forward so the pipeline can repair weak evidence during GATHER.

## Edge cases & gotchas

- Mock fallback is registry-wide only. It is not a substitute for a single unconfigured adapter.
- HN and GitHub both AND their query terms, so long queries can silently return no hits.
- Trends is paid and DEEP-only; extra queries are ignored.
- Signal items are stored as synthetic pages, so VERIFY and quote matching see the signal text itself.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/24
- Source repo: https://github.com/Eden-Cohen1/ideascout

<!-- provenance: drafted from ideascout PR #24 -->
