---
id: llm-provider-stack
title: LLM provider stack
sidebar_position: 2
---

# LLM provider stack

This page documents the LLM adapter layer used by ideascout after PR #15.

## Purpose

Keep provider-specific HTTP, streaming, and vendor quirks behind a stable `LlmProvider`
contract so the pipeline can select a provider/model without knowing which vendor is serving
it.

## Behavior

- The provider id list is fixed in shared code: `deepseek`, `openai`, `anthropic`, `gemini`,
  and `mock`.
- `LLM_DEFAULT_PROVIDER` now defaults to `deepseek`.
- The registry resolves a requested provider first, then the configured default provider, and
  finally `mock` when the selected provider is unavailable or unregistered.
- `providerKey(id)` maps `deepseek` to `DEEPSEEK_API_KEY`, `openai` to `OPENAI_API_KEY`,
  `anthropic` to `ANTHROPIC_API_KEY`, and `gemini` to `GEMINI_API_KEY`.
- `OpenAiCompatibleProvider` owns the shared chat-completions and SSE streaming logic for
  OpenAI-compatible providers.
- `DeepSeekLlmProvider` is an OpenAI-compatible adapter with:
  - default model `deepseek-v4-flash`
  - endpoint `https://api.deepseek.com/chat/completions`
  - `seed` omitted
  - `thinking` disabled unless a call passes `reasoningEffort`
- Structured calls use the shared JSON/zod helper. The helper appends a JSON-only directive,
  retries once on schema failure, and records usage for the run.
- `ANALYZE` and `VERDICT` call the reasoning model with `reasoningEffort: 'high'`.
  `CLASSIFY` uses the fast model and does not request reasoning mode.
- `VERDICT` computes score, confidence, verdict, and lean in code; the model only supplies
  the narrative fields.

## Why

The implementation keeps model selection and vendor-specific transport in the adapter layer,
so pipeline steps can stay vendor-neutral. That lets ideascout swap providers by changing
configuration and registry wiring instead of rewriting step logic.

## Edge cases & gotchas

- DeepSeek and OpenAI-compatible structured calls need a JSON instruction in the prompt; the
  shared helper adds it automatically.
- DeepSeek V4 appears to default `thinking` on upstream, so the adapter explicitly disables it
  unless a caller opts in.
- If a provider key is missing, the app falls back to `mock` and still runs end to end.
- `stream()` on OpenAI-compatible providers is true SSE parsing, not a fake chunk splitter.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/15
- Source repo: https://github.com/Eden-Cohen1/ideascout

<!-- provenance: reconciled against ideascout PR #15 (merged 2026-07-04) -->
