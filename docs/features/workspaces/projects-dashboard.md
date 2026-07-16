---
id: projects-dashboard
title: Projects dashboard and infinite scroll
sidebar_position: 3
---

# Projects dashboard and infinite scroll

## Purpose

`PR #45` replaces the landing-page placeholder with the signed-in projects dashboard. It shows project cards quickly, keeps the list bounded with cursor pagination, and fetches more results as the user scrolls.

## Behavior

- `/` now renders `ProjectsView` instead of `HomeView`.
- The dashboard renders the same four visible states as the source PR and Linear issue describe:
  - loading skeleton cards on cold load
  - empty state for first-run workspaces
  - error state with a retry affordance
  - success state as a responsive card grid
- The success grid uses incremental rendering:
  - the first page is shown immediately
  - additional pages are requested when a bottom sentinel enters the viewport
  - the sentinel is cleaned up when the list unmounts
- The store moved from a flat `list()` shape to paged access:
  - `fetchFirstPage(force?)` returns cached results immediately on revisit, then revalidates page 1 in the background
  - concurrent first-page callers are coalesced onto one request
  - `fetchNextPage()` appends the next page, dedupes by id, and keeps `loadMoreError` separate from the main list
- Each project card links to `/projects/:id`.
- `/projects/:id` exists as a stub detail route; the dashboard is the real screen in this PR.

## Why

The Linear issue says signed-in users need to see their projects as cards on the landing page, with fast initial rendering and automatic loading as they scroll, so large workspaces never turn into a long wait. This PR consumes the paged projects contract from `2BU-37` and turns it into the first real screen in the web app.

## Edge cases & gotchas

- `loadMoreError` does not replace the already-rendered list.
- The sentinel disappears once there is no next cursor.
- This doc covers the dashboard and the infinite-scroll behavior, not project creation, rename/delete, virtualization, search, or detail content.
- The design and card copy in the source PR are implementation details; the stable contract here is the route/state/pagination behavior.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/45
- Linear issue: https://linear.app/2builders/issue/2BU-33/build-the-projects-list-view-the-dashboard

<!-- provenance: drafted from ideascout PR #45 -->
