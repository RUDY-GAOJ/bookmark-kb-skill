import json
import os
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class BookmarkKbRefreshTest(unittest.TestCase):
    def test_refresh_writes_jsonl_and_state(self):
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "assets" / "skills" / "bookmark-kb-skill" / "scripts" / "bookmark_kb.py"
        bookmarks_file = repo_root / "test" / "fixtures" / "Bookmarks"

        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["BOOKMARK_KB_HOME"] = tmpdir

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "refresh",
                    "--bookmarks-file",
                    str(bookmarks_file),
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["added"], 2)
            self.assertEqual(payload["store"], tmpdir)

            bookmarks_jsonl = Path(tmpdir) / "bookmarks.jsonl"
            lines = bookmarks_jsonl.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)

            first = json.loads(lines[0])
            second = json.loads(lines[1])
            self.assertEqual(first["title"], "OpenAI Docs")
            self.assertEqual(first["folder_path"], ["Bookmarks Bar", "AI"])
            self.assertTrue(first["id"])
            self.assertEqual(first["status"], "known")
            self.assertEqual(second["title"], "Example")
            self.assertEqual(second["folder_path"], ["Bookmarks Bar"])

            state = json.loads((Path(tmpdir) / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["schema_version"], 1)
            self.assertEqual(state["bookmark_count"], 2)
            self.assertTrue(state["bookmark_file_sha256"])
            self.assertEqual(state["bookmarks_file"], str(bookmarks_file))

    def test_refresh_skips_unchanged_bookmark_file(self):
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "assets" / "skills" / "bookmark-kb-skill" / "scripts" / "bookmark_kb.py"
        bookmarks_file = repo_root / "test" / "fixtures" / "Bookmarks"

        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["BOOKMARK_KB_HOME"] = tmpdir

            first = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "refresh",
                    "--bookmarks-file",
                    str(bookmarks_file),
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            first_payload = json.loads(first.stdout)
            self.assertEqual(first_payload["added"], 2)

            second = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "refresh",
                    "--bookmarks-file",
                    str(bookmarks_file),
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            second_payload = json.loads(second.stdout)

            self.assertTrue(second_payload["unchanged"])
            self.assertEqual(second_payload["added"], 0)
            self.assertEqual(second_payload["updated"], 0)
            self.assertEqual(second_payload["removed"], 0)
            self.assertEqual(second_payload["store"], tmpdir)

    def test_refresh_backfills_missing_category_and_tags_on_unchanged_bookmark_file(self):
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "assets" / "skills" / "bookmark-kb-skill" / "scripts" / "bookmark_kb.py"
        bookmarks_file = repo_root / "test" / "fixtures" / "Bookmarks"

        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["BOOKMARK_KB_HOME"] = tmpdir

            first = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "refresh",
                    "--bookmarks-file",
                    str(bookmarks_file),
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            first_payload = json.loads(first.stdout)
            self.assertEqual(first_payload["added"], 2)

            bookmarks_jsonl = Path(tmpdir) / "bookmarks.jsonl"
            rows = []
            for line in bookmarks_jsonl.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                row.pop("category", None)
                row.pop("tags", None)
                rows.append(row)
            bookmarks_jsonl.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                encoding="utf-8",
            )

            second = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "refresh",
                    "--bookmarks-file",
                    str(bookmarks_file),
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            second_payload = json.loads(second.stdout)

            self.assertTrue(second_payload["unchanged"])
            self.assertTrue(second_payload.get("reclassified"))
            self.assertEqual(second_payload["added"], 0)
            self.assertEqual(second_payload["updated"], 0)
            self.assertEqual(second_payload["removed"], 0)
            self.assertEqual(second_payload["store"], tmpdir)

            refreshed_rows = [
                json.loads(line)
                for line in bookmarks_jsonl.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(refreshed_rows), 2)
            for row in refreshed_rows:
                self.assertIn("category", row)
                self.assertIn("tags", row)
                self.assertIsInstance(row["tags"], list)

    def test_search_returns_compact_result_with_reason(self):
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "assets" / "skills" / "bookmark-kb-skill" / "scripts" / "bookmark_kb.py"
        bookmarks_file = repo_root / "test" / "fixtures" / "Bookmarks"

        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["BOOKMARK_KB_HOME"] = tmpdir

            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "refresh",
                    "--bookmarks-file",
                    str(bookmarks_file),
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "search",
                    "openai docs",
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertGreaterEqual(len(payload["results"]), 1)
            first = payload["results"][0]
            self.assertEqual(first["title"], "OpenAI Docs")
            self.assertIn("title", first["match_reasons"])

    def test_search_returns_empty_results_without_cache(self):
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "assets" / "skills" / "bookmark-kb-skill" / "scripts" / "bookmark_kb.py"

        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["BOOKMARK_KB_HOME"] = tmpdir

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "search",
                    "anything",
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["results"], [])

    def test_context_bundle_writes_markdown_with_sources(self):
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "assets" / "skills" / "bookmark-kb-skill" / "scripts" / "bookmark_kb.py"
        bookmarks_file = repo_root / "test" / "fixtures" / "Bookmarks"

        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["BOOKMARK_KB_HOME"] = tmpdir

            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "refresh",
                    "--bookmarks-file",
                    str(bookmarks_file),
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "context",
                    "openai",
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertTrue(payload["path"])
            self.assertTrue(Path(payload["path"]).exists())
            markdown = Path(payload["path"]).read_text(encoding="utf-8")
            self.assertIn("https://platform.openai.com/docs", markdown)

    def test_organize_exports_duplicate_report_without_execution(self):
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "assets" / "skills" / "bookmark-kb-skill" / "scripts" / "bookmark_kb.py"
        bookmarks_file = repo_root / "test" / "fixtures" / "Bookmarks"

        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["BOOKMARK_KB_HOME"] = tmpdir

            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "refresh",
                    "--bookmarks-file",
                    str(bookmarks_file),
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            bookmarks_jsonl = Path(tmpdir) / "bookmarks.jsonl"
            original_lines = bookmarks_jsonl.read_text(encoding="utf-8").splitlines()
            bookmarks_jsonl.write_text(
                "\n".join(original_lines + [original_lines[0]]) + "\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "organize",
                    "--mode",
                    "all",
                    "--json",
                ],
                cwd=repo_root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertFalse(payload["executed"])
            self.assertTrue(payload["markdown_path"])
            self.assertTrue(Path(payload["markdown_path"]).exists())

    def test_tokenize_returns_set_semantics(self):
        repo_root = Path(__file__).resolve().parents[2]
        script = repo_root / "assets" / "skills" / "bookmark-kb-skill" / "scripts" / "bookmark_kb.py"
        spec = importlib.util.spec_from_file_location("bookmark_kb", script)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        tokens = module.tokenize("OpenAI Docs / Search")
        self.assertIsInstance(tokens, set)
        self.assertEqual(tokens, {"openai", "docs", "search"})


if __name__ == "__main__":
    unittest.main()
