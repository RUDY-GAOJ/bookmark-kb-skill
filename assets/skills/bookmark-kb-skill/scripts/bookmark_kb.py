import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
import sys


def kb_home():
    home = os.environ.get("BOOKMARK_KB_HOME")
    if home:
        return Path(home)
    return Path.home() / ".bookmark-kb"


def runs_dir():
    path = kb_home() / "runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def fingerprint(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def bookmark_id(row):
    payload = json.dumps(
        {
            "folder_path": row["folder_path"],
            "title": row["title"],
            "url": row["url"],
        },
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_bookmarks(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def tokenize(text):
    if not text:
        return set()
    return {part for part in re.split(r"[\s/\-]+", str(text).lower()) if part}


def classify(row):
    text = " ".join(
        str(part)
        for part in (
            row.get("title", ""),
            row.get("url", ""),
            "/".join(row.get("folder_path", [])),
        )
    ).lower()
    if "openai" in text or " ai" in f" {text}" or text.startswith("ai"):
        return "AI", ["ai"]
    if "docs" in text or "documentation" in text:
        return "Documentation", ["docs"]
    return "Needs Review", []


def walk_bookmarks(node, folder_path=None):
    folder_path = list(folder_path or [])
    node_type = node.get("type")
    name = node.get("name")

    if node_type == "folder":
        next_path = folder_path + ([name] if name else [])
        for child in node.get("children", []):
            yield from walk_bookmarks(child, next_path)
        return

    if node_type == "url":
        row = {
            "title": name,
            "url": node.get("url"),
            "folder_path": folder_path,
        }
        row["id"] = bookmark_id(row)
        row["status"] = "known"
        yield row


def normalized_url(url):
    return str(url or "").lower().rstrip("/")


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def load_state(home):
    state_path = home / "state.json"
    if not state_path.exists():
        return None
    return json.loads(state_path.read_text(encoding="utf-8"))


def load_bookmark_rows(home=None):
    home = home or kb_home()
    rows_path = home / "bookmarks.jsonl"
    return read_jsonl(rows_path) if rows_path.exists() else []


def search_rows(query, limit=10):
    query_tokens = tokenize(query)
    rows = load_bookmark_rows()

    results = []
    for row in rows:
        title = row.get("title", "")
        url = row.get("url", "")
        folder_path = "/".join(row.get("folder_path", []))

        title_tokens = set(tokenize(title))
        url_tokens = set(tokenize(url))
        folder_tokens = set(tokenize(folder_path))

        match_reasons = []
        score = 0
        if any(token in title_tokens for token in query_tokens):
            match_reasons.append("title")
            score += 3
        if any(token in folder_tokens for token in query_tokens):
            match_reasons.append("folder_path")
            score += 2
        if any(token in url_tokens for token in query_tokens):
            match_reasons.append("url")
            score += 1

        if not match_reasons:
            continue

        results.append(
            {
                "id": row.get("id", ""),
                "title": title,
                "url": url,
                "summary": row.get("summary") or "",
                "tags": row.get("tags") or [],
                "category": row.get("category") or "Unclassified",
                "match_reasons": match_reasons,
                "_score": score,
            }
        )

    results.sort(key=lambda item: (-item["_score"], item["title"].lower(), item["url"]))
    compact_results = [{k: v for k, v in item.items() if k != "_score"} for item in results[:limit]]
    return {"query": query, "results": compact_results}


def refresh(args):
    home = kb_home()
    home.mkdir(parents=True, exist_ok=True)

    raw = Path(args.bookmarks_file).read_bytes()
    raw_hash = fingerprint(raw)
    state = load_state(home)
    if state and state.get("bookmark_file_sha256") == raw_hash:
        rows_path = home / "bookmarks.jsonl"
        rows = read_jsonl(rows_path)
        reclassified = False
        for row in rows:
            if "category" not in row or "tags" not in row:
                category, tags = classify(row)
                row["category"] = category
                row["tags"] = tags
                reclassified = True
        if reclassified:
            write_jsonl(rows_path, rows)
        result = {
            "unchanged": True,
            "reclassified": reclassified,
            "added": 0,
            "updated": 0,
            "removed": 0,
            "store": str(home),
        }
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("## Refresh")
            print("- Unchanged: true")
        return result

    bookmarks = read_bookmarks(args.bookmarks_file)

    rows = []
    roots = bookmarks.get("roots", {})
    for root_key in ("bookmark_bar", "other", "synced"):
        root = roots.get(root_key)
        if root:
            for row in walk_bookmarks(root):
                category, tags = classify(row)
                row["category"] = category
                row["tags"] = tags
                rows.append(row)

    write_jsonl(home / "bookmarks.jsonl", rows)

    state = {
        "schema_version": 1,
        "bookmarks_file": str(Path(args.bookmarks_file)),
        "bookmark_count": len(rows),
        "bookmark_file_sha256": raw_hash,
    }
    (home / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    result = {
        "unchanged": False,
        "added": len(rows),
        "updated": 0,
        "removed": 0,
        "store": str(home),
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("## Refresh")
        print(f"- Added: {len(rows)}")
    return result


def search(args):
    query = " ".join(args.query) if isinstance(args.query, list) else str(args.query)
    payload = search_rows(query, limit=10)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print("## Search")
        for item in payload["results"]:
            print(f"- {item['title']} - {item['url']}")
    return payload


def context(args):
    query = " ".join(args.query) if isinstance(args.query, list) else str(args.query)
    payload = search_rows(query, limit=5)
    items = payload["results"]
    path = runs_dir() / f"context-{stamp()}.md"
    lines = [f"# Context: {query}", ""]
    for item in items:
        lines.append(f"- {item['title']} | {item['url']} | Category: {item['category']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = {"query": query, "path": str(path), "items": items}

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"## Context: {query}")
        for item in items:
            print(f"- {item['title']} - {item['url']} ({item['category']})")
    return result


def organize(args):
    home = kb_home()
    rows = load_bookmark_rows(home)
    groups = {}
    for row in rows:
        key = normalized_url(row.get("url"))
        groups.setdefault(key, []).append(row)

    duplicate_groups = []
    for url, items in groups.items():
        if len(items) > 1 and url:
            duplicate_groups.append(
                {
                    "normalized_url": url,
                    "count": len(items),
                    "items": [
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "folder_path": item.get("folder_path", []),
                            "category": item.get("category", "Unclassified"),
                        }
                        for item in items
                    ],
                }
            )

    path_base = runs_dir() / f"organize-{stamp()}"
    markdown_path = path_base.with_suffix(".md")
    json_path = path_base.with_suffix(".json")
    markdown_lines = [f"# Organize Report", f"- Mode: {args.mode}", f"- Duplicate groups: {len(duplicate_groups)}", ""]
    for group in duplicate_groups:
        markdown_lines.append(f"## {group['normalized_url']}")
        for item in group["items"]:
            markdown_lines.append(f"- {item['title']} | {item['url']} | Category: {item['category']}")
        markdown_lines.append("")
    markdown_path.write_text("\n".join(markdown_lines).rstrip() + "\n", encoding="utf-8")

    payload = {
        "executed": False,
        "mode": args.mode,
        "duplicate_groups": duplicate_groups,
        "markdown_path": str(markdown_path),
        "json_path": str(json_path),
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print("## Organize")
        print(f"- Executed: false")
        print(f"- Duplicate groups: {len(duplicate_groups)}")
    return payload


def build_parser():
    parser = argparse.ArgumentParser(prog="bookmark_kb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    refresh_parser = subparsers.add_parser("refresh")
    refresh_parser.add_argument("--bookmarks-file", required=True)
    refresh_parser.add_argument("--json", action="store_true")
    refresh_parser.set_defaults(func=refresh)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query", nargs="+")
    search_parser.add_argument("--json", action="store_true")
    search_parser.set_defaults(func=search)

    context_parser = subparsers.add_parser("context")
    context_parser.add_argument("query", nargs="+")
    context_parser.add_argument("--json", action="store_true")
    context_parser.set_defaults(func=context)

    organize_parser = subparsers.add_parser("organize")
    organize_parser.add_argument("--mode", default="all")
    organize_parser.add_argument("--json", action="store_true")
    organize_parser.set_defaults(func=organize)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
