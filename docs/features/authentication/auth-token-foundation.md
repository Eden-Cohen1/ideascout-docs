---
id: auth-token-foundation
title: Auth token foundation for verification and reset
sidebar_position: 3
---

# Auth token foundation for verification and reset

This page documents ideascout PR #39, which adds the data model, shared enums, and token
service behind email verification and password reset. It is foundation only: no endpoint,
enforcement, or user-facing flow changes ship here.

## Purpose

Provide the reusable token mechanism that later verification and reset endpoints can build on,
without changing how users log in today.

## Behavior

- `User` gains additive fields for future auth state: `emailVerified` (default `false`),
  `emailVerifiedAt`, and `passwordChangedAt`.
- Prisma adds a new `AuthToken` model with `userId`, `type`, `tokenHash`, `expiresAt`, and
  `consumedAt`, plus an `AuthTokenType` enum.
- `AuthTokenService.issue(userId, type)` creates a cryptographically random token, stores only
  its SHA-256 hash, and returns the raw token to the caller so it can be embedded in a link.
- `AuthTokenService.consume(rawToken, type)` validates the token atomically, marks it consumed
  with a guarded update, and returns the owning `userId` on success or `null` otherwise.
- Token lifetimes come from validated env vars: `EMAIL_VERIFICATION_TTL` and
  `PASSWORD_RESET_TTL`.
- `AuthUser` gains optional `emailVerified`, and both `/auth/me` and the login/register auth
  responses now include it.

## Why

The linked Linear issue says verification and password reset both need short-lived,
single-use, securely stored tokens tied to a user. This PR creates that foundation now so the
later endpoint and enforcement issues stay thin. It is additive and does not change behavior
for existing users or sessions.

## Edge cases & gotchas

- The raw token is never stored in the database; only its SHA-256 hash is persisted.
- `consume` is single-use and race-safe because it only succeeds when `consumedAt` is still
  `null`.
- Wrong-type, expired, replayed, or already-consumed tokens all return `null` without leaking
  which check failed.
- The new env vars are validated at boot; a bad duration string fails fast instead of producing
  a broken expiry timestamp.
- This PR does not add verification or reset endpoints yet, and it does not gate any user
  action on `emailVerified`.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/39
- Linear issue: https://linear.app/2builders/issue/2BU-28/add-auth-token-model-service-for-verification-and-reset-tokens

<!-- provenance: drafted from ideascout PR #39 -->
