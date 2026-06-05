# Bookmark KB Skill

Install and run a platform-neutral bookmark knowledge base skill.

## Install The Skill

From a published package:

```sh
npx bookmark-kb-skill install --platforms=codex --scope=project --overwrite
```

From this repository checkout:

```sh
npm exec --package . -- bookmark-kb-skill install --platforms=codex --scope=project --overwrite
```

Supported platform ids: `codex`, `claude`, `gemini`, `cursor`, `opencode`.

## Use The Bookmark CLI

```sh
bookmark-kb refresh --json
bookmark-kb search "openai docs" --json
bookmark-kb context "openai docs" --json
bookmark-kb organize --mode all --json
```

Runtime data defaults to `~/.bookmark-kb`. Set `BOOKMARK_KB_HOME` to test with a temporary cache.

The npm command is the user-facing interface. The package keeps the Python script as an internal portable implementation detail.
