---
id: outreach-campaign-skeleton
title: Outreach campaign skeleton
sidebar_position: 1
---

# Outreach campaign skeleton

## Purpose

The outreach system finds and contacts qualified prospects for a founder's idea.
This doc describes the campaign lifecycle, persona confirmation, per-contact
sequence drafting with mode toggling, and the campaign-level approve action that
moves a campaign from review into active sending.

## Behavior

### Campaign lifecycle

The shared package defines these lifecycle states in `CAMPAIGN_LIFECYCLE_STATES`:
`DRAFT`, `DISCOVERING`, `REVIEWING`, `ACTIVE`, and `CONCLUDED`.

- A campaign starts in **`DRAFT`** when created from an existing idea.
- Contact discovery and enrichment run during **`DISCOVERING`**.
- Once all contacts are discovered and sequenced, the campaign enters **`REVIEWING`**
  where the founder reviews each contact's mode and draft sequence.
- The founder **approves** the campaign to move it from `REVIEWING` to `ACTIVE`
  (the previously-defined-but-unused transition, now implemented).
- `CONCLUDED` is reached when the campaign is finished.

### Persona hypothesis gate (PR #53)

Opening a draft campaign derives a persona hypothesis from the idea's research.
The founder corrects or confirms it; confirming the persona is the only way a
campaign leaves `DRAFT`.

- `PersonaHypothesisSchema` models the target persona (roles, seniority, company
  profile, pain rationale, targeting keywords).
- The campaign response carries `persona`, `personaConfirmedAt`,
  `personaResearchGrounded`, `founderIntro`, `defaultContactMode`, and
  `schedulingLink`.
- Persona becomes read-only once confirmed, but `founderIntro`, `defaultContactMode`,
  and `schedulingLink` remain editable after confirmation.
- `AI_INTERVIEW` does not require a scheduling link; `CALL` and `MIX` do.
  `modeRequiresSchedulingLink()` enforces this.

### Contact modes

`CONTACT_MODES` includes `CALL`, `AI_INTERVIEW`, and `MIX`. A per-contact mode
toggle lets the founder override the default.

- Each contact gets an **engine-recommended preset** from enrichment signals:
  senior + low-activity → AI lean; active poster → call lean; otherwise mix.
- The founder can manually toggle a contact's mode at any time during review.

### Per-contact sequences (PR #63)

Every discovered contact gets a **personalized outreach sequence**: an initial
message + up to 2 follow-ups, drafted from the contact's enrichment data and the
founder's introduction.

#### Drafting

- Drafting is handled by `drafting.processor.ts` using an LLM (mock-first,
  keyless-green provider family).
- The LLM drafts only the **personalization body**; the ask sentence and links are
  composed **deterministically** in `sequence-composer.ts`.
- `OutreachSequenceSchema` (a Zod contract in `packages/shared`) validates every
  sequence and refuses any structurally dishonest message — the ask must match
  the contact's mode.
- The sequence is persisted as a validated `Json` column on the `Contact` model
  (mirroring the `enrichment`/`persona` precedent with a boundary `safeParse`).
- A **Regenerate** button triggers a fresh LLM draft (throttled at 5/minute per
  contact).

#### Mode toggling

Switching the mode toggle **instantly recomposes** the messages from the stored
personalization body — no new LLM call. The deterministic composer guarantees:

- **Call mode** — the opener references a scheduling link.
- **AI-interview mode** — the interview link itself is the honest micro-ask;
  no scheduling-link promise.
- **Mix mode** — the message presents both options.

The invariant enforced by construction (not by prompt):
> The ask in the message always matches what the prospect will actually get.

#### Hand edits

The founder can hand-edit any drafted message. Hand-edited text is:

- **Honesty-checked** — `OutreachSequenceSchema` refuses sequences whose ask
  doesn't match the mode.
- **Never silently overwritten** — mode toggling or regeneration that would
  overwrite a hand-edit returns a **409 Conflict** until the founder confirms.
  The founder's own text is preserved verbatim on confirmation.

#### Craft rules

All drafted messages obey these rules (asserted in tests against mock output):

- LinkedIn messages < 400 characters.
- Blank connection request with personalized message after acceptance.
- Interest-based micro-ask — never a "15-minute call" opener.
- Mom-Test advice-ask framing (validating, not selling).
- Genuine 1:1 personalization referencing something specific/recent.
- Max 2–3 touches per sequence (enforced by `OutreachSequenceSchema`, not convention).

### Approve action

The campaign-level approve action implements the `REVIEWING → ACTIVE` transition.
After approving, the campaign is ready for the future send pipeline to materialize
outreach rows from the approved drafts.

## Why

The outreach system exists because manual prospecting doesn't scale for early-stage
founders. Each slice builds toward a fully reviewable campaign:

- **Persona gate** (PR #53, 2BU-49) — the human targeting-quality check that
  prevents wasted outreach. It is deliberately not skippable: the founder must
  confirm who the campaign is aimed at before discovery can start.
- **Per-contact sequences + mode toggle** (PR #63, 2BU-54) — makes every discovered
  contact actionable with a personalized draft. The mode recommendation heuristics
  are presets, not decisions, keeping the heuristic simple and inspectable.
  The deterministic composition of asks (not prompt-based) is the key invariant:
  the message a prospect sees must match the mode the founder chose, by
  construction, not by hope.

## Edge cases & gotchas

- A campaign can derive a persona even when the underlying research is incomplete;
  the UI marks `personaResearchGrounded: false` and warns about lower accuracy.
- Invalid scheduling links are rejected; the stored link must be an `http(s)` URL.
- On mode toggle, hand-edit preservation produces a 409 that the UI must surface
  as a confirmation dialog — the founder must explicitly confirm overwrite.
- Draft regeneration is throttled (5/min); the throttle applies per contact, not
  per campaign.
- The campaign remains in `REVIEWING` until the founder explicitly approves it.
  Draft messages are not sent until the future send pipeline materializes rows
  from the approved state.

## Screenshots

The PR includes a full screenshot set under `docs/screenshots/2bu-54/`. The most
representative states are below.

| State | Screenshot |
| --- | --- |
| Drafting in progress after discovery | ![Drafting in progress](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/01-drafting-in-progress.png) |
| Review panel with per-contact sequences | ![Review with sequences](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/02-review-with-sequences.png) |
| Mode toggle with engine-recommended preset | ![Mode toggle suggested](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/03-mode-toggle-suggested.png) |
| AI-only mode — recomposed messages | ![AI-only recomposed](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/04-ai-only-recomposed.png) |
| Hand-editing a drafted touch | ![Edit touch](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/05-edit-touch.png) |
| Confirm-overwrite dialog for hand edits | ![Confirm overwrite dialog](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/06-confirm-overwrite-dialog.png) |
| Draft error and regenerate | ![Draft error regenerate](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/07-draft-error-regenerate.png) |
| Approve dialog | ![Approve dialog](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/08-approve-dialog.png) |
| Approved campaign in ACTIVE state | ![Approved active](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/09-approved-active.png) |
| Review panel on narrow viewport | ![Review narrow](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/ece14a55e339/docs/screenshots/2bu-54/10-review-narrow.png) |

## References

- Source PR #53 (persona gate): https://github.com/Eden-Cohen1/ideascout/pull/53
- Source PR #63 (sequences + mode toggle): https://github.com/Eden-Cohen1/ideascout/pull/63
- Linear issue (2BU-54): https://linear.app/2builders/issue/2BU-54/per-contact-personalized-sequences-with-callaimix-mode-toggle
- Parent spec (2BU-47): https://linear.app/2builders/issue/2BU-47/spec-outreach-and-ai-interview-validation-loop-phase-2-recruit-real

<!-- provenance: updated from PR #63 (feat(outreach): per-contact personalized sequences with call/AI/mix mode toggle), reconciled 2026-07-20 -->
