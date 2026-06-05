import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import sys


def kb_home():
    home = os.environ.get("BOOKMARK_KB_HOME")
    if home:
        return Path(home)
    return Path.home() / ".bookmark-kb"


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
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def tokenize(text):
    if not text:
        return []
    return [part for part in re.split(r"[\s/\-]+", str(text).lower()) if part]


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


def refresh(args):
    home = kb_home()
    home.mkdir(parents=True, exist_ok=True)

    raw = Path(args.bookmarks_file).read_bytes()
    raw_hash = fingerprint(raw)
    state = load_state(home)
    if state and state.get("bookmark_file_sha256") == raw_hash:
        result = {
            "unchanged": True,
            "added": 0,
            "updated": 0,
            "removed": 0,
            "store": state,
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
            rows.extend(walk_bookmarks(root))

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
        "store": state,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("## Refresh")
        print(f"- Added: {len(rows)}")
    return result


def search(args):
    home = kb_home()
    query = " ".join(args.query) if isinstance(args.query, list) else str(args.query)
    query_tokens = tokenize(query)
    rows_path = home / "bookmarks.jsonl"
    rows = read_jsonl(rows_path) if rows_path.exists() else []

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
    compact_results = [{k: v for k, v in item.items() if k != "_score"} for item in results[:10]]
    payload = {"query": query, "results": compact_results}

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print("## Search")
        for item in compact_results:
            print(f"- {item['title']} - {item['url']}")
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

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
