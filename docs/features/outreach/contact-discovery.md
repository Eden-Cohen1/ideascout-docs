---
id: contact-discovery
title: Contact discovery & enrichment
sidebar_position: 2
---

# Contact discovery & enrichment

## Purpose

Confirming a campaign's persona kicks off contact discovery: a queued job searches for real people matching the persona, enriches each one with role/company/experience/social links, and presents the results as reviewable contact cards. This replaces the "upcoming slice" placeholder with a working discovery → review loop, mock-only until a real vendor is chosen.

## Behavior

### Provider contract — `PeopleDiscoveryProvider`

A new adapter family in the existing provider-registry pattern. Two methods on the stable interface:

| Method | Input | Output | What it does |
|---|---|---|---|
| `search(persona, limit)` | A `PersonaHypothesis` (the persona schema *is* the query language — no intermediate type) | `CandidateContact[]` | Finds people matching the persona, capped at `limit` |
| `enrich(candidate)` | One `CandidateContact` | `ContactEnrichment` | Returns a full profile for one person |

The persona schema is the neutral query language. Vendors map their own vocabularies to our shared enums (e.g. `C_LEVEL` → Apollo's `c_suite`) privately inside each adapter; adapters never touch Prisma or campaign state.

### Registry — `PeopleRegistry`

Config-selected default provider (`PEOPLE_DEFAULT_PROVIDER` env var, defaults to `mock`), keyless fallback to the deterministic mock. Mirror of the existing `LlmRegistry` / `ResearchRegistry` pattern.

### Discovery job — `DiscoveryProcessor`

One job per campaign confirm (or retry), not fan-out:

1. **Search** the provider via `search(persona, maxContacts)` — the hard cap is enforced in the job, not trusted to the adapter.
2. **Enrich** each candidate sequentially via `enrich(candidate)`. A failed enrich leaves that contact at `DISCOVERED` (identity-only card) and never fails the run.
3. **Atomic write** — one transaction: wipe existing contacts → `createMany` → state-guarded transition `DISCOVERING → REVIEWING`. A crash or retry can never leave partial or duplicate contacts.

### Contact model

**Identity (required):** `fullName`, `headline`, `company`.
**Enrichment (optional Zod-validated Json):** `location`, `seniority`/`companySize` (shared persona enums), `experienceSummary`, `socialLinks` (http(s)-only), `recentActivity` (optional and normal-when-absent — see Why).
**Derived (stored):** `matchRationale` (pure function, never LLM-generated), `source` (provider provenance).
**Deliberately absent:** email, phone. (See Why below.)

Contacts cascade-delete with their campaign. Per-contact funnel state: `DISCOVERED` (identity only) and `ENRICHED` (full profile).

### Match rationale — `matchRationale` function

A pure function that derives "why this person matched" from persona↔contact criteria overlaps (roles, seniority, company size, industry, keywords). Zero LLM calls anywhere in discovery.

### API endpoints

| Method | Path | What it does | Throttle |
|---|---|---|---|
| `POST /projects/:id/campaigns/:cid/persona/confirm` | Confirms persona, enqueues discovery job | 5/min |
| `GET /projects/:id/campaigns/:cid/contacts` | Lists discovered contacts (review screen) | — |
| `POST /projects/:id/campaigns/:cid/discovery/retry` | Wipes partial contacts, re-runs discovery | 3/min |

### Web UI states

**DISCOVERING (progress):** Renders a progress indicator with quiet 4s polling (no status flicker; unchanged campaigns are a no-op; hidden tabs skip the fetch). The watcher cleans up on state change or unmount.

**DISCOVERING (error):** Shows inline error + retry button when `discoveryError` is set on the campaign. The retry calls the throttled endpoint, which wipes contacts and re-runs.

**REVIEWING:** Renders contact cards with enrichment summary and match rationale. An enrich-failed (`DISCOVERED`-only) card renders honestly with just identity fields — it says "identity only" instead of pretending to be complete. Uses the existing scoped-list store machinery (cache, coalescing, supersede guard).

**Confirm dialog:** Before confirming the persona (and thus firing discovery), a dismiss-resistant consequence dialog states it's one-way and up to N contacts will be discovered. `Dialog` + `@interact-outside.prevent` — outside-click cannot dismiss it, Escape still closes.

## Why

These design decisions are recorded so a future vendor/tool exploration knows what to revisit and why.

### Mock-first, vendor-agnostic

Only the deterministic mock adapter ships now. The real vendor is deliberately not chosen yet (Apollo/PDL/Bright Data are candidates; Proxycurl's court-ordered death is why this stays behind an adapter — a vendor dying is a config change, not a rewrite). The contacts vendor and the activity vendor may end up being different companies, and that split stays a per-capability config choice behind the registry.

### No email/phone fields

Broker-sourced contact details are where GDPR exposure concentrates (noyb's cases against Apollo/RocketReach; the Art. 14 never-notified problem). They're premium-priced fields (PDL contact match $0.40-0.55 vs $0.28 base enrichment), and nothing can use them yet — no outreach channel exists in this slice. **Revisit when the email channel ships:** re-enrich only the founder-approved contacts at that point — fresher data, fewer records held, pay only for contacts that survived review.

### `recentActivity` is optional and normal-when-absent

Activity/posts are the contested resource post-Proxycurl — Apollo and PDL carry none, Bright Data lags real-time, and remaining options put ToS risk on us. The mock returns a mix of contacts *with* and *without* recentActivity so downstream slices (drafting personalization) handle the degraded vendor shape from day one.

### One job, not fan-out

The hard cap is 50 contacts and nothing here is latency-sensitive. Per-contact job fan-out buys completion-detection and partial-fleet-failure problems at a scale that doesn't need them. **Revisit only if a real vendor's rate limits force it** — the funnel-state field is already in place.

### Match rationale is derived, not LLM-generated

Deterministic, free, keyless — discovery needs zero LLM calls. The LLM-voiced per-contact narrative belongs to the drafting slice, which reads the same contact + persona anyway — one smart pass, not two.

### Failure lives on the campaign, not in the lifecycle

`discoveryError`/`discoveryErrorAt` are written on the campaign only on BullMQ's **final** retry attempt (max 3). State stays `DISCOVERING` ("discovery owed", which failed-retryable still is). The retry endpoint (3/min) clears the error via a state-guarded update and wipes contacts in the same transaction. It also accepts the stranded case (DISCOVERING, no error, no contacts, no job — e.g. Redis was down at confirm). This keeps the lifecycle enum linear for the four later slices built on it.

## Edge cases & gotchas

- **Enrich failure per contact:** leaves that contact at `DISCOVERED` identity-only. Does not fail the whole run. The UI renders an honest "identity only" card.
- **Job exhausted all retries:** writes `discoveryError` on the campaign. State stays `DISCOVERING`. The UI shows the error inline with a retry button.
- **Retry endpoint throttled:** 3 requests per 60 seconds per campaign. Each retry wipes contacts and re-runs discovery. Accepts the stranded case (DISCOVERING, no error, no contacts, no running job).
- **Race on retry during transition:** the retry endpoint uses a state-guarded `update` — if the campaign reached `REVIEWING` mid-race (e.g. the job completed between the client's check and the retry call), Prisma's `P2025` error becomes a 409. Contacts that were already reviewed are never lost.
- **Confirm throttle:** 5/min, separate from the retry throttle. The one-way DRAFT gate already makes repeats 409, but the provider-triggering rule needs an explicit bound.
- **Web discovery poll:** 4s interval, skips on hidden tabs (`document.hidden`). Watcher is cleaned up on state change or component unmount. No SSE yet for discovery progress.
- **Stranded campaigns:** a campaign in DISCOVERING with no error, no contacts, and no running job (e.g. the worker was down at confirm time) — the retry endpoint accepts and recovers it.
- **env.example includes `PEOPLE_DEFAULT_PROVIDER=mock`** — the only provider so far. When a real vendor lands, its id joins the shared enum and its API key gets its own optional env var; an absent key falls back to mock.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/56
- Linear issue: https://linear.app/2builders/issue/2BU-51/contact-discovery-and-enrichment-behind-a-mock-first
- Parent spec: https://linear.app/2builders/issue/2BU-47/spec-outreach-and-ai-interview-validation-loop-phase-2-recruit-real
- Campaign skeleton (preceding slice): https://github.com/Eden-Cohen1/ideascout/pull/52
