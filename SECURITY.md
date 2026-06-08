# Security Policy

## Supported Versions

The current `0.x` line receives security fixes.

## Reporting A Vulnerability

Please report security issues privately through GitHub's security advisory flow if available, or by opening a minimal issue that avoids sensitive details.

## Security Model

- Bookmark data is read from the local Chrome `Bookmarks` file.
- Runtime cache data is stored locally under `~/.bookmark-kb` or `BOOKMARK_KB_HOME`.
- The first version does not modify Chrome bookmarks.
- Normal search does not crawl bookmarked websites.
