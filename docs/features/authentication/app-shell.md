---
id: app-shell
title: Authenticated app shell and logout chrome
sidebar_position: 5
---

# Authenticated app shell and logout chrome

This page documents the authenticated top-level shell added in ideascout PR #36. It wraps
protected web pages with a brand header, a user chip, and a logout action.

## Purpose

Keep authenticated pages framed with the current user and a clear exit path, while leaving
public auth screens clean.

## Behavior

- `apps/web/src/App.vue` now decides whether to render the shell with
  `route.meta.requiresAuth && auth.isAuthenticated`.
- Protected routes render inside `AppShell`; public routes such as login render bare.
- `apps/web/src/components/AppShell.vue` owns the chrome:
  - a plain `ideascout` wordmark linking home,
  - a muted avatar chip derived from the signed-in user,
  - the current user label when available,
  - and a text-only logout button.
- Logout reuses the existing auth store, then redirects to `/login`.
- While logout is in flight, the button is disabled and shows `Signing out…` so repeated clicks
  are ignored.
- Routed pages render inside the shell's `<main>` and style with design tokens rather than owning
  a full-screen layout. PR #36 migrated `HomeView.vue` this way; the `/` landing view has since
  been replaced by the projects dashboard (documented separately), but the shell-wrapping contract
  described here is unchanged.
- `apps/web/src/App.spec.ts` and `apps/web/src/components/AppShell.spec.ts` cover the shell
  contract: authenticated wrapping, public routes staying bare, display-label fallback,
  logout redirect, and the in-flight guard.

## Why

The PR keeps authenticated content visually anchored without adding decorative chrome. The
review note explicitly says the shell ships without icons; the wordmark, initials chip, and
text-labelled logout action are deliberate.

## Edge cases & gotchas

- If the auth store loses the session, the shell disappears immediately because the wrapper
  checks `auth.isAuthenticated` before rendering it.
- The user label falls back from `displayName` to email.
- The initials chip falls back from name words to the email local-part.
- A second logout click is ignored while the first request is still pending.
- This change does not alter the route guard itself; see the auth route guard page for the
  boot-time session check and redirect behavior.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/36
- Linear issue: https://linear.app/2builders/issue/2BU-13/build-authenticated-appshell-nav-logout

<!-- provenance: drafted from ideascout PR #36 -->
