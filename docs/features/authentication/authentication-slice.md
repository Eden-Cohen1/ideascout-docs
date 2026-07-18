---
id: authentication-slice
title: "Authentication slice: verification, reset, and Google sign-in"
sidebar_position: 4
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

## Prove-then-link fast path (2BU-44, PR #59)

When a Google sign-in matches an existing **unverified password** account, the callback
(`/auth/oauth/google/callback`) now makes **both** routes available to the user:

1. The existing **email-verification round-trip** — a verification email is sent; once verified,
   the next sign-in auto-links.
2. A new **password-proof fast path** — the user can enter their account password immediately
   on the `/login?notice=verify-email` screen and link Google in one step, without waiting for
   the email.

### OAuthLinkTokenService

New service (`apps/api/src/modules/oauth/oauth-link-token.service.ts`) that mirrors
`OAuthStateService`:

- `issue(pending)` — signs a short-lived (10-minute), `purpose: 'oauth_link'` JWT carrying the
  pending Google identity (`userId`, `provider`, `providerAccountId`).
- `verify(cookieValue)` — validates the JWT, checks the `purpose` marker, and returns the
  `PendingLink` or `null` on any failure (missing, expired, forged, tampered with a different
  signing key, or a session JWT replayed here).

The token is stateless — no DB, no server session — and dropped into an **httpOnly `oauth_link`
cookie** on the callback response. The client can never forge which account it links.

### accountLinkService.proveAndLink

New method (`apps/api/src/modules/oauth/account-link.service.ts`) that:

1. Looks up the user by the `pending.userId` (not the client's assertion).
2. Rejects immediately if the user is missing or is an OAuth-only (passwordless) account.
3. Verifies the password via `AuthService.verifyPassword`.
4. On success: links the `OAuthAccount` record + marks the email verified.
5. On any failure — unknown user, OAuth-only account, wrong password — throws the **same
   generic 401** (`'Invalid credentials'`), so nothing leaks about which case occurred
   (enumeration-safe, matching the login endpoint's posture).

### POST /auth/oauth/google/link

New endpoint (`OAuthController.link`) behind a **5/min throttle** (matching login-class
endpoints, tighter than the 10/min OAuth-redirect bucket):

- **Request body:** `LinkGoogleAccountRequest` — a shared Zod DTO containing only `password`.
  The password is the only client-supplied value; the pending identity rides the httpOnly
  `oauth_link` cookie from the callback, never the body.
- **On success:** links the Google identity, clears the one-time cookie, issues a session
  (httpOnly `access_token` cookie), and returns `AuthResponse`. The user is signed in.
- **On failure:** the generic 401 surfaces in the response; the cookie is consumed (one-time).
- **Provider check:** the token carries the provider; the endpoint also rejects a token
  minted for a different provider (e.g. GitHub) before touching the account.

### Frontend

- `authApi.linkGoogle(body)` calls `POST /auth/oauth/google/link`.
- `authStore.linkGoogleWithPassword(body)` drives the session exactly like `login`: sets
  `status` to `loading`, calls the API, updates `user` on success, or rethrows the error
  (inline form displays a generic message like *"That password is incorrect, or this link
  has expired."*) without toasting.
- On the `AuthView` screen at `/login?notice=verify-email`, a password form appears below
  the notice banner with a password field and a "Connect Google with password" button.

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
- The `oauth_link` cookie is one-time: a proved link clears it on success, and the endpoint
  also clears it on failure so a stale cookie cannot be replayed.
- The link endpoint's 5/min throttle is per-IP, preventing brute-force password attempts at
  the same rate as direct password login.
- Every proveAndLink failure mode (missing user, OAuth-only account, wrong password) returns
  the identical `401 Invalid credentials` — never "no such user" or "wrong password", which
  would let an attacker enumerate accounts.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/50
- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/59 (prove-then-link fast path)
- Linear issues referenced in the PRs: 2BU-29, 2BU-41, 2BU-42, 2BU-43, 2BU-44

<!-- provenance: draft from ideascout PR #50; updated with PR #59 (prove-then-link fast path) -->
