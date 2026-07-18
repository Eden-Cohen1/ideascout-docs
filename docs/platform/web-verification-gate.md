---
id: web-verification-gate
title: Web verification gate and design-token enforcement
sidebar_position: 6
---

# Web verification gate and design-token enforcement

This page documents the web-side verification gate: the one-command `verify:web` check,
the design-token lint step for Vue components (`token-lint`), the WCAG 2.2 contrast guard
(`contrast-check`), and the CI wiring that runs them automatically. The gate was added in
PR #31, tightened in PR #47 (with the `token-lint` scan), and extended with contrast
checking in PR #49.

## Behavior

- `npm run verify:web` at the repo root runs the web gate as a fail-fast chain:
  `typecheck → lint → format:check → test` for `@ideascout/web` →
  `lint:cycles` for `@ideascout/web` → `token-lint` for `@ideascout/web` →
  `contrast-check` for `@ideascout/web`.
- `apps/web/package.json` defines two tooling scripts:
  - `token-lint` runs `apps/web/scripts/token-lint.mjs`.
  - `contrast-check` runs `apps/web/scripts/contrast-check.mjs`.
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
- `apps/web/scripts/contrast-check.mjs` recomputes WCAG 2.2 AA for every declared token
  pair in both light and dark themes. It parses the hex tokens from the `:root` and `.dark`
  blocks in `src/style.css` and verifies each required pairing (body text: 4.5:1, large
  text/UI: 3:1). A palette edit that breaks accessibility fails the build.
- `.github/workflows/ci.yml` adds the web circular-dependency, design-token, and contrast
  checks to the CI quality job.
- `eslint.config.mjs` grants Node globals to `.mjs` tooling scripts so the lint and contrast
  scripts can run cleanly.
- `apps/web/DESIGN.md` records the enforcement model: a deterministic lint gate plus human
  review for judgment calls that a regex cannot make, and contrast-check as a numeric gate
  that no palette change can silently regress. The design tokens table now includes
  `--auth-panel` / `--auth-panel-foreground` (scoped to `AuthShell` only), and `contrast-check`
  verifies this pair against WCAG AA.

## Why

The PR turns the frontend rule of “no raw colors/fonts in components” into an enforceable
gate: a single command for local verification, deterministic lint coverage for the raw
Tailwind/font bypasses that human review used to catch, and CI enforcement so the check cannot
be skipped. The contrast-check gate ensures that any future palette edit either keeps or
improves accessibility — it's a numeric guarantee that human review cannot provide.

## Edge cases & gotchas

- `token-lint` is intentionally narrow. It catches the literal color and font bypasses above,
  but it still does not judge whether a token choice is semantically the right one for the
  UI. That part stays in review.
- The guard only scans `apps/web/src/**/*.vue`, so it is aimed at component markup rather
  than the whole repository.
- If a raw value is genuinely unavoidable, use the line/file disable comments and explain
  why nearby.
- `contrast-check` only validates the token pairs declared in `style.css` — it does not
  verify runtime CSS variable resolution in components. A component that builds a color
  from raw CSS variables bypasses both `token-lint` and `contrast-check`.
- `verify:web` is a web-focused gate; it sits alongside the repo-wide checks rather than
  replacing them.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/49
- Prior source PR: https://github.com/Eden-Cohen1/ideascout/pull/47
- Prior source PR: https://github.com/Eden-Cohen1/ideascout/pull/31
- Linear issue: https://linear.app/2builders/issue/2BU-40/add-marketing-home-page-as-public-entry-point-before-login

<!-- provenance: drafted from ideascout PR #49; updates from PR #31 and PR #47 preserved -->
