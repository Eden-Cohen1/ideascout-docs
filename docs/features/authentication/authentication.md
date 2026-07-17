---
id: authentication
title: Authentication flow
sidebar_position: 1
---

# Authentication flow

This page documents the login and account-creation screens in the web app, along with the
redirect behavior around them. It is for anyone changing the auth UI, auth routes, or the
shared validation and error-handling helpers those screens depend on.

## Behavior

- The app exposes three public routes: `/` (the marketing landing page), `/login`, and
  `/register`.
- `LoginView` collects email and password.
- `RegisterView` collects name, email, password, and password confirmation.
- Both screens use the shared Zod request schemas from `@ideascout/shared` to validate the
  form before any request is sent.
- Validation errors render inline under the matching field.
- Submit buttons stay disabled while a request is in flight and change label to show the
  loading state.
- Both screens call the auth store and show the server failure inline on error.
- After a successful sign-in or sign-up, the app navigates to the route named by
  `?redirect=` when that query value is a same-app path (excluding `/` itself); otherwise
  it falls back to `/projects` (the authenticated home — `/` is the public marketing page,
  not a useful landing after login).
- The `/` route has `publicOnly` meta: authenticated users visiting `/` are redirected to
  `/projects`.
- Signed-in users are kept out of `/login` and `/register` and sent back to `/projects`.
- The login page links to registration and preserves the current query string.
- The registration page links back to login and preserves the current query string.

## Why

The linked product issue framed this work as adding the missing path for users to sign in or
create an account so they can access their workspace. It also explicitly kept password reset
and OAuth out of scope, so this page only documents the in-app email/password flow.

## Edge cases & gotchas

- The registration form treats a blank or whitespace-only display name as omitted.
- `confirmPassword` is a client-only field; the API never receives it.
- The redirect helper only accepts same-app paths that start with a single `/`. Protocol-relative
  values like `//example.com`, strings without a leading slash, and non-string values (e.g. a
  repeated `?redirect=` query param, which arrives as an array) all fall back to `/projects`.
  The path `/` itself is also rejected — a stale `?redirect=/` falls through to `/projects`
  instead of bouncing a fresh login back to the public marketing page.
- The auth error handler turns a bare `401 Unauthorized` into session-expired copy, but keeps a
  specific server message such as invalid credentials when one is provided.
- Field validation shows one message per field, with the first issue winning.

## Related

- [Documentation home](/)

<!-- provenance: updated for PR #49 (marketing home page + Evidence Ledger rebrand); original from PR #35 (Add Login and Register views) -->
