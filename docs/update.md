# Update Bookmark KB Skill

You are an AI coding agent. Update Bookmark KB Skill in the current project.

## What To Do

1. Detect which platform skill directories already contain `bookmark-kb-skill/SKILL.md`.
2. Map those directories to platform ids:
   - `.codex/skills` -> `codex`
   - `.claude/skills` -> `claude`
   - `.gemini/skills` -> `gemini`
   - `.cursor/skills` -> `cursor`
   - `.opencode/skills` -> `opencode`
   - `.openclaw/workspace/skills` -> `openclaw`
   - `.hermes/skills` -> `hermes`
3. If no existing installation is found, detect your current AI agent platform and install for that platform.
4. Run the installer with `--overwrite` from the current project root:

```sh
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=<platform-id-or-list> --scope=project --overwrite
```

## Verify

Confirm `bookmark-kb-skill/SKILL.md` exists under each selected platform's skill directory after the update.
