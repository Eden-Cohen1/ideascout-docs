---
id: authentication-slice
title: "Authentication slice: verification, reset, and Google sign-in"
sidebar_position: 6
---

# Authentication slice: verification, reset, and Google sign-in

## Purpose

This page documents the backend auth slice introduced in ideascout PR #50: email verification,
password reset, Google sign-in, and the guardrails that keep those flows safe.

## Behavior

- `packages/shared/src/api-routes.ts` now exposes auth routes for `verify-email`,
  `resend-verification`, `forgot-password`, `reset-password`, plus Google OAuth start and
  callback endpoints.
- `apps/api/src/modules/auth/auth.controller.ts` adds the email-verification and password-reset
  endpoints.
- `apps/api/src/modules/oauth/oauth.controller.ts` adds the Google OAuth redirect flow:
  `/auth/oauth/google/start` begins the consent redirect and `/auth/oauth/google/callback`
  handles the callback.
- The OAuth handshake stores a short-lived, signed `oauth_state` cookie that carries the PKCE
  verifier and state token. The callback rejects missing, stale, forged, or mismatched values
  before it touches the provider.
- Google sign-in is adapter-based. The registry picks the real adapter when credentials are
  available and falls back to a mock adapter for local development and tests.
- The backend stores OAuth identities in a separate `OAuthAccount` record keyed by
  `(provider, providerAccountId)` rather than by email.
- `User.passwordHash` is nullable, so password-based and OAuth-based accounts can coexist.
- `JwtAuthGuard` now checks the database-backed user state, including `passwordChangedAt`, so a
  password reset revokes older sessions.
- `VerifiedEmailGuard` blocks only the expensive research-start action; browsing and existing run
  views stay open to unverified users.
- Shared DTOs now include the verification/reset request schemas, and the auth responses stay
  enumeration-safe for resend/forgot-password flows.

## Why

This slice turns auth into a multi-path backend instead of a password-only login system. The code
adds the recovery path for email accounts, the OAuth path for Google users, and the trust gate that
keeps research runs behind verified email addresses.

## Edge cases & gotchas

- `resend-verification` and `forgot-password` return generic acknowledgements so the endpoints do
  not reveal whether an account exists.
- The Google callback clears the handshake cookie on every attempt and redirects back to `/login`
  on any OAuth error.
- If Google credentials are not configured, the mock adapter is only acceptable outside production;
  production without a real adapter fails closed.
- An unverified password account is not silently linked to a Google identity; the merge path can
  require proof first.
- Password reset updates `passwordChangedAt`, which is what makes older JWTs stop working.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/50
- Linear issues referenced in the PR: 2BU-29, 2BU-41, 2BU-42, 2BU-43

<!-- provenance: draft from ideascout PR #50 -->
