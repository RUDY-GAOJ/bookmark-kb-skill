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


if __name__ == "__main__":
    unittest.main()
