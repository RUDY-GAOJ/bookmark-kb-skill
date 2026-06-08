<p align="center">
  <img src="docs/hero.svg" alt="Bookmark KB Skill - Chrome bookmarks to local AI context" width="100%" />
</p>

<p align="center">
  <a href="docs/README.zh-CN.md">中文</a>
  ·
  <a href="#agent-quick-install">Agent Quick Install</a>
  ·
  <a href="#human-installation">Human Installation</a>
</p>

<p align="center">
  <a href="https://github.com/RUDY-GAOJ/bookmark-kb-skill/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/RUDY-GAOJ/bookmark-kb-skill/actions/workflows/ci.yml/badge.svg" /></a>
  <a href="https://github.com/RUDY-GAOJ/bookmark-kb-skill/releases/tag/v0.1.0"><img alt="Release" src="https://img.shields.io/github/v/release/RUDY-GAOJ/bookmark-kb-skill?display_name=tag" /></a>
  <a href="https://github.com/RUDY-GAOJ/bookmark-kb-skill/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/RUDY-GAOJ/bookmark-kb-skill" /></a>
</p>

# Bookmark KB Skill

Turn Chrome bookmarks into a local, low-token knowledge base for AI agents.

`bookmark-kb-skill` installs a platform-neutral Agent Skill into common AI tool skill directories, and provides an npm CLI for refreshing, searching, exporting context bundles, and generating organization reports.

The user-facing interface is npm/npx. The package keeps a small Python standard-library script internally for portable local bookmark processing.

## Agent Quick Install

Copy this into your AI coding agent:

```text
Install bookmark-kb-skill into this project for Codex. Use:
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex --scope=project --overwrite
Then refresh my Chrome bookmarks and search them when I ask bookmark-related questions.
```

For Codex + Claude:

```text
Install bookmark-kb-skill into this project for Codex and Claude. Use:
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex,claude --scope=project --overwrite
Then use bookmark-kb-skill when I ask to search, use, or organize my Chrome bookmarks.
```

## Human Installation

After npm publication:

```sh
npx bookmark-kb-skill install --platforms=codex --scope=project --overwrite
```

Install into more than one platform:

```sh
npx bookmark-kb-skill install --platforms=codex,claude --scope=project --overwrite
```

Install from GitHub before npm publication:

```sh
npm exec --yes --package github:RUDY-GAOJ/bookmark-kb-skill -- bookmark-kb-skill install --platforms=codex --scope=project --overwrite
```

Install from a local checkout:

```sh
npm exec --package . -- bookmark-kb-skill install --platforms=codex --scope=project --overwrite
```

Supported platform ids:

- `codex`
- `claude`
- `gemini`
- `cursor`
- `opencode`

Project scope installs under the current directory. Global scope installs under the user profile where supported:

```sh
npx bookmark-kb-skill install --platforms=codex --scope=global --overwrite
```

## Features

- Install the same Skill package into Codex, Claude, Gemini, Cursor, or OpenCode skill directories.
- Read the default Chrome `Bookmarks` file, or use `--bookmarks-file` for another profile.
- Cache normalized bookmark records locally under `~/.bookmark-kb`.
- Search by title, URL, folder path, category, and tags without crawling websites on every query.
- Export compact context bundles for later AI tasks.
- Export organization reports without modifying Chrome bookmarks.
- Use Markdown output by default and JSON output with `--json`.

## Requirements

- Node.js 20 or newer.
- npm 10 or newer.
- Python available as `python` on Windows or `python3` / `python` on macOS and Linux.

Set `BOOKMARK_KB_PYTHON` if Python is installed at a custom path.

## Use The Bookmark CLI

Refresh the local cache:

```sh
bookmark-kb refresh --json
```

Search cached bookmarks:

```sh
bookmark-kb search "openai docs" --json
```

Create a compact context bundle:

```sh
bookmark-kb context "openai docs" --json
```

Export an organization report:

```sh
bookmark-kb organize --mode all --json
```

Use a temporary cache while testing:

```sh
BOOKMARK_KB_HOME=.tmp-bookmark-kb bookmark-kb refresh --json
```

Use an explicit Chrome profile file:

```sh
bookmark-kb refresh --bookmarks-file "/path/to/Chrome/User Data/Default/Bookmarks" --json
```

## Agent Usage

After installation, open a new AI tool session and ask naturally:

```text
Use bookmark-kb-skill to search my Chrome bookmarks for AI agent resources.
```

```text
Use my bookmarked OpenAI API links as context for this planning task.
```

```text
Organize my Chrome bookmarks and report duplicate links.
```

## Data And Privacy

Runtime data is local by default:

```text
~/.bookmark-kb
```

Set `BOOKMARK_KB_HOME` to use another directory.

The first version does not modify Chrome bookmarks and does not crawl saved websites during normal search. It reads bookmark titles, URLs, and folder paths from Chrome's local `Bookmarks` file.

## Development

```sh
npm test
npm run pack:check
```

Run a realistic local npx smoke test:

```sh
npm pack
npx --yes --package ./bookmark-kb-skill-0.1.0.tgz bookmark-kb-skill --help
```

## Publishing

Before publishing:

```sh
npm test
npm run pack:check
npm publish
```

The package is configured with `publishConfig.access=public`.

## Stars

<p align="center">
  <a href="https://github.com/RUDY-GAOJ/bookmark-kb-skill/stargazers">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/RUDY-GAOJ/bookmark-kb-skill?style=social" />
  </a>
</p>

## License

MIT
