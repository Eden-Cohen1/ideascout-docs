---
id: email-service
title: Transactional email service
sidebar_position: 3
---

# Transactional email service

This page documents the reusable, mock-first email subsystem added in ideascout PR #37. It
covers the adapter/registry pattern, the asynchronous send path, and the local dev fallback
that keeps the app usable with no real email credentials.

## Purpose

Provide one stable surface for transactional mail so future verification, password reset, and
notification flows can send email without knowing which provider is active.

## Behavior

- `EmailService` is the only app-facing send surface. Callers pass structured content, and the
  service renders it into HTML + plaintext before enqueuing a BullMQ `email` job.
- Jobs are retried automatically with exponential backoff. The HTTP request path never blocks on
  a provider call.
- `EmailRegistry` selects the adapter at send time. `EMAIL_PROVIDER` wins when that adapter is
  registered and available; otherwise the registry falls back to the always-available `mock`
  adapter.
- The registered adapters are:
  - `mock` — captures messages in memory and logs a summary line.
  - `smtp` — Nodemailer against `SMTP_URL`.
  - `resend` — HTTP delivery against `RESEND_API_KEY`.
- `EMAIL_PROVIDER`, `EMAIL_FROM`, `RESEND_API_KEY`, `SMTP_URL`, and `APP_WEB_URL` are optional.
  With nothing configured, the app stays runnable and email is captured instead of sent.
- `docker-compose.override.yml` adds Mailpit for local preview. Set `EMAIL_PROVIDER=smtp` and
  `SMTP_URL=smtp://localhost:1025`, then view the inbox at `http://localhost:8025`.
- The worker now runs a dedicated email queue alongside research jobs.

## Why

The linked Linear issue frames this as a reusable seam: every future email should share the same
adapter/registry contract, and mock must be first-class so shipping the seam does not require a
real mail account. The source PR explicitly says this work is additive, does not change any
user-facing behavior, and unblocks the later verification/reset flows.

## Edge cases & gotchas

- If `EMAIL_PROVIDER` is misspelled or its credentials are missing, the registry logs a warning and
  falls back to `mock`.
- The template escapes all interpolated content, so callers pass plain text (never markup) — a
  value like `<script>` is rendered as inert text, not injected into the HTML email.
- `MockEmailAdapter` keeps only the most recent 100 captured messages in memory.
- `ResendEmailAdapter` uses the API directly; the account still needs a verified sending domain for
  unrestricted delivery.
- `APP_WEB_URL` is present for future link-building, but this PR does not ship the verification or
  reset flows that will consume it.
- `EMAIL_FROM` is optional. When unset, the service uses the built-in fallback sender until a real
  verified sender is configured.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/37
- Linear issue: https://linear.app/2builders/issue/2BU-27/build-a-reusable-mock-first-email-service-adapter-queue

<!-- provenance: drafted from ideascout PR #37 on 2026-07-12 -->
