---
id: authentication
title: Authentication flow
sidebar_position: 1
---

# Authentication flow

This page documents the auth screens in the web app — sign-in, sign-up, password
reset, email verification — along with the unified `AuthShell` layout and the
shared auth components. It is for anyone changing the auth UI, auth routes, or
the shared validation and error-handling helpers those screens depend on.

## AuthShell — the split-screen brand panel

All auth screens render inside `AuthShell`, a split-screen layout:

- **Desktop (lg+):** a brand panel on the left (soft cobalt wash via the scoped
  `--auth-panel` / `--auth-panel-foreground` token pair) showing the product
  pitch (Evaluate → Refine → Validate) and a cited-research trust mark. The form
  renders on the right.
- **Mobile (below lg):** the brand panel is hidden; a compact wordmark is shown
  above the form instead.

The `--auth-panel` token is deliberately *not* `--accent`, so the panel can be
retuned without touching ghost-hover surfaces. It is registered in `contrast-check`
and documented in `DESIGN.md`.

## Sign-in / Sign-up (`/login`, `/register`)

Both `/login` and `/register` render the **same** `AuthView` component. Vue Router
reuses the instance when navigating between them — the mode (login or register)
flips reactively, so the heading, mode-specific fields (Name, Confirm password),
and strength meter transition with an expand/swap animation instead of a hard
remount.

- **Login** collects email and password; validation uses the shared
  `LoginRequestSchema`.
- **Register** collects name (optional), email, password, and password
  confirmation; validation uses the shared `RegisterFormSchema`.
- The password field uses `PasswordInput` (inline show/hide toggle with eye icon).
- On register, `PasswordStrengthMeter` appears below the password field once the
  user starts typing. The four-segment indicator maps score to semantic colors
  (destructive → warning → success).
- The "Continue with Google" button is a full-page redirect to
  `/auth/oauth/google/start` — a plain `<a>` tag, not a fetch.
- An "or continue with email" divider separates the OAuth button from the form.
- A "Forgot password?" link on the login form navigates to `/forgot-password`.
- Validation errors render inline under the matching field.
- Submit buttons stay disabled while a request is in flight and change label
  (`Signing in…` / `Creating account…`).
- On success the app navigates to the route named by `?redirect=` when that query
  value is a same-app path; otherwise it falls back to `/projects`.
- Mode-specific fields (Name, Confirm, strength meter) use CSS
  `grid-template-rows: 0fr↔1fr` transitions for smooth expand/collapse without
  magic pixel values.
- Signed-in users are kept out via the `publicOnly` route guard and redirected to
  `/projects`. The public marketing landing page at `/` carries the same
  `publicOnly` meta, so an authenticated user who hits `/` is likewise sent to
  `/projects`.
- Switching mode (login ↔ register) clears field-level and form-level errors.
  The email and password values persist (no loss if the user mistypes and clicks
  the other tab).

## Prove-then-link: password-proof Google linking (`/login?notice=verify-email`)

When a Google sign-in matches an existing **unverified password** account, the
OAuth callback redirects to `/login?notice=verify-email`. On this screen the user
sees both options:

1. **Password-proof fast path** — a notice banner plus a password form:
   - A `PasswordInput` field (`#link-password`) for the account password.
   - A "Connect Google with password" submit button.
   - Submitting calls `authStore.linkGoogleWithPassword({ password })`, which
     posts to `POST /auth/oauth/google/link`. The pending Google identity rides the
     httpOnly `oauth_link` cookie (set by the callback), so only the password is
     sent in the request body.
   - **On success:** the user is authenticated and routed into the workspace.
   - **On failure:** a generic enumeration-safe error is shown inline
     (*"That password is incorrect, or this link has expired."*) and the user
     stays on the screen. They can still use the emailed verification link.
2. **Email-verification round-trip** — the callback also sent a verification
   email; once verified, the next Google sign-in auto-links.

### Screenshots

| State | Screenshot |
|:---|---:|
| **Prove-then-link** (notice + password form) | ![Prove-then-link](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/1b04946ff15c6228149296f821c718627a75f33b/docs/screenshots/2bu-44/01-prove-then-link.png) |
| **Wrong password** (inline error) | ![Wrong password](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/1b04946ff15c6228149296f821c718627a75f33b/docs/screenshots/2bu-44/02-prove-then-link-error.png) |
| **Mobile** | ![Mobile](https://raw.githubusercontent.com/Eden-Cohen1/ideascout/1b04946ff15c6228149296f821c718627a75f33b/docs/screenshots/2bu-44/03-prove-then-link-mobile.png) |

## Forgot password (`/forgot-password`)

A standalone view inside `AuthShell` that collects the user's email and sends a
reset link.

- Email-only form with validation.
- Enumeration-safe: the API acknowledges identically whether or not the account
  exists, returning a generic `{ message }` on success.
- Shows a confirmation message after submission ("Check your inbox for the reset
  link.").
- Links back to login.

## Reset password (`/reset-password?token=…`)

A standalone view inside `AuthShell` that sets a new password from a reset link.

- The single-use `token` comes from the URL query (`?token=…`), not the form.
- The form validates the new password + a client-only confirmation match.
- Uses `PasswordInput` and `PasswordStrengthMeter`.
- On success the backend logs the user in (sets the httpOnly cookie), so the app
  routes into the workspace at `/projects`.
- A missing or blank token renders a clean dead-end ("This reset link is invalid")
  with a link to request a new one.
- An expired or already-used token shows the server error inline and offers a
  "Request a new link" action.

## Verify email (`/verify-email?token=…`)

A standalone view inside `AuthShell` that confirms an email from a verification
link. The token comes from the URL and is submitted automatically on mount — the
user just lands here from their inbox.

- **Verifying phase:** shows a loading state while the API confirms the token.
- **Success phase:** authenticates the user (cookie set), shows a success
  message with a "Continue" link to `/projects`, and auto-redirects after 1.5
  seconds (timer cleared on unmount).
- **Error phase:** shows the error (expired/reused/missing token). If the user
  is still signed in (unverified), a "Resend verification email" button is
  shown. If not signed in, it offers "Sign in to resend".

## Verify email banner (in `AppShell`)

A dismissible nudge bar shown inside the authenticated `AppShell` while the
signed-in user has not yet verified their email (`emailVerified === false`).

- Renders only when `emailVerified` is definitely `false` — never when the flag
  is absent.
- Shows the user's email and a "Resend email" button.
- On send success, the text changes to "Verification email sent — check your
  inbox."
- The banner can be dismissed via an X button. It stays dismissed for the
  session.
- Verification gates expensive actions (starting a research run), not browsing.

## Why

The PR turns the auth UI into a single, reusable surface that supports both
email/password and Google sign-in, and completes the recovery/verification flow
that the backend already implemented. The split-screen `AuthShell` gives every
auth screen a consistent brand presentation, and the shared `AuthView` avoids
route-level duplication between login and register.

## Edge cases & gotchas

- `LoginView.vue` and `RegisterView.vue` are **deleted** — superseded by
  `AuthView.vue`. Both `/login` and `/register` now point to `AuthView.vue`.
- The registration form treats a blank or whitespace-only display name as
  omitted.
- `confirmPassword` is a client-only field; the API never receives it.
- The `?redirect=` helper only accepts same-app paths that start with a single
  `/`. Protocol-relative values like `//example.com`, strings without a leading
  slash, and non-string values (e.g. a repeated `?redirect=` query param, which
  arrives as an array) all fall back to `/projects`. The path `/` itself is also
  rejected — a stale `?redirect=/` falls through to `/projects` instead of
  bouncing a fresh login back to the public marketing page.
- Forgot-password and resend-verification are enumeration-safe: the API returns
  the same response whether or not the account exists.
- Reset-password and verify-email authenticate the user on success (the API sets
  the httpOnly cookie), matching the `reset ⇒ signed in` contract.
- The auth error handler turns a bare `401 Unauthorized` into session-expired
  copy, but keeps a specific server message such as invalid credentials when one
  is provided.
- Field-level validation shows one message per field, with the first issue
  winning.
- The reset and verify routes do **not** carry `publicOnly` or `requiresAuth`
  meta — reset and verify sign the user in on success, and an unverified user
  may hit verify while already logged in.
- The verify-email auto-redirect timer is cleared on unmount so it cannot fire
  after the component is gone.
- Avatar initials are derived from name words, falling back to the email
  local-part.

## Related

- [Auth API and Pinia store](./auth-session-layer.md)
- [Auth token foundation](./auth-token-foundation.md)
- [Backend authentication slice](./authentication-slice.md)
- [Authenticated app shell](./app-shell.md)
- [Documentation home](/)

<!-- provenance: drafted from ideascout PR #57 (auth redesign Option B with email verification & password reset, supersedes #51), reconciled after design-system merge; rebased onto PR #49 canonical (marketing home + Evidence Ledger rebrand), preserving the `/` publicOnly + redirect-guard behavior; original from PR #35 (Add Login and Register views) -->

