import json
import os
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


if __name__ == "__main__":
    unittest.main()
