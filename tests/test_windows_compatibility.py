import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PureWindowsPath
from unittest import mock

from scripts import standalone_runner as runner


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "scripts" / "standalone_runner.py"


class WindowsCompatibilityTests(unittest.TestCase):
    def test_command_hints_cover_posix_powershell_and_cmd(self) -> None:
        argv = [
            r"C:\Program Files\Python\python.exe",
            r"C:\briefing skill\standalone_runner.py",
            "digest",
            "--specialty",
            "BESS'; Write-Error should-not-run; #",
        ]

        hints = runner.build_command_hints(argv)

        self.assertEqual(set(hints), {"posix", "windows_powershell", "windows_cmd"})
        self.assertTrue(hints["windows_powershell"].startswith("& 'C:\\Program Files"))
        self.assertIn("BESS''; Write-Error should-not-run; #", hints["windows_powershell"])
        self.assertEqual(hints["windows_cmd"], subprocess.list2cmdline(argv))
        self.assertEqual(
            runner.format_command_hint(argv, "powershell"),
            hints["windows_powershell"],
        )

    def test_windows_host_defaults_to_powershell_hint(self) -> None:
        argv = [r"C:\Python\python.exe", "script with spaces.py"]

        with mock.patch.object(runner.os, "name", "nt"):
            hint = runner.format_command_hint(argv)

        self.assertEqual(hint, runner.build_command_hints(argv)["windows_powershell"])

    def test_artifact_paths_preserve_windows_parents_and_spaces(self) -> None:
        items = PureWindowsPath(r"C:\News Briefing\候选 items.json")
        draft = PureWindowsPath(r"C:\News Briefing\今日 简报.md")

        paths = runner.build_artifact_paths(items, draft)

        self.assertEqual(paths["items_file"], str(items))
        self.assertEqual(
            paths["verification_results_file"],
            str(PureWindowsPath(r"C:\News Briefing\候选 items.verification-results.json")),
        )
        self.assertEqual(paths["digest_output_file"], str(draft))

    def test_utf8_writer_uses_no_bom_and_lf_newlines(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "带 空格" / "简报.md"

            runner.write_utf8_text(output, "第一行\n第二行\n")

            self.assertEqual(output.read_bytes(), "第一行\n第二行\n".encode("utf-8"))

    def test_cli_redirected_output_overrides_ascii_with_utf8(self) -> None:
        environment = dict(os.environ)
        environment["PYTHONIOENCODING"] = "ascii"

        result = subprocess.run(
            [sys.executable, str(RUNNER), "contract"],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            check=True,
        )

        decoded = result.stdout.decode("utf-8")
        self.assertIn("AI与科技", decoded)
        self.assertNotIn(b"\\u4e0e", result.stdout)


if __name__ == "__main__":
    unittest.main()
