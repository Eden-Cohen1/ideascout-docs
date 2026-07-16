---
id: web-verification-gate
title: Web verification gate and design-token enforcement
sidebar_position: 4
---

# Web verification gate and design-token enforcement

This page documents the web-side verification gate added in ideascout PR #31 and tightened
in PR #47: the one-command `verify:web` check, the design-token lint step for Vue
components, and the CI wiring that runs both automatically.

## Behavior

- `npm run verify:web` at the repo root runs the web gate as a fail-fast chain:
  `typecheck → lint → format:check → test` for `@ideascout/web` →
  `lint:cycles` for `@ideascout/web` → `token-lint` for `@ideascout/web`.
- `apps/web/package.json` adds `token-lint`, which runs `apps/web/scripts/token-lint.mjs`.
- `apps/web/scripts/token-lint.mjs` scans `apps/web/src/**/*.vue` and fails on anything that
  bypasses the color/font tokens:
  - **Literal colors** — hex colors, `rgb()/rgba()`, `hsl()/hsla()`, `oklch()/oklab()`, and
    arbitrary color values such as `text-[#...]` or `bg-[rgb(...)]`.
  - **Raw Tailwind palette utilities** — `bg-slate-500`, `hover:text-gray-400`,
    `dark:border-zinc-200/80`, and similar variants. Use semantic tokens like `bg-muted`,
    `text-muted-foreground`, and `border-border` instead.
  - **Pure white/black utilities** — `bg-white`, `text-black`, and similar bypasses of the
    semantic background/foreground tokens.
  - **Hardcoded fonts** — `font-family: 'Inter', ...` in scoped CSS and arbitrary font
    utilities like `font-['Inter']` or `font-[550]`. Use `font-sans` / `font-mono`.
  - Variant prefixes (`hover:`, `dark:`) and `/opacity` modifiers are handled.
- `token-lint` supports narrow opt-outs with `token-lint-disable-line` and
  `token-lint-disable-file`.
- `.github/workflows/ci.yml` adds the web circular-dependency and design-token checks to the
  CI quality job.
- `eslint.config.mjs` grants Node globals to `.mjs` tooling scripts so the new linter script
  can run cleanly.
- `apps/web/DESIGN.md` records the enforcement model: a deterministic lint gate plus human
  review for judgment calls that a regex cannot make.

## Why

The PR turns the frontend rule of “no raw colors/fonts in components” into an enforceable
gate: a single command for local verification, deterministic lint coverage for the raw
Tailwind/font bypasses that human review used to catch, and CI enforcement so the check cannot
be skipped.

## Edge cases & gotchas

- `token-lint` is intentionally narrow. It catches the literal color and font bypasses above,
  but it still does not judge whether a token choice is semantically the right one for the
  UI. That part stays in review.
- The guard only scans `apps/web/src/**/*.vue`, so it is aimed at component markup rather
  than the whole repository.
- If a raw value is genuinely unavoidable, use the line/file disable comments and explain
  why nearby.
- `verify:web` is a web-focused gate; it sits alongside the repo-wide checks rather than
  replacing them.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/47
- Prior source PR: https://github.com/Eden-Cohen1/ideascout/pull/31
- Linear issue: not linked in the source PR metadata

<!-- provenance: draft from ideascout PR #47 -->
