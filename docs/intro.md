---
id: intro
title: Documentation home
sidebar_position: 1
slug: /
---

# ideascout documentation

This site is the **canonical documentation** for ideascout. It is maintained by the
Hermes docs agent: when a pull request merges into
[`Eden-Cohen1/ideascout`](https://github.com/Eden-Cohen1/ideascout), the agent evaluates
whether the docs need to change and, if so, opens a documentation pull request here for
human review before anything is published.

Browse the docs by product area: **Authentication**, **Workspaces**, **Research**, and
**Platform**.

## How this works

- Every page under **Docs** is plain Markdown committed to the
  [`ideascout-docs`](https://github.com/Eden-Cohen1/ideascout-docs) repository.
- Pages are grouped by feature so related flows live together instead of being buried in a
  single architecture bucket.
- Changes arrive as pull requests on `proposal/*` branches. Vercel builds a **preview** of
  each proposal so you can read the rendered page before it merges.
- A page only reaches production after a human approves it in Slack (`#docs-agent`) and the
  proposal PR is merged into `main`.

## Provenance

Each agent-authored page ends with a provenance line noting the source PR(s) it was derived
from and the date it was last reconciled. If a page looks stale, that line tells you which
code change it was last checked against.
