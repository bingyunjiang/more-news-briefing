import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "standalone_runner.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures"
ITEMS_FILE = FIXTURES / "items.json"
VERIFICATION_RESULTS_FILE = FIXTURES / "verification-results.json"


def run_runner(*args: str) -> tuple[dict, str]:
    result = subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = result.stdout.strip()
    try:
        return json.loads(stdout), stdout
    except json.JSONDecodeError:
        return {}, stdout


class StandaloneRunnerTests(unittest.TestCase):
    def test_finalize_writes_date_named_markdown_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            items_file = tmpdir_path / "items.json"
            items_file.write_text(ITEMS_FILE.read_text(encoding="utf-8"), encoding="utf-8")

            finalize_payload, _ = run_runner(
                "finalize",
                "--items-file",
                str(items_file),
            )

            expected_output = tmpdir_path / f"daily-news-{date.today().isoformat()}.md"
            self.assertEqual(finalize_payload["written_to"], str(expected_output))
            self.assertTrue(expected_output.exists())
            self.assertIn("一次刷尽近期热点", expected_output.read_text(encoding="utf-8"))

    def test_execute_verify_tasks_expose_merge_command_hint(self) -> None:
        payload, _ = run_runner("execute", "--items-file", str(ITEMS_FILE), "--depth", "analyst")
        verify_items = [item for item in payload["execute_queue"]["queue"] if item["phase"] == "verify"]
        self.assertEqual(len(verify_items), 2)
        for item in verify_items:
            self.assertIn("merge_command_hint", item)
            self.assertIn("verify-results", item["merge_command_hint"])
            self.assertIn("--merge", item["merge_command_hint"])
            self.assertTrue(item["result_stub_file"].endswith(".json"))

    def test_verify_builtin_route_is_standardized(self) -> None:
        payload, _ = run_runner("verify", "--items-file", str(ITEMS_FILE), "--mode", "standard")
        plan = payload["verify_execution_plan"]
        self.assertEqual(plan["execution_mode"], "built_in_verification")
        self.assertIn("builtin_verification_tasks", plan)
        self.assertGreaterEqual(len(plan["builtin_verification_tasks"]), 1)
        first_task = plan["builtin_verification_tasks"][0]
        self.assertIn("result_template", first_task)
        self.assertEqual(first_task["result_template"]["verdict"], "")
        self.assertIn("judgment_options", first_task)

    def test_verify_results_merge_and_finalize(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            shared_verify_file = tmpdir_path / "shared.verification-results.json"
            digest_output_file = tmpdir_path / "final.digest.txt"

            init_payload, _ = run_runner(
                "verify-results",
                "--items-file",
                str(ITEMS_FILE),
                "--output-file",
                str(shared_verify_file),
            )
            self.assertEqual(init_payload["write_mode"], "overwrite")
            self.assertTrue(shared_verify_file.exists())

            merge_payload, _ = run_runner(
                "verify-results",
                "--items-file",
                str(ITEMS_FILE),
                "--results-file",
                str(VERIFICATION_RESULTS_FILE),
                "--output-file",
                str(shared_verify_file),
                "--merge",
            )
            self.assertEqual(merge_payload["write_mode"], "merge")
            merged_file = json.loads(shared_verify_file.read_text(encoding="utf-8"))
            self.assertEqual(len(merged_file["results"]), 2)

            finalize_payload, _ = run_runner(
                "finalize",
                "--items-file",
                str(ITEMS_FILE),
                "--verification-results-file",
                str(shared_verify_file),
                "--output-file",
                str(digest_output_file),
                "--format",
                "analyst_watch",
            )
            self.assertEqual(finalize_payload["written_to"], str(digest_output_file))
            digest_text = digest_output_file.read_text(encoding="utf-8")
            self.assertIn("BLS发布6月就业报告", digest_text)
            self.assertIn("继续跟踪", digest_text)
            self.assertIn("G7发布地缘政治声明", digest_text)


if __name__ == "__main__":
    unittest.main()
