---
id: projects-pagination
title: Projects pagination and shared page contracts
sidebar_position: 2
---

# Projects pagination and shared page contracts

This page documents the backend/shared contract change in ideascout PR #42: `GET /projects`
moved from a bare array to a cursor-paginated page, and `packages/shared` gained the reusable
page contract used by that endpoint and future list endpoints.

## Purpose

Keep large project lists fast to load and make the page shape reusable for future list APIs
without each endpoint inventing its own pagination DTO.

## Behavior

- `PageQuerySchema` accepts `{ cursor?, limit }`.
- `limit` comes from the query string, defaults to 20, and is clamped to 100.
- An empty `cursor` is treated like "first page".
- `ProjectPageSchema` is `pageSchema(ProjectResponseSchema)` and returns
  `{ items, nextCursor }`.
- `GET /projects` now returns a page instead of an array.
- The service orders by `createdAt desc, id desc` so the sort is total when timestamps tie.
- Pagination uses `take: limit + 1` to derive `nextCursor` without a count query.
- Subsequent pages use Prisma `cursor` + `skip: 1`.
- `nextCursor: null` means there is no next page.
- Swagger documents the query parameters and page response.

## Why

Linear 2BU-37 says the dashboard's projects list needs to scale to large workspaces and eventually
feed infinite scroll. Cursor pagination is chosen over offset because it stays stable when rows are
inserted and performs better at depth. The shared page contract is intentionally reusable for
future ideas/research lists, so the API shape is a contract rather than a one-off endpoint tweak.

## Edge cases & gotchas

- A stale cursor can produce an empty page if the referenced project disappears between requests.
  The client should restart from the first page.
- `limit` is a ceiling, not a hard validation error: asking for more than 100 returns 100.
- Empty `cursor` values should not be treated as invalid input.
- The endpoint still scopes results to the current owner; pagination does not change access control.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/42
- Linear issue: https://linear.app/2builders/issue/2BU-37/add-cursor-pagination-to-get-projects-shared-page-contracts

<!-- provenance: drafted from ideascout PR #42 -->
