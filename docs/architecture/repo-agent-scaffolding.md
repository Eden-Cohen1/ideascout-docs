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

Open question: the PR does not include a linked Linear issue or another explicit rationale for
why these agent instructions were vendored into the repo, or why the skill-set collision
cleanup needed to land now. The doc can safely say what changed, but the business reason for
preserving this setup in canonical docs still needs confirmation before publish.

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
