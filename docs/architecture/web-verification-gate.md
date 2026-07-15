---
id: web-verification-gate
title: Web verification gate and design-token enforcement
sidebar_position: 4
---

# Web verification gate and design-token enforcement

This page documents the web-side verification gate added in ideascout PR #31: the one-command
`verify:web` check, the design-token lint step for Vue components, and the CI wiring that
runs both automatically.

## Behavior

- `npm run verify:web` at the repo root runs the web gate as a fail-fast chain:
  `typecheck → lint → format:check → test` for `@ideascout/web` →
  `lint:cycles` for `@ideascout/web` → `token-lint` for `@ideascout/web`.
- `apps/web/package.json` adds `token-lint`, which runs `apps/web/scripts/token-lint.mjs`.
- `apps/web/scripts/token-lint.mjs` scans `apps/web/src/**/*.vue` and fails on literal color
  values: hex colors, `rgb()/rgba()`, `hsl()/hsla()`, `oklch()/oklab()`, and arbitrary color
  values such as `text-[#...]` or `bg-[rgb(...)]`.
- `token-lint` supports narrow opt-outs with `token-lint-disable-line` and
  `token-lint-disable-file`.
- `.github/workflows/ci.yml` adds the web circular-dependency and design-token checks to the
  CI quality job.
- `eslint.config.mjs` grants Node globals to `.mjs` tooling scripts so the new linter script
  can run cleanly.
- `apps/web/DESIGN.md` records the enforcement model: a deterministic lint gate plus human
  review for judgment calls that a regex cannot make.

## Why

The PR frames this as a no-regression gate for the frontend: a single command for local
verification, a narrow rule that keeps literal colors out of Vue components without creating
noise, and CI enforcement so the check cannot be skipped.

## Edge cases & gotchas

- `token-lint` is intentionally narrow. It catches literal color values, but it does not try
  to judge whether a Tailwind palette utility like `bg-slate-50` is semantically correct.
  That part stays in review.
- The guard only scans `apps/web/src/**/*.vue`, so it is aimed at component markup rather
  than the whole repository.
- If a raw value is genuinely unavoidable, use the line/file disable comments and explain
  why nearby.
- `verify:web` is a web-focused gate; it sits alongside the repo-wide checks rather than
  replacing them.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/31
- Linear issue: https://linear.app/2builders/issue/2BU-24/add-web-verification-gate-token-lint-one-command-verifyweb-ci-wiring

<!-- provenance: draft from ideascout PR #31 -->
