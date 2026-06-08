# Install Bookmark KB Skill

You are an AI coding agent. Install Bookmark KB Skill into the current project so the user can search, use as context, and organize their Chrome bookmarks through this skill.

## What To Do

1. Detect your current AI agent platform.
2. Choose the matching platform id:
   - Codex: `codex`
   - Claude Code: `claude`
   - Gemini CLI: `gemini`
   - Cursor: `cursor`
   - OpenCode: `opencode`
   - OpenClaw: `openclaw`
   - Hermes: `hermes`
3. If you cannot confidently detect the platform, ask the user which platform id to use.
4. Run the installer from the current project root:

```sh
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=<platform-id> --scope=project --overwrite
```

Use a comma-separated list only if the user explicitly asks for multiple platforms:

```sh
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex,claude,openclaw,hermes --scope=project --overwrite
```

## Verify

Confirm the installed `bookmark-kb-skill/SKILL.md` exists under the selected platform's skill directory.

After installation, tell the user they can ask:

```text
Use bookmark-kb-skill to search my Chrome bookmarks for AI agent resources.
```

Bookmark KB Skill reads local Chrome bookmark metadata and writes a local cache. It must not modify Chrome bookmarks.
