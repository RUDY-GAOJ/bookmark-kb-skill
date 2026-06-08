# Contributing

Thanks for helping improve Bookmark KB Skill.

## Local Setup

Requirements:

- Node.js 20 or newer
- npm 10 or newer
- Python 3

Run checks:

```sh
npm test
npm run pack:check
```

## Development Notes

- Keep the public interface npm-first. Users should call `bookmark-kb-skill` or `bookmark-kb`, not the internal Python script directly.
- Keep normal search local and cache-based. Do not add website crawling to search paths.
- Organization commands must not modify Chrome bookmarks unless a future explicit feature adds reviewed execution.
- Prefer standard-library code unless a dependency is clearly justified.

## Pull Requests

Please include:

- A short summary of behavior changes.
- Test coverage for new commands or flags.
- The output of `npm test`.
