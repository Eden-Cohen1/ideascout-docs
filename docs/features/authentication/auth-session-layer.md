---
id: auth-session-layer
title: Auth API module and Pinia auth store
sidebar_position: 2
---

# Auth API module and Pinia auth store

This page documents the web auth session layer in ideascout: the thin HTTP wrapper around the auth endpoints and the Pinia store that owns user session state for the app.

## Behavior

- `src/api/auth.api.ts` is a thin wrapper over `apiFetch` and `ApiRoutes.auth.*` for `register`, `login`, `logout`, and `me`.
- `src/stores/auth.store.ts` owns the session state: `user`, `isAuthenticated`, and `status` (`idle` | `loading` | `ready`).
- The store exposes `login`, `register`, `logout`, and `fetchMe`.
- The store registers an unauthorized hook so any 401 response clears the session.
- `fetchMe()` is the boot-time hydration step: it resolves the initial `idle` state into a definite authenticated or logged-out state.
- `login()` and `register()` set `status` to `loading`, then `ready` once the request completes; failures are normalized and rethrown so the view can render inline form errors.
- `logout()` clears the local session even if the remote logout call fails.
- `src/lib/errors.ts` normalizes failures into `ApiError`, logs once with context, and keeps auth forms from inventing their own error handling.
- `src/lib/notify.ts` provides the shared notification sink with a console fallback until the toast host registers.

## Why

The linked Linear issue says this layer owns session state and auth calls so the views and router guard stay thin. It also uses the `idle` versus `ready` distinction to avoid a flash on protected routes before the app has checked the server.

## Edge cases & gotchas

- A 401 during `fetchMe()` is the normal logged-out state at boot, not a user-visible error.
- An unexpected `fetchMe()` failure still resolves the store to a definite logged-out state so the app does not stay stuck in `loading`.
- Failed logout is handled locally: the session is cleared even if the network call errors.
- Auth form failures are logged but not toasted by default; the form handles the message inline.
- This PR adds new modules only; it does not change env/config.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/29
- Linear issue: https://linear.app/2builders/issue/2BU-10/add-auth-api-module-and-pinia-auth-store

<!-- provenance: reconciled from ideascout PR #29 on 2026-07-12 -->
