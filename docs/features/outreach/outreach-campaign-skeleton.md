---
id: outreach-campaign-skeleton
title: Outreach campaign skeleton
sidebar_position: 1
---

# Outreach campaign skeleton

## Purpose

PR #52 adds the first outreach slice: founders can create a validation campaign from an existing idea, then view it in the new Outreach area. It establishes the shared contract, API, Prisma model, and web surface for future outreach work.

## Behavior

- Shared package:
  - `CAMPAIGN_LIFECYCLE_STATES` includes `DRAFT`, `DISCOVERING`, `REVIEWING`, `ACTIVE`, and `CONCLUDED`.
  - `CreateCampaignRequestSchema` and `CampaignResponseSchema` live in `@ideascout/shared` and are exported from the shared index.
  - `maxContacts` defaults to 50 and is hard-capped at 50.
- API:
  - Validation-campaign routes are nested under `projects/:projectId/campaigns`.
  - `POST` creates a draft campaign from an existing idea.
  - `GET` lists a project's campaigns, newest first.
  - `GET :campaignId` fetches a single campaign in the project.
  - `JwtAuthGuard` and `ProjectAccessGuard` gate every route.
  - Campaign creation checks that the idea belongs to the same project; missing or cross-project ideas return 404.
  - Responses include the idea title plus created/updated timestamps.
  - The Prisma model stores the campaign, its project and idea foreign keys, lifecycle state, and max-contact bound.
- Web:
  - The app shell now exposes an Outreach route.
  - `OutreachView` shows the campaign list and a new-campaign panel.
  - `CampaignDetailView` renders the detail screen for a created campaign.
  - The web app adds campaign and idea API wrappers plus Pinia stores for both.
  - The UI covers loading, empty, error, and success states, and uses a lifecycle badge for the campaign state.
- This slice stops at `DRAFT`; transitions to later lifecycle states are deferred.

## Why

This is the steel thread for the phase-2 outreach flow described in 2BU-47 and 2BU-48. The intended product move is to let a founder start from an idea they already have, create a bounded validation campaign, and then build the rest of the recruiting and interview loop on top of a real campaign record instead of a one-off UI flow.

## Edge cases & gotchas

- Omitting `maxContacts` uses the default of 50; values above 50 are rejected.
- Campaign routes are nested under projects, so access depends on project ownership rather than a campaign-specific guard.
- Creating a campaign for an idea in another project returns 404, not 403.
- The shared lifecycle enum already includes future states even though this slice only emits `DRAFT`.
- This PR does not implement persona discovery, contact discovery, interview flows, or any state transitions beyond `DRAFT`.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/52
- Linear issue: https://linear.app/2builders/issue/2BU-48/outreach-campaign-skeleton-create-a-validation-campaign-from-an
- Parent spec: https://linear.app/2builders/issue/2BU-47/spec-outreach-and-ai-interview-validation-loop-phase-2-recruit-real

<!-- provenance: drafted from ideascout PR #52 -->
