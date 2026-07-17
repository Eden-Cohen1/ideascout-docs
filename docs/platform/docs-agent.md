---
id: docs-agent
title: Docs agent architecture
sidebar_position: 2
---

# Docs agent architecture

The docs agent keeps this site in sync with the ideascout codebase. It runs on the Hermes
multi-agent host and is triggered by GitHub, not by a clock.

## Trigger path (event-driven)

```
merged PR on ideascout
        │  (GitHub "pull_request" webhook, action=closed, merged=true)
        ▼
Cloudflare Tunnel  ── outbound-dialed; no inbound port is opened on the VPS
        ▼
Hermes webhook adapter  (docs gateway, 127.0.0.1:8644, route "merged-pr")
        │  HMAC-SHA256 validated, event + merged filter, PR context templated
        ▼
propose-docs skill  ── classifies docs impact, drafts / updates a page
        ▼
proposal PR on ideascout-docs  ── Vercel builds a preview
        ▼
interview-docs (Slack Q&A)  →  human approval in #docs-agent
        ▼
publish-docs  ── merges the proposal PR  →  Vercel production deploy
```

A low-frequency cron sweep remains as a **reconciliation backstop** in case a webhook is
ever missed; it does the same classification but only for merges with no ledger entry.

## Storage

Canonical docs are Markdown in this repository. The registry
(`registry.json`) maps source areas and PRs to the doc pages they affect, and
`proposals/ledger.jsonl` is an append-only record of every proposal and its outcome. There is
no external docs database.

<!-- provenance: seeded from the Hermes server runbook during the Notion→Docusaurus migration -->
