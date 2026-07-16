---
id: project-creation-from-dashboard
title: Project creation from the dashboard
sidebar_position: 4
---

# Project creation from the dashboard

## Purpose

The Projects dashboard now gives signed-in users a first-class way to create a new project.
The empty-state CTA shipped in 2BU-33 now leads into the same flow as the top-level
“New project” button.

## Behavior

- `ProjectsView` shows a `New project` button in the header and the same action in the empty state.
- Both buttons open `CreateProjectDialog`.
- The dialog collects a required `name` and optional `description`.
- Validation uses `CreateProjectRequestSchema`, so the client and API share the same rules.
- A blank description is trimmed away instead of being sent as `""`.
- While submission is in flight, the submit button reads `Creating…` and stays disabled.
- On success, the store creates the project, the dialog closes, and the new project is emitted back to the view.
- On server failure, the dialog stays open and shows the error inline.

## Why

PR #48 closes 2BU-34: the dashboard needed the missing create action behind the empty-state
CTA from 2BU-33. The goal is to let a signed-in user start a new project without leaving
the Projects page.

## Edge cases & gotchas

- `name` is required; the shared schema surfaces the message “Project name is required.”
  both inline and in the API response.
- Reopening the dialog resets prior inputs and errors.
- Cancel simply closes the dialog; it does not create a project.
- The flow assumes the user is already signed in because it runs on the authenticated
  Projects dashboard.

## References

- Source PR: https://github.com/Eden-Cohen1/ideascout/pull/48
- Linear issue: 2BU-34

<!-- provenance: draft from ideascout PR #48 -->
