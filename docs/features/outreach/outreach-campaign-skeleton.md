---
id: outreach-campaign-skeleton
title: Outreach campaign skeleton
sidebar_position: 1
---

# Outreach campaign skeleton

## Purpose

PR #53 extends the first outreach slice from PR #52 with the persona hypothesis gate.
Opening a draft campaign now derives a persona hypothesis from the idea's research,
the founder corrects or confirms it, and confirming it is the only way a campaign
leaves `DRAFT`.

## Behavior

- Shared package:
  - `CAMPAIGN_LIFECYCLE_STATES` still includes `DRAFT`, `DISCOVERING`, `REVIEWING`,
    `ACTIVE`, and `CONCLUDED`.
  - `PersonaHypothesisSchema` models the target persona with roles, seniority,
    company profile, pain rationale, and targeting keywords.
  - `CONTACT_MODES` includes `CALL`, `AI_INTERVIEW`, and `MIX`.
  - `modeRequiresSchedulingLink()` requires a scheduling link for call-bearing modes,
    but not for `AI_INTERVIEW`.
  - `CreateCampaignRequestSchema`, `CampaignResponseSchema`, and the new update schema
    live in `@ideascout/shared` and are exported from the shared index.
  - `maxContacts` still defaults to 50 and is still hard-capped at 50.
- Campaign data:
  - Campaign responses now carry `persona`, `personaConfirmedAt`,
    `personaResearchGrounded`, `founderIntro`, `defaultContactMode`, and
    `schedulingLink`.
  - Draft campaigns can be updated with persona and campaign-level inputs before the
    founder confirms the gate.
  - The campaign keeps the founder's default contact mode, and the scheduling link is
    only meaningful when the mode includes a call.
- API:
  - Validation-campaign routes are still nested under `projects/:projectId/campaigns`.
  - `POST` still creates a draft campaign from an existing idea.
  - The new persona-derivation / persona-confirmation flow is the only exit from `DRAFT`.
  - The campaign's conversation settings stay editable after confirmation, but the
    persona itself becomes read-only once confirmed.
  - `JwtAuthGuard` and `ProjectAccessGuard` still gate every route.
- Web:
  - `CampaignDetailView` now renders the persona gate on draft campaigns and a read-only
    summary once the persona is confirmed.
  - The detail view also surfaces the default contact mode and the discovery-note state
    once the campaign reaches `DISCOVERING`.
  - The web app adds the persona gate UI needed to keep the draft editable until the
    founder approves it.
- This slice still keeps the broader outreach flow staged: later discovery and interview
  work continues after the confirmed persona is in place.

## Screenshots

The PR includes a full screenshot set under `docs/screenshots/2bu-49/`. The most
representative states are below.

| State | Screenshot |
| --- | --- |
| Deriving on first open | ![Deriving](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/a113ea2a27226c6160e0ef45adf26d0776e16879/docs/screenshots/2bu-49/01-deriving.jpg) |
| Gate editing with research warning | ![Gate editing](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/a113ea2a27226c6160e0ef45adf26d0776e16879/docs/screenshots/2bu-49/02-gate-editing-research-warning.jpg) |
| Mode: Both | ![Mode both](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/a113ea2a27226c6160e0ef45adf26d0776e16879/docs/screenshots/2bu-49/03-gate-mode-both.jpg) |
| Confirmed settings card | ![Confirmed](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/a113ea2a27226c6160e0ef45adf26d0776e16879/docs/screenshots/2bu-49/06-confirmed-settings-card.jpg) |

## Why

The persona gate is the human targeting-quality check that protects make-good
 economics for the outreach campaign. It is deliberately not skippable: the founder
 must confirm who the campaign is aimed at before outreach can start. The scheduling
 link is optional when the founder is running a text-only / AI-interview-only mode,
 so the gate does not force a booking URL onto founders who do not need one.

## Edge cases & gotchas

- A campaign can derive a persona even when the underlying research is incomplete; in
  that case the UI marks `personaResearchGrounded: false` and warns that targeting
  accuracy may be lower.
- `AI_INTERVIEW` does not require a scheduling link, but `CALL` and `MIX` do.
- Invalid scheduling links are rejected; the stored link must be an `http(s)` URL.
- Once the persona is confirmed, the persona itself is locked, but the campaign-level
  intro, contact mode, and scheduling link remain editable.
- The campaign is still not a full outreach engine yet; contact discovery and the later
  interview stages are still staged behind the confirmed persona.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/53
- Linear issue: https://linear.app/2builders/issue/2BU-49/persona-hypothesis-confirmation-gate-before-any-outreach
- Parent spec: https://linear.app/2builders/issue/2BU-47/spec-outreach-and-ai-interview-validation-loop-phase-2-recruit-real

<!-- provenance: drafted from ideascout PR #53 -->

