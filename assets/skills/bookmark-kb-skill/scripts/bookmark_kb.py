import argparse
import hashlib
import json
import os
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


def refresh(args):
    home = kb_home()
    home.mkdir(parents=True, exist_ok=True)

    raw = Path(args.bookmarks_file).read_bytes()
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
        "bookmark_file_sha256": fingerprint(raw),
    }
    (home / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    result = {"added": len(rows)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("## Refresh")
        print(f"- Added: {len(rows)}")
    return result


def build_parser():
    parser = argparse.ArgumentParser(prog="bookmark_kb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    refresh_parser = subparsers.add_parser("refresh")
    refresh_parser.add_argument("--bookmarks-file", required=True)
    refresh_parser.add_argument("--json", action="store_true")
    refresh_parser.set_defaults(func=refresh)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
