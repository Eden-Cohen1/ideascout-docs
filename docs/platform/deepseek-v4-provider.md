---
id: deepseek-v4-provider
title: DeepSeek V4 provider
sidebar_position: 1
---

# DeepSeek V4 provider

This page documents the DeepSeek V4 LLM path in ideascout: the default provider, the
provider-specific model toggle, and the per-step thinking mode used by the judgment steps.

## Behavior

- `LLM_DEFAULT_PROVIDER` now defaults to `deepseek`.
- `DEEPSEEK_API_KEY` enables the real DeepSeek provider; when no provider key is configured,
  the provider registry falls back to deterministic `mock` mode.
- `LLM_DEFAULT_MODEL` is provider-global. For DeepSeek it selects between
  `deepseek-v4-flash` (default) and `deepseek-v4-pro`.
- The shared LLM interface now accepts `reasoningEffort?: 'none' | 'high' | 'max'`.
- DeepSeek V4 maps `reasoningEffort` to its thinking mode and forces thinking off unless a
  caller opts in.
- The Moat analysis and Verdict pipeline steps opt into `reasoningEffort: 'high'`.
- DeepSeek V4 does not use `seed`.
- `OpenAiCompatibleProvider` now holds the shared OpenAI-compatible wire logic; the OpenAI
  adapter is a thin subclass of it.

## Why

Open question: the merged source PR does not link a Linear issue, so the product rationale
for making DeepSeek the default provider is not documented in the source materials available
to the docs agent.

## Edge cases & gotchas

- `LLM_DEFAULT_MODEL` is global across providers, so a DeepSeek model override affects any
  provider that reads the same setting.
- Thinking mode is only enabled where the pipeline explicitly requests it. That keeps the
  extraction/structuring path non-thinking.
- If `DEEPSEEK_API_KEY` is unset, the app stays usable in deterministic mock mode.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/15
- Linear issue: none found

<!-- provenance: reconciled from ideascout PR #15 on 2026-07-11 -->
