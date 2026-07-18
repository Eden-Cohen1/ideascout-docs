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
incrementally-loaded, cursor-paged model to back the dashboard's infinite scroll (PR #45). The
store later gained a server-side name search (PR #62) — the filter stays server-side so the
list remains cursor-paginated and owner-scoped. This page describes the current layer.

## Purpose

Provide one stable source of truth for project reads and writes so the dashboard can load,
create, rename, and delete projects without each view talking to the API directly — and keep
the list **bounded** as it grows by paging rather than fetching every project at once. The
server-side search extends this model: the client never receives the full list, and filtered
navigation works through the same pagination path.

## Behavior

### API client — `apps/web/src/api/projects.api.ts`

- A thin HTTP wrapper over `apiFetch` and `ApiRoutes.projects`, typed by the shared project
  DTOs. No state lives here.
- `page({ cursor?, limit, q? }, signal?)` returns one cursor-paginated `ProjectPage`
  (`{ items, nextCursor }`). It builds the `?limit=…&cursor=…&q=…` query string and accepts an
  optional `AbortSignal` so the store can cancel a stale request. The `q` parameter is the
  server-side name filter (passed through from the store's `query`).
- `get`, `create`, `update`, and `remove` are the per-entity CRUD calls; `get(id)` exists for
  the future project-detail route even though the store does not call it yet.
- Path helpers URL-encode the project id before calling the per-project endpoint.

### Store — `apps/web/src/stores/projects.store.ts`

The dashboard's single source of truth. It owns a cursor-paginated, incrementally-loaded list
with server-side search.

- **State:** `items` (the accumulated list), `status` (`idle` → `loading` → `ready` → `error`),
  `error` (a friendly message for the first-page retry state), `nextCursor` (the cursor for the
  next page, or `null` at the end), `isLoadingMore`, and `loadMoreError` (a separate error for
  next-page loads so a failed "load more" never clobbers the visible list), `query` (the active
  trimmed search term, `''` = no filter), `isSearching` (whether a search-driven page-1 load is
  in flight), and `hasQuery` (whether a name filter is active — distinct from `isSearching`).
- **Getters:** `byId` (per-id lookup over the cache), `isLoading` (first page in flight), `hasMore`
  (`nextCursor !== null`), and `hasQuery` (`query.length > 0`, used by the view for a
  "no matches" empty state vs "no projects yet").
- `fetchFirstPage(force?)` loads page 1. A cold load shows the loading state; a revisit to an
  already-`ready` store is **stale-while-revalidate** — it shows the cached list instantly and
  silently revalidates page 1 in the background (no spinner flash). Concurrent first-page callers
  are coalesced onto a single in-flight request. Each page-1 load is tied to an `AbortController`
  that supersedes the prior one — a stale in-flight response is aborted so it can never overwrite
  newer results. `force` re-runs with the loading state and drives the error-state retry.
- `fetchNextPage()` appends the next page as the user scrolls, using `nextCursor`. It carries the
  active `query` through to the API so later pages stay within the same filtered result set, and
  checks whether the query changed mid-flight (dropping the page if a new search reset the list).
  It **dedupes by id** (a project inserted server-side between page fetches could otherwise appear
  twice) and is a no-op when the store is not `ready`, there is no next cursor, or a load is
  already in flight.
- `setQuery(next)` applies a server-side name filter. It trims the term, stores it, resets
  the cursor, and reloads page 1 with the filter (superseding any in-flight load via the
  AbortController). It is a no-op when the trimmed term is unchanged. `isSearching` keeps the
  current list on screen with a spinner rather than flashing skeletons while the filtered
  results arrive.
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

The server-side search (2BU-39) extends this model: instead of shipping the full list to the
client for client-side filtering, the `q` filter is sent with every page request, so the
API payload stays bounded even during a search.

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
- An aborted request (superseded by a newer search) silently returns without touching state — the
  `isAbortError` guard prevents a stale response from overwriting newer results.
- `setQuery` is a no-op when the trimmed term is unchanged, avoiding unnecessary requests on
  rapid identical input.

## Related

- [Project creation from the dashboard](./project-creation-from-dashboard.md) — the create dialog
  that calls `store.create`.
- [Projects dashboard and infinite scroll](./projects-dashboard.md) — the view that consumes this
  store, including the search box and "no matches" state.
- [Projects pagination and shared page contracts](./projects-pagination.md) — the `ProjectPageQuery`
  type and the backend contracts.

## References

- Source PR (search/filter): https://github.com/Eden-Cohen1/ideascout/pull/62
- Source PR (current store/API): https://github.com/Eden-Cohen1/ideascout/pull/45
- Backend cursor pagination: https://github.com/Eden-Cohen1/ideascout/pull/42
- Original data layer: https://github.com/Eden-Cohen1/ideascout/pull/40
- Linear issue (search/filter): https://linear.app/2builders/issue/2BU-39/server-side-project-search-filter
- Linear issue (data layer): https://linear.app/2builders/issue/2BU-32/add-the-projects-api-client-pinia-store
- Parent epic: https://linear.app/2builders/issue/2BU-31/projects-dashboard-list-create-open-and-manage-projects

<!-- provenance: drafted from ideascout PRs #40, #42, #45, #62 -->
