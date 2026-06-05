# Bookmark KB CLI

Run the bundled script from the skill directory:

```sh
python scripts/bookmark_kb.py <command> [options]
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
python scripts/bookmark_kb.py refresh
python scripts/bookmark_kb.py refresh --json
python scripts/bookmark_kb.py refresh --bookmarks-file "<path-to-Bookmarks>"
python scripts/bookmark_kb.py refresh --bookmarks-file "<path-to-Bookmarks>" --json
```

Search cached bookmarks:

```sh
python scripts/bookmark_kb.py search openai docs
python scripts/bookmark_kb.py search openai docs --json
```

Write a compact context bundle under the run directory:

```sh
python scripts/bookmark_kb.py context openai docs
python scripts/bookmark_kb.py context openai docs --json
```

Export organization suggestions and duplicate reports without executing changes:

```sh
python scripts/bookmark_kb.py organize --mode all
python scripts/bookmark_kb.py organize --mode all --json
```

`organize` reports `executed: false`; review the exported Markdown or JSON before making any browser changes manually.
