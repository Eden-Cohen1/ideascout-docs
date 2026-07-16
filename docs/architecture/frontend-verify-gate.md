---
id: frontend-verify-gate
title: Frontend verification gate and testing reference
sidebar_position: 4
---

# Frontend verification gate and testing reference

## Purpose

`frontend-task` is how the team builds an `apps/web` screen. `frontend-verify` is the closing gate that checks the result before the work is called done, and `references/testing.md` tells new frontend work what to test by default. `references/performance.md` now gives the scaling thresholds and toolkit for data-heavy screens.

## Behavior

- `frontend-verify` is scoped to `apps/web` work and is invoked when a frontend change needs verification before merge or handoff.
- It runs `verify:web` first. That command is the deterministic gate for the workspace.
- After the gate passes, the skill performs three judgment passes that scripts cannot do:
  - UI/UX and accessibility review against `apps/web/DESIGN.md` and the `pro-graphite.html` reference, with attention to tokens-only usage, loading/empty/error/success states, keyboard reachability, visible focus, restraint, and responsive behavior.
  - Architecture review for downward-only layering and centralized error handling, while composing `/code-review` instead of duplicating it.
  - Performance and scalability review for bounded list and payload size, pagination or incremental render where needed, cache/revisit behavior, request cancellation, leaked observers/listeners, and avoiding premature virtualization for realistically small lists.
- `frontend-task/references/testing.md` captures the testing baseline for `apps/web`: store actions, error paths, composables, and component states. It also standardizes colocated specs and the Vitest/Vue Test Utils style.
- `frontend-task/references/performance.md` captures the scaling toolkit for `apps/web`: cursor pagination, infinite scroll, virtualization, stale-while-revalidate caching, request cancellation, and memory hygiene, plus the rough thresholds for when each becomes worth it.
- The skill produces a `PASS` or `CHANGES NEEDED` verdict. It does not claim `PASS` unless it actually ran the gate.

## Why

The linked Linear issue says `frontend-task` covers how to build a screen, but verification had only a manual checklist. This adds a dedicated verification skill so every frontend change is checked the same way, plus testing and performance references so screens ship with tests by default and data-heavy screens are reviewed against realistic scale instead of by guesswork.

## Edge cases & gotchas

- This change is docs/skills only; it does not change user-facing app behavior.
- `verify:web` and `token-lint` are out of scope for this PR. The skill depends on them, but it does not define them.
- `frontend-verify` is a verification pass, not a replacement for `frontend-task` or `code-review`.
- The testing reference is a guidance page, not a mandate to test framework internals or CSS pixel output.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/41
- Linear issue: https://linear.app/2builders/issue/2BU-36/add-a-performance-and-scalability-audit-to-frontend-verify-performance

<!-- provenance: drafted from ideascout PR #41 -->
