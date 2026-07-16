import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from scripts import standalone_runner as runner


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


def run_runner_in_process(*args: str) -> tuple[dict, str]:
    output = io.StringIO()
    with mock.patch.object(sys, "argv", [str(RUNNER), *args]), contextlib.redirect_stdout(output):
        return_code = runner.main()
    if return_code != 0:
        raise AssertionError(f"runner returned {return_code}")
    stdout = output.getvalue().strip()
    try:
        return json.loads(stdout), stdout
    except json.JSONDecodeError:
        return {}, stdout


class StandaloneRunnerTests(unittest.TestCase):
    def test_all_cli_commands_run_in_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            items_file = tmpdir_path / "items.json"
            results_file = tmpdir_path / "results.json"
            prepared_file = tmpdir_path / "prepared.json"
            verification_output = tmpdir_path / "shared.verification-results.json"
            final_output = tmpdir_path / "final.md"
            draft_file = tmpdir_path / "draft.md"
            items_file.write_text(ITEMS_FILE.read_text(encoding="utf-8"), encoding="utf-8")
            results_file.write_text(
                VERIFICATION_RESULTS_FILE.read_text(encoding="utf-8"), encoding="utf-8"
            )
            draft_file.write_text("一次刷尽近期热点，高效工作一整天\n", encoding="utf-8")

            common = (
                "--time-window",
                "last_7d",
                "--cadence",
                "weekly",
                "--topic-mix",
                "AI与科技,专项关注",
                "--depth",
                "analyst",
                "--format",
                "long_message",
                "--audience",
                "research",
                "--mode",
                "full",
                "--cognitive-features",
                "interrogate,sprout,commentary,continuity",
                "--specialty",
                "BESS",
                "--specialty-scope",
                "grid-scale storage",
                "--specialty-keywords",
                "BESS,储能",
                "--specialty-exclusions",
                "户储",
                "--specialty-geography",
                "China",
                "--specialty-priority",
                "policy",
                "--source-roles",
                "discovery,verification,watch",
                "--company-watchlist",
                "CATL",
                "--institution-watchlist",
                "国家能源局",
                "--community-watchlist",
                "OpenEMS",
            )

            json_commands = [
                ("contract", *common),
                ("queries", *common, "--flat"),
                ("adapters", "--available-only"),
                ("route", *common),
                ("collect", *common),
                ("verify", *common, "--items-file", str(items_file)),
                (
                    "polish",
                    *common,
                    "--items-file",
                    str(items_file),
                    "--draft-file",
                    str(draft_file),
                ),
                (
                    "pipeline",
                    *common,
                    "--items-file",
                    str(items_file),
                    "--draft-file",
                    str(draft_file),
                ),
                (
                    "execute",
                    *common,
                    "--items-file",
                    str(items_file),
                    "--draft-file",
                    str(draft_file),
                ),
                (
                    "prepare",
                    *common,
                    "--items-file",
                    str(items_file),
                    "--output-file",
                    str(prepared_file),
                ),
                (
                    "verify-results",
                    "--items-file",
                    str(items_file),
                    "--results-file",
                    str(results_file),
                    "--output-file",
                    str(verification_output),
                ),
                (
                    "verify-results",
                    "--items-file",
                    str(items_file),
                    "--results-file",
                    str(results_file),
                    "--output-file",
                    str(verification_output),
                    "--merge",
                ),
                (
                    "finalize",
                    *common,
                    "--items-file",
                    str(items_file),
                    "--verification-results-file",
                    str(verification_output),
                    "--output-file",
                    str(final_output),
                ),
            ]

            for command in json_commands:
                payload, stdout = run_runner_in_process(*command)
                self.assertTrue(payload, msg=f"expected JSON output for {command[0]}: {stdout}")

            for output_format in (
                "quick_brief",
                "standard_digest",
                "analyst_watch",
                "long_message",
                "long_message_exec",
            ):
                _payload, stdout = run_runner_in_process(
                    "digest",
                    "--items-file",
                    str(items_file),
                    "--format",
                    output_format,
                )
                self.assertIn("一次刷尽近期热点", stdout)

            self.assertTrue(prepared_file.exists())
            self.assertTrue(verification_output.exists())
            self.assertTrue(final_output.exists())

    def test_prepare_writes_normalized_ranked_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "prepared.json"

            payload, _ = run_runner(
                "prepare",
                "--items-file",
                str(ITEMS_FILE),
                "--output-file",
                str(output_file),
            )

            self.assertEqual(payload["written_to"], str(output_file))
            prepared = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertTrue(prepared)
            self.assertTrue(all(item.get("item_id") for item in prepared))
            self.assertEqual(payload["items"], prepared)

    def test_finalize_rejects_blocking_items_without_writing_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            items_file = tmpdir_path / "invalid-items.json"
            output_file = tmpdir_path / "should-not-exist.md"
            items_file.write_text(
                json.dumps([{"title": "Missing evidence"}]),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "finalize",
                    "--items-file",
                    str(items_file),
                    "--output-file",
                    str(output_file),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("failed acceptance", result.stderr)
            self.assertFalse(output_file.exists())

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
        payload, _ = run_runner(
            "execute",
            "--items-file",
            str(ITEMS_FILE),
            "--depth",
            "analyst",
            "--cognitive-features",
            "interrogate,sprout",
        )
        verify_items = [item for item in payload["execute_queue"]["queue"] if item["phase"] == "verify"]
        self.assertEqual(len(verify_items), 2)
        for item in verify_items:
            self.assertIn("merge_command_hint", item)
            self.assertIn("verify-results", item["merge_command_hint"])
            self.assertIn("--merge", item["merge_command_hint"])
            self.assertTrue(item["result_stub_file"].endswith(".json"))
        self.assertEqual(payload["contract_summary"]["cognitive_features"], ["interrogate", "sprout"])
        self.assertIn("--cognitive-features", payload["digest_command_argv"])
        self.assertIn("interrogate,sprout", payload["digest_command_argv"])

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
