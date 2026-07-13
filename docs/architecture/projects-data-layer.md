---
id: projects-data-layer
title: Projects data layer
sidebar_position: 5
---

# Projects data layer

This page documents the frontend projects seam added in ideascout PR #40: the thin
`projectsApi` wrapper and the Pinia store that keeps the dashboard's project list in one
cached, error-handled place.

## Purpose

Provide one stable source of truth for project reads and writes so the dashboard can load,
create, rename, and delete projects without each view having to talk to the API directly.

## Behavior

- `apps/web/src/api/projects.api.ts` is a thin HTTP wrapper over `apiFetch` and
  `ApiRoutes.projects`.
- The API client exposes `list`, `get`, `create`, `update`, and `remove`.
- `get(id)` is present for the future project-detail route even though the current store does
  not call it yet.
- Path helpers URL-encode the project id before calling the per-project endpoint.
- `apps/web/src/stores/projects.store.ts` owns the dashboard cache:
  - `items` holds the current list.
  - `status` tracks `idle` → `loading` → `ready` → `error`.
  - `error` stores a friendly message for the inline retry state.
  - `byId` provides per-id lookup over the cached list.
  - `isLoading` is a derived convenience flag for the view layer.
- `fetchList()` loads once and does not refetch when `status === 'ready'` unless `force` is
  passed.
- Concurrent callers share a single in-flight list request instead of duplicating network
  work.
- `create()` prepends the new project into the cache after the API call succeeds.
- `update()` replaces the matching project in place.
- `remove()` filters the deleted project out of the cache.
- Every failure routes through `handleError` with `notify: false`.
- `fetchList()` keeps a status-derived message in `error` so the dashboard can render the inline
  retry state.
- `create()`, `update()`, and `remove()` rethrow the normalized `ApiError` so the calling form
  can surface the failure inline.

## Why

The linked Linear issue frames this as the reusable data layer for the projects dashboard:
read and write projects through one cached, error-handled source of truth, keep the views thin,
and make the dashboard the workspace home for signed-in users. The work is intentionally
additive: it consumes the shared project DTOs and `ApiRoutes.projects` that already exist
instead of redefining contract shape in the web app.

## Edge cases & gotchas

- The list is authoritative once loaded; a revisited dashboard will not hit the network again
  unless `fetchList(true)` is used.
- `fetchList()` is log-only on failure; mutation failures are rethrown for inline form handling.
- The store keeps the cached list unchanged on failed create/update/remove calls.
- `get(id)` exists in the API client for the future detail route, but the current store and UI do
  not consume it yet.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/40
- Linear issue: https://linear.app/2builders/issue/2BU-32/add-the-projects-api-client-pinia-store
- Parent epic: https://linear.app/2builders/issue/2BU-31/projects-dashboard-list-create-open-and-manage-projects

<!-- provenance: drafted from ideascout PR #40 on 2026-07-13 -->
