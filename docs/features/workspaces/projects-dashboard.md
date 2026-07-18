---
id: projects-dashboard
title: Projects dashboard and infinite scroll
sidebar_position: 3
---

# Projects dashboard and infinite scroll

## Purpose

The signed-in projects dashboard shows project cards, keeps the list bounded with cursor pagination, and fetches more results as the user scrolls. Each card now has an actions menu (Rename / Delete) so a user can keep their workspace tidy without leaving the dashboard.

## Behavior

### Listing

- `/` renders `ProjectsView` instead of `HomeView`.
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
- `/projects/:id` exists as a stub detail route; the dashboard is the real screen.

### Actions menu (Rename / Delete)

Each `ProjectCard` shows a `⋯` (MoreHorizontal) button in its header. Clicking it opens a dropdown with **Rename** and **Delete** options. The card itself remains a single semantic `<a>` via a stretched `RouterLink`; the menu lives on its own stacking context (`z-10`) so clicks on it never trigger navigation, and the focus ring is scoped to the link only (not the whole card when the menu button is focused).

`ProjectsView` owns one instance each of `EditProjectDialog` and `DeleteProjectDialog`, retargeted per card — not one dialog per card. The target project persists through the close animation so the dialog doesn't blank out mid-transition.

#### Rename

Clicking **Rename** opens `EditProjectDialog`, prefilled with the card's `name` and `description`. The user can edit either field:

- **Name** is required, validated via `UpdateProjectRequestSchema.safeParse`. Inline field errors surface on the input.
- **Description** is optional. An emptied description sends `''` to clear it; provider fields stay omitted (out of scope → unchanged).

While saving, the submit button reads *Saving…* and stays disabled. On success the dialog closes and the card updates in place. On failure the dialog stays open and shows a status-derived error message inline.

#### Delete

Clicking **Delete** opens `DeleteProjectDialog`, an explicit destructive confirm: the dialog names the project and warns that the project and its ideas will be permanently removed.

- The confirm button is a plain `Button` (not `AlertDialogAction`) so the dialog stays open on failure to show the inline error, closing only on success.
- While deleting, the button reads *Deleting…* and stays disabled.

The delete uses the same `useDialogForm` composable as create and rename, but with no form fields — it consumes only the loading/error half of the contract.

### Shared form behavior (`useDialogForm`)

All three dialog flows (create, rename, delete) use the `useDialogForm` composable, which provides `validate` (calls `safeParse` and surfaces inline field errors) and `run` (calls the store action, handles loading state and inline error surfacing). This was extracted in PR #60 so all dialogs reuse the same plumbing.

## Why

The Linear issue says signed-in users need to see their projects as cards on the landing page, with fast initial rendering and automatic loading as they scroll, so large workspaces never turn into a long wait. This PR consumes the paged projects contract from `2BU-37` and turns it into the first real screen in the web app.

The actions menu closes `2BU-35`: users can now rename and delete projects inline from the dashboard, keeping their workspace tidy without navigating to a separate settings page.

## Edge cases & gotchas

- `loadMoreError` does not replace the already-rendered list.
- The sentinel disappears once there is no next cursor.
- Reopening a dialog resets prior inputs and errors; each dialog starts clean.
- The rename dialog seeds from the current project on open (`{ immediate: true }` watch) so a pre-opened dialog with a target works on mount.
- The delete dialog keeps the confirm button as a plain `Button` (not `AlertDialogAction`) so it stays open on failure for the inline error; only success closes it.
- The card grid uses **windowed (virtualized) rendering** via `@tanstack/vue-virtual` (a window virtualizer over page scroll, so the page scrollbar and layout are unchanged). The flat list is chunked into grid rows and only the rows in — and just around — the viewport are kept in the DOM, recycling nodes as you scroll. It is a transparent performance optimization with no visual or behavioral change.
- **Windowing is unconditional** — it is always active, not gated behind a row-count threshold. For a short list the window simply spans every row, so there is no visible difference; the payoff comes once a workspace grows into the hundreds of projects, where rendering every card at once would jank scrolling. (The `~172px` row-height estimate and 4-row overscan are tuning constants, not an on/off trigger.)
- **Focus limitation:** focusing a card by pointer and then scrolling it far off-screen does not restore focus to that card on scroll-back — the off-screen row is unmounted, so focus falls back to the document body. The normal keyboard Tab flow (which keeps the focused card in the viewport) is unaffected.
- This doc covers the dashboard, infinite-scroll behavior, and per-card actions; not project creation, search, or detail content.

## References

- Source PR (dashboard & infinite scroll): https://github.com/Eden-Cohen1/ideascout/pull/45
- Source PR (rename & delete actions): https://github.com/Eden-Cohen1/ideascout/pull/60
- Source PR (windowed rendering): https://github.com/Eden-Cohen1/ideascout/pull/61
- Linear issue (dashboard): https://linear.app/2builders/issue/2BU-33/build-the-projects-list-view-the-dashboard
- Linear issue (rename & delete): https://linear.app/2builders/issue/2BU-35
- Linear issue (windowing): https://linear.app/2builders/issue/2BU-38/virtualize-very-long-project-lists-windowed-rendering

<!-- provenance: derived from PR #45, PR #60 (rename & delete project), and PR #61 (windowed rendering); reconciled 2026-07-18 -->
