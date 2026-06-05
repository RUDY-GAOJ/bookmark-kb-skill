# Bookmark KB CLI

Install or run with npm/npx:

```sh
npx bookmark-kb-skill install --platforms=codex --scope=project --overwrite
npx bookmark-kb-skill refresh --json
```

Runtime data defaults to `~/.bookmark-kb`. Set `BOOKMARK_KB_HOME` to use another cache directory.

## Chrome Bookmarks File

Chrome's default profile usually stores bookmarks at:

- Windows: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`
- macOS: `~/Library/Application Support/Google/Chrome/Default/Bookmarks`
- Linux: `~/.config/google-chrome/Default/Bookmarks`

`refresh` uses that default path when no `--bookmarks-file` is provided. Use `--bookmarks-file` to point at another Chrome profile's `Bookmarks` file.

## Commands

Refresh the local cache first:

```sh
bookmark-kb refresh
bookmark-kb refresh --json
bookmark-kb refresh --bookmarks-file "<path-to-Bookmarks>"
bookmark-kb refresh --bookmarks-file "<path-to-Bookmarks>" --json
```

Search cached bookmarks:

```sh
bookmark-kb search openai docs
bookmark-kb search openai docs --json
```

Write a compact context bundle under the run directory:

```sh
bookmark-kb context openai docs
bookmark-kb context openai docs --json
```

Export organization suggestions and duplicate reports without executing changes:

```sh
bookmark-kb organize --mode all
bookmark-kb organize --mode all --json
```

`organize` reports `executed: false`; review the exported Markdown or JSON before making any browser changes manually.

The `bookmark-kb` command is a Node wrapper. It may use the bundled Python implementation internally, but users and agents should call the npm command.
