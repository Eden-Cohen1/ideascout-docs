---
id: repo-agent-scaffolding
title: Repo agent scaffolding
sidebar_position: 6
---

# Repo agent scaffolding

This page documents the repo-local agent guidance added in ideascout PR #43 and refined in
PR #44: the vendored `.claude/skills/` tree, the top-level `CLAUDE.md`, the root
`CONTEXT-MAP.md`, the static `docs/agents/skills-map.md` guide, and the `docs/agents/`
guidance pages.

## Purpose

Keep the repository's agent instructions, issue-tracker convention, and domain-map guidance
close to the codebase so team agents read the same repo-local rules instead of relying on
personal setup.

## Behavior

- `CLAUDE.md` gives the repo's agent-facing operating notes:
  - phase scope and monorepo layout
  - TypeScript, adapter, mock-first, and access-control conventions
  - Swagger/OpenAPI expectations for API changes
  - dependency, testing, and secret-handling norms
  - a short `Agent skills` section that points at the repo-local guidance files
- `docs/agents/issue-tracker.md` says work tracking lives in Linear, team `2builders`
  (`2BU-*`), and that GitHub Issues are not used for repo work tracking.
- `docs/agents/domain.md` says this is a multi-context repo and tells agent workflows to read
  `CONTEXT-MAP.md` plus any relevant `docs/adr/` entries before exploring a topic.
- `CONTEXT-MAP.md` indexes the three repo contexts — shared contracts, API, and web — and
  points at the intended `CONTEXT.md` files for each.
- The map also says context files and ADR folders are created lazily, so a pointer can exist
  before the target file does.
- The vendored `.claude/skills/` directory makes the team skill set live in the repo instead
  of only in a personal workspace.
- `docs/agents/skills-map.md` is the static task→skill map. It splits the repo's skills into
  auto skills and slash-only skills, and it points people to `/ask-matt` when they need the
  router to decide.
- `CLAUDE.md` now points at that map and gives the short rule of thumb for the main splits:
  `apps/web` work → `frontend-task` / `frontend-verify`; backend / `packages/shared` /
  infra → `/implement`; issue authoring → `linear-issue`.
- `/ask-matt` was expanded with the repo's project-specific skill boundaries so the router
  can surface the right choice instead of leaving the generic and repo-local skills blurred
  together.
- The skill set itself was reshuffled so the repo has one clear choice per task: `spec-review`
  now names standards + spec conformance, while a few overlapping tools were pushed to
  slash-only use.

## Why

The stated goal (source PR #44) is to make the repo's own skills and the vendored Matt Pocock
skills read as **one coherent system with a single clear choice per task** — resolving name
collisions (notably `code-review` → `spec-review`), demoting directly-competing tools to
slash-only, and adding the task→skill map plus cross-referenced boundaries so neither the model
nor a person is left guessing which skill to reach for. Vendoring the skills into the repo
(source PR #43) keeps that guidance versioned with the codebase rather than in a personal setup.

Open question: neither PR links a Linear issue, so there is no tracked initiative to point at
for the longer-term intent — worth a human confirmation before publish, but the change itself is
well-motivated in the PR descriptions.

## Edge cases & gotchas

- `CONTEXT-MAP.md` can legitimately point at files that do not exist yet.
- `docs/agents/domain.md` explicitly says to proceed silently if a referenced glossary or ADR
  file is absent.
- The issue-tracker guide is repo policy, not a request to migrate anything back into GitHub
  Issues.
- The vendored skills are repo content, but this page should not try to summarize each skill's
  behavior individually.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/44
- Prior source PR: https://github.com/Eden-Cohen1/ideascout/pull/43

<!-- provenance: drafted from ideascout PR #44 -->
