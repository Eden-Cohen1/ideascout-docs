---
id: depth-quality-spike
title: 2BU-19 search-depth spike results
sidebar_position: 4
---

# 2BU-19 search-depth spike results

This page records the 2026-07-12 spike that measured research quality versus cost as search depth increased. The source PR archived the raw run data in `scripts/spike-2bu19/` and concluded that deeper corpus rendering was the best quality-per-dollar knob.

## Purpose

Capture the measured tradeoff so future depth-tuning decisions have a stable reference instead of re-running the spike from memory.

## Behavior

- The spike compared 3 fixed ideas:
  - MealMind — crowded consumer
  - CrownAudit — thin evidence / niche B2B
  - AgentMeter — emerging category
- It ran QUICK, DEEP, and DEEP + 4000/3000 corpus truncation.
- Config D (extra coverage iteration) stayed registered but was skipped because `remainingGaps` was 0 on every idea.
- All runs used the real DeepSeek + Brave path.
- Judged quality was monotone: QUICK < DEEP < DEEP + fat corpus on all 3 ideas.
- The fat-corpus variant won the blind pairwise comparison 3/3.
- The write-up’s recommendation was to make DEEP use 4000/3000 truncation by default and keep QUICK unchanged as the cheap screening tier.
- The spike also exposed a verdict-stability problem: identical QUICK runs could flip between NO_GO and CONDITIONAL_GO.
- A NUL-byte artifact crash showed up in the DEEP path and needs a production fix.
- The cost model was too pessimistic: a full DEEP+corpus run landed around $0.16, not the earlier $0.70–1.20 estimate.

## Why

The 2BU-19 issue asked whether better search depth buys enough quality to justify the extra spend. The spike’s answer was yes for DEEP truncation, but the bigger remaining problem is verdict stability, not raw depth.

## Edge cases & gotchas

- QUICK is still useful as a cheap screen, but its verdict category wobbled on the same idea.
- The extra coverage step is conditional, not part of the steady-state path.
- The measured cost was dominated by search spend, not DeepSeek input tokens.
- The blind judge could partially identify QUICK runs from their smaller competitor-map footprint.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/28
- Linear issue: https://linear.app/2builders/issue/2BU-19/investigate-research-quality-vs-cost-by-tweaking-search
- Raw artifacts: `scripts/spike-2bu19/`

<!-- provenance: drafted from ideascout PR #28 -->
