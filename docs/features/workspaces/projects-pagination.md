---
id: projects-pagination
title: Projects pagination and shared page contracts
sidebar_position: 2
---

# Projects pagination and shared page contracts

This page documents the backend/shared contract for `GET /projects`. The endpoint originally
returned a bare array (ideascout PR #40), then moved to a cursor-paginated page (PR #42), and
later added a server-side name filter (PR #62). The shared page contracts in `packages/shared`
are designed to be reusable across list endpoints.

## Purpose

Keep large project lists fast to load and make the page shape reusable for future list APIs
without each endpoint inventing its own pagination DTO. The server-side name filter extends
this model: search stays cursored and owner-scoped rather than shipping the full list to the
client for client-side filtering.

## Behavior

- `PageQuerySchema` accepts `{ cursor?, limit }`.
- `limit` comes from the query string, defaults to 20, and is clamped to 100.
- An empty `cursor` is treated like "first page".
- `ProjectPageSchema` is `pageSchema(ProjectResponseSchema)` and returns
  `{ items, nextCursor }`.
- `GET /projects` returns a page instead of an array.
- The service orders by `createdAt desc, id desc` so the sort is total when timestamps tie.
- Pagination uses `take: limit + 1` to derive `nextCursor` without a count query.
- Subsequent pages use Prisma `cursor` + `skip: 1`.
- `nextCursor: null` means there is no next page.
- Swagger documents the query parameters and page response.

### Name filter (2BU-39)

`ProjectPageQuerySchema` extends `PageQuerySchema` with an optional `q` parameter:

```ts
export const ProjectPageQuerySchema = PageQuerySchema.extend({
  q: z.string().max(200).optional(),
});
```

- When `q` is present and non-blank, `pageForOwner` filters by case-insensitive **name contains**
  (`ILIKE '%term%'`). A blank or whitespace-only `q` is treated as "no filter".
- LIKE metacharacters (`%`, `_`, `\`) are backslash-escaped so the search term matches literally,
  not as a wildcard.
- The filter is part of every page's `where` clause, so cursor-paginated navigation through a
  filtered result set works exactly like the unfiltered list.
- Swagger documents the `q` query parameter.

## Why

The original pagination (2BU-37) was driven by scalability — the dashboard's projects list needed
to handle large workspaces without loading every row at once. Cursor pagination is chosen over
offset because it stays stable when rows are inserted and performs better at depth. The shared
page contract is intentionally reusable for future list endpoints.

The server-side name filter (2BU-39) is a deferred follow-up: past a few hundred projects, users
search rather than scroll. Keeping the filter server-side preserves the pagination model (the
client never receives the full list) and avoids filtering a huge client array. Substring
search (`ILIKE '%term%'`) is a sequential scan within the owner's rows — fine at the
feature's scale (a few hundred projects per owner); a `pg_trgm` GIN index on `name` is the
future lever if lists ever reach tens of thousands.

## Edge cases & gotchas

- A stale cursor can produce an empty page if the referenced project disappears between requests.
  The client should restart from the first page.
- `limit` is a ceiling, not a hard validation error: asking for more than 100 returns 100.
- Empty `cursor` values should not be treated as invalid input.
- The endpoint still scopes results to the current owner; pagination does not change access control.
- The `q` filter is bounded at `.max(200)` — well past any real project name; longer input is
  treated as a malformed/abusive request, not a search.

## References

- Source PR (name filter): https://github.com/Eden-Cohen1/ideascout/pull/62
- Source PR (cursor pagination): https://github.com/Eden-Cohen1/ideascout/pull/42
- Linear issue (name filter): https://linear.app/2builders/issue/2BU-39/server-side-project-search-filter
- Linear issue (pagination): https://linear.app/2builders/issue/2BU-37/add-cursor-pagination-to-get-projects-shared-page-contracts

<!-- provenance: drafted from ideascout PRs #42, #62 -->
