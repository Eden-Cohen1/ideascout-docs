---
id: projects-dashboard
title: Projects dashboard and infinite scroll
sidebar_position: 3
---

# Projects dashboard and infinite scroll

## Purpose

The signed-in projects dashboard. It shows project cards quickly, keeps the list bounded with
cursor pagination, fetches more results as the user scrolls, and provides a server-side name
search so users can find projects without scrolling a large list.

## Behavior

- `/` renders `ProjectsView` instead of `HomeView`.
- The dashboard renders five visible states:
  - **Loading** — skeleton cards on cold load
  - **Empty** — first-run workspace with no projects yet
  - **Error** — with a retry affordance
  - **Success** — responsive card grid with incremental rendering
  - **No matches** — distinct from the empty workspace, shown when a search finds nothing
- The success grid uses incremental rendering:
  - the first page is shown immediately
  - additional pages are requested when a bottom sentinel enters the viewport
  - the sentinel is cleaned up when the list unmounts
- Each project card links to `/projects/:id`.
- `/projects/:id` exists as a stub detail route; the dashboard is the real screen.

### Server-side name search (2BU-39)

A search box appears above the grid once there are projects to search (or when an active filter
is present — so it stays visible in the "no matches" state). It is hidden during the cold-load,
error, and first-run empty states.

- **Debounced input** — typing is debounced at 300ms via `watchDebounced` from `@vueuse/core`,
  so one server-side search fires per typing pause rather than per keystroke.
- **AbortController superseding** — each new search aborts the prior in-flight request; a stale
  response that lands late is silently dropped so it cannot overwrite newer results.
- **Distinct empty states** — when a search returns zero results, the view shows a "no matches"
  state (identifiable by `data-testid="projects-no-matches"`) with the active query and a clear
  button. This is visually and semantically different from the first-run empty workspace state
  (`data-testid="projects-empty"`).
- **Clear** — a clear button (X icon) on the right of the input, or pressing Escape, clears
  the filter and restores the full list.
- **Scroll-to-top** — when the active filter changes, the window scrolls to top so the virtual
  grid re-windows from the top instead of sitting past the end of a now-shorter list.
- **`maxlength=200`** — the input is bounded to match the server-side schema constraint.

| State | Screenshot |
| --- | --- |
| Success (virtualized list) | <img width="440" src="https://raw.githubusercontent.com/Eden-Cohen1/ideascout/6bc12fc0fc4ced2a7cd93737a176880297780d4d/docs/screenshots/2bu-39/01-list.png" /> |
| Search — filtered (clear button + focus ring) | <img width="440" src="https://raw.githubusercontent.com/Eden-Cohen1/ideascout/6bc12fc0fc4ced2a7cd93737a176880297780d4d/docs/screenshots/2bu-39/02-search-filtered.png" /> |
| Filtered pagination (page 2 loaded within the filter) | <img width="440" src="https://raw.githubusercontent.com/Eden-Cohen1/ideascout/6bc12fc0fc4ced2a7cd93737a176880297780d4d/docs/screenshots/2bu-39/03-search-paginated-bottom.png" /> |
| No matches (distinct from empty workspace) | <img width="440" src="https://raw.githubusercontent.com/Eden-Cohen1/ideascout/6bc12fc0fc4ced2a7cd93737a176880297780d4d/docs/screenshots/2bu-39/04-no-matches.png" /> |
| Cleared (full list restored) | <img width="440" src="https://raw.githubusercontent.com/Eden-Cohen1/ideascout/6bc12fc0fc4ced2a7cd93737a176880297780d4d/docs/screenshots/2bu-39/05-cleared.png" /> |

## Why

The Linear issue says signed-in users need to see their projects as cards on the landing page,
with fast initial rendering and automatic loading as they scroll, so large workspaces never turn
into a long wait. The server-side search (2BU-39) extends this: past a few hundred projects,
users search rather than scroll. Debounced input + abort controllers keep it responsive, and the
distinct "no matches" state avoids confusing a failed search with an empty workspace.

## Edge cases & gotchas

- `loadMoreError` does not replace the already-rendered list.
- The sentinel disappears once there is no next cursor.
- The search box is hidden during cold-load, error, and first-run empty states — it only appears
  once there is data or an active filter.
- When the search filter changes, the window scrolls to top so the virtual grid re-windows
  correctly (a now-shorter list would otherwise render nothing until the user scrolls up).
- The "no matches" state includes a clear button and shows the active query text.
- This doc covers the dashboard, infinite scroll, and search — not project creation, rename/delete,
  or detail content.

## References

- Source PR (search): https://github.com/Eden-Cohen1/ideascout/pull/62
- Source PR (dashboard + infinite scroll): https://github.com/Eden-Cohen1/ideascout/pull/45
- Linear issue (search): https://linear.app/2builders/issue/2BU-39/server-side-project-search-filter
- Linear issue (dashboard): https://linear.app/2builders/issue/2BU-33/build-the-projects-list-view-the-dashboard

<!-- provenance: drafted from ideascout PR #45, #62 -->
