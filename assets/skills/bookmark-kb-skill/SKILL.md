---
name: bookmark-kb-skill
description: Use when you need to refresh a local bookmark knowledge base, search bookmarks, gather bookmark-backed context, or export organization suggestions without changing the browser.
---

# Bookmark KB Skill

Use when a task can benefit from the user's browser bookmarks as a local knowledge base: finding saved resources, gathering source context, or reviewing bookmark organization.

## Workflow

1. Refresh first. Run `refresh` against the current Chrome bookmarks file before searching unless the user explicitly wants to use the existing cache.
2. Search the local cache for quick matches by title, URL, and folder path.
3. Use `context` when the user needs a compact source bundle written to the run directory.
4. Use `organize` only to export suggestions and duplicate reports. It does not execute browser changes, move bookmarks, or delete bookmarks.

## Data Location

Runtime data is stored in the user's home directory by default at `~/.bookmark-kb`. Respect `BOOKMARK_KB_HOME` whenever it is set, including for tests, temporary runs, or user-selected storage.

The cache is local. Refresh writes bookmark rows and state to the runtime store; search and context read from that cache.

## CLI Reference

For exact commands and options, see `references/cli.md`. Prefer that reference when choosing flags such as `--bookmarks-file`, `--mode`, or `--json`.
