---
id: llm-provider-configuration
title: LLM provider configuration
sidebar_position: 10
---

# LLM provider configuration

ideascout's API chooses a default LLM provider at boot, and the research pipeline uses a shared provider interface for chat, structured output, and streaming calls.
This page covers the current provider wiring, the DeepSeek V4 default, and the per-step reasoning mode used by the pipeline.

## Provider selection

| Env var | Meaning |
| --- | --- |
| `LLM_DEFAULT_PROVIDER` | Provider id selected at boot. Defaults to `deepseek`. |
| `LLM_DEFAULT_MODEL` | Optional model override. It is global, so only set it to a model name that exists on the active provider. |
| `DEEPSEEK_API_KEY` | API key for DeepSeek V4. |
| `OPENAI_API_KEY` | API key for OpenAI. |
| `ANTHROPIC_API_KEY` | API key for Anthropic. |
| `GEMINI_API_KEY` | API key for Gemini. |

Supported provider ids are `deepseek`, `openai`, `anthropic`, `gemini`, and `mock`.
The `mock` provider has no API key and is the deterministic fallback when a real provider is unavailable.

## DeepSeek V4 behavior

DeepSeek uses the OpenAI-compatible chat completions endpoint at `https://api.deepseek.com/chat/completions`.
Its default model is `deepseek-v4-flash`; `deepseek-v4-pro` is the stronger tier.
The adapter does not send `seed` and treats thinking as opt-in.

| `reasoningEffort` | DeepSeek request body |
| --- | --- |
| omitted or `none` | thinking disabled |
| `high` or `max` | thinking enabled with the matching `reasoning_effort` value |

## Pipeline usage

The research pipeline enables `reasoningEffort: 'high'` on the `MOAT_ANALYSIS` and `VERDICT` steps.
The earlier extraction and grounding steps stay non-thinking so their structured output remains stable.
Every provider still implements the same `LlmProvider` interface, so the rest of the app does not depend on a vendor SDK.

## Open question

:::note intent needed
What should the docs say about the product rationale for making DeepSeek V4 the default provider, and for limiting thinking mode to the moat and verdict steps?
:::

## Related

- [Docs agent architecture](./docs-agent)
- [Documentation home](../intro)

<!-- provenance: derived from PR #15 (DeepSeek V4 LLM provider and thinking mode), reconciled 2026-07-11 -->
