---
id: projects-data-layer
title: Projects data layer
sidebar_position: 1
---

# Projects data layer

This page documents the frontend projects seam: the thin `projectsApi` wrapper and the Pinia
store that keep the dashboard's project list in one cached, paginated, error-handled place.

The layer started as a simple array fetch (ideascout PR #40) and was then reworked for scale —
the backend moved `GET /projects` to cursor pagination (PR #42), and the store switched to an
incrementally-loaded, cursor-paged model to back the dashboard's infinite scroll (PR #45). This
page describes the current, paginated layer.

## Purpose

Provide one stable source of truth for project reads and writes so the dashboard can load,
create, rename, and delete projects without each view talking to the API directly — and keep
the list **bounded** as it grows by paging rather than fetching every project at once.

## Behavior

### API client — `apps/web/src/api/projects.api.ts`

- A thin HTTP wrapper over `apiFetch` and `ApiRoutes.projects`, typed by the shared project
  DTOs. No state lives here.
- `page({ cursor?, limit }, signal?)` returns one cursor-paginated `ProjectPage`
  (`{ items, nextCursor }`). It builds the `?limit=…&cursor=…` query string and accepts an
  optional `AbortSignal` so the store can cancel a stale request.
- `get`, `create`, `update`, and `remove` are the per-entity CRUD calls; `get(id)` exists for
  the future project-detail route even though the store does not call it yet.
- Path helpers URL-encode the project id before calling the per-project endpoint.

### Store — `apps/web/src/stores/projects.store.ts`

The dashboard's single source of truth. It owns a cursor-paginated, incrementally-loaded list.

- State: `items` (the accumulated list), `status` (`idle` → `loading` → `ready` → `error`),
  `error` (a friendly message for the first-page retry state), `nextCursor` (the cursor for the
  next page, or `null` at the end), `isLoadingMore`, and `loadMoreError` (a separate error for
  next-page loads so a failed "load more" never clobbers the visible list).
- Getters: `byId` (per-id lookup over the cache), `isLoading` (first page in flight), and
  `hasMore` (`nextCursor !== null`).
- `fetchFirstPage(force?)` loads page 1. A cold load shows the loading state; a revisit to an
  already-`ready` store is **stale-while-revalidate** — it shows the cached list instantly and
  silently revalidates page 1 in the background (no spinner flash). Concurrent first-page callers
  are coalesced onto a single in-flight request. `force` re-runs with the loading state and drives
  the error-state retry.
- `fetchNextPage()` appends the next page as the user scrolls, using `nextCursor`. It **dedupes
  by id** (a project inserted server-side between page fetches could otherwise appear twice) and
  is a no-op when the store is not `ready`, there is no next cursor, or a load is already in
  flight.
- `create()` prepends the new project into the cache; `update()` replaces the matching project
  in place; `remove()` filters the deleted project out.

### Error handling

- First-page and next-page loads route failures through the central `handleError` with
  `notify: false` (the view renders the error inline). `fetchFirstPage` keeps a status-derived
  message in `error`; `fetchNextPage` keeps its own in `loadMoreError`.
- `create()`, `update()`, and `remove()` rethrow the normalized `ApiError` so the calling form
  can surface the failure inline.

## Why

The linked epic frames this as the reusable data layer for the projects dashboard: read and
write projects through one cached, error-handled source of truth and keep the views thin. Paging
is the scaling piece — `GET /projects` previously returned every project in one unbounded
payload; cursor pagination bounds both the payload and the rendered list, and the store's
`fetchFirstPage`/`fetchNextPage` pair backs the dashboard's infinite scroll. The work consumes
the shared project and page DTOs and `ApiRoutes.projects` instead of redefining contract shape
in the web app.

## Edge cases & gotchas

- Revisiting a loaded dashboard is stale-while-revalidate: the cached list shows immediately and
  page 1 is refreshed in the background — a background revalidation failure is logged only and
  keeps the cached list visible (it does **not** flip the view into the error state).
- Next-page failures set `loadMoreError` without clearing `items`, so a failed "load more" leaves
  the already-loaded list intact with its own retry affordance.
- `fetchNextPage()` dedupes by id, so a project inserted between page fetches is not shown twice.
- Mutation failures leave the cached list unchanged; the normalized `ApiError` is rethrown for
  inline form handling.
- `get(id)` exists in the API client for the future detail route, but the current store and UI do
  not consume it yet.

## Related

- [Project creation from the dashboard](./project-creation-from-dashboard.md) — the create dialog
  that calls `store.create`.

## References

- Source PR (current store/API): https://github.com/Eden-Cohen1/ideascout/pull/45
- Backend cursor pagination: https://github.com/Eden-Cohen1/ideascout/pull/42
- Original data layer: https://github.com/Eden-Cohen1/ideascout/pull/40
- Linear issue: https://linear.app/2builders/issue/2BU-32/add-the-projects-api-client-pinia-store
- Parent epic: https://linear.app/2builders/issue/2BU-31/projects-dashboard-list-create-open-and-manage-projects

<!-- provenance: drafted from ideascout PR #40, reconciled to the current cursor-paginated layer (PRs #42, #45) -->
