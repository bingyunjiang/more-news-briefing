import argparse
import json
import shlex
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import standalone_runner as runner


class RunnerHardeningTests(unittest.TestCase):
    def test_verification_contract_requires_verdict_and_declares_identity_fields(self) -> None:
        contract = runner.build_verification_result_contract()

        self.assertEqual(contract["required_fields"], ["verdict"])
        self.assertEqual(
            contract["identity_fields"],
            {
                "at_least_one": ["item_id", "canonical_url", "title"],
                "preference_order": ["item_id", "canonical_url", "title"],
                "title_fallback": "unique_titles_only",
            },
        )

    def test_anysearch_commands_expose_shell_safe_argv(self) -> None:
        contract = runner.Contract(
            specialty="BESS'; touch /tmp/should-not-run; echo '",
            specialty_keywords=["BESS'; touch /tmp/should-not-run; echo '"],
            topic_mix=["专项关注"],
        )

        batch = runner.build_anysearch_batches(contract)[0]

        self.assertIsInstance(batch["command_argv"], list)
        self.assertEqual(batch["command_hint"], shlex.join(batch["command_argv"]))
        self.assertIn("touch /tmp/should-not-run", batch["command_argv"][-1])

    def test_unknown_verification_verdict_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown verification verdict"):
            runner.normalize_verification_result({"title": "A", "verdict": "banana"})

    def test_incomplete_or_unsourced_item_moves_to_follow_up(self) -> None:
        main_items, follow_ups = runner.split_items([{"title": "Unverified"}])

        self.assertEqual(main_items, [])
        self.assertIn("Unverified", follow_ups)

    def test_verification_uses_item_id_before_duplicate_title(self) -> None:
        items = [
            {
                "item_id": "story-a",
                "title": "Same title",
                "what": "A",
                "why": "A impact",
                "bucket": "AI与科技",
                "source_level": "次选证据",
                "evidence_status": "交叉验证中",
                "sources": ["source-a"],
            },
            {
                "item_id": "story-b",
                "title": "Same title",
                "what": "B",
                "why": "B impact",
                "bucket": "AI与科技",
                "source_level": "次选证据",
                "evidence_status": "交叉验证中",
                "sources": ["source-b"],
            },
        ]
        results = [
            {
                "item_id": "story-b",
                "title": "Same title",
                "verdict": "confirm",
                "source_level": "首选证据",
                "evidence_status": "已确认",
                "sources": ["official-b"],
            }
        ]

        updated = runner.apply_verification_results(items, results)

        self.assertEqual(updated[0]["source_level"], "次选证据")
        self.assertEqual(updated[1]["source_level"], "首选证据")
        self.assertEqual(updated[1]["sources"], ["official-b"])

    def test_specialty_scope_exclusions_and_watchlists_drive_queries(self) -> None:
        contract = runner.Contract(
            specialty="储能",
            specialty_scope="grid-scale BESS",
            specialty_keywords=["储能", "BESS"],
            specialty_exclusions=["户储", "consumer battery"],
            specialty_geography="China",
            specialty_priority="policy",
            topic_mix=["专项关注"],
            company_watchlist=["CATL"],
            institution_watchlist=["国家能源局"],
            community_watchlist=["OpenEMS"],
        )

        queries = runner.build_queries(contract)
        source_targets = runner.build_source_targets(contract)

        specialty_queries = " ".join(
            query
            for group in queries["专项关注"].values()
            for query in group
        )
        self.assertIn("grid-scale BESS", specialty_queries)
        self.assertIn("-户储", specialty_queries)
        self.assertIn("CATL", specialty_queries)
        self.assertIn("国家能源局", specialty_queries)
        self.assertIn("OpenEMS", specialty_queries)
        self.assertIn("watchlists", source_targets)
        self.assertIn("source_packs", source_targets)

    def test_execute_queue_has_complete_artifact_chain(self) -> None:
        contract = runner.Contract(mode="standard")
        collect_plan = runner.build_collect_execution_plan(contract)
        verify_plan = runner.build_verify_execution_plan(contract, [])
        polish_plan = runner.build_polish_execution_plan(contract)
        handoff = runner.build_handoff_package(
            contract,
            collect_plan,
            verify_plan,
            polish_plan,
            runner.build_artifact_paths(),
        )

        queue = runner.build_execute_queue(handoff)["queue"]
        phases = [item["phase"] for item in queue]

        self.assertEqual(
            phases,
            ["collect", "normalize", "rank", "verify", "render", "cognition", "acceptance", "polish"],
        )
        produced = {item.get("produces_artifact") for item in queue}
        consumed = {item.get("consumes_artifact") for item in queue}
        self.assertIn("candidate_pool", produced)
        self.assertIn("candidate_pool", consumed)
        self.assertIn("retained_items", produced)
        self.assertIn("retained_items", consumed)
        self.assertIn("final_briefing", produced)

    def test_execute_commands_expose_safe_merge_and_digest_argv(self) -> None:
        contract = runner.Contract(mode="standard")
        items = [
            {
                "title": "Quoted ' title",
                "what": "Event",
                "why": "Impact",
                "bucket": "AI与科技",
                "source_level": "次选证据",
                "evidence_status": "交叉验证中",
                "sources": ["source"],
            }
        ]
        artifact_paths = runner.build_artifact_paths(
            Path("items with spaces.json"), Path("digest with spaces.md")
        )
        handoff = runner.build_handoff_package(
            contract,
            runner.build_collect_execution_plan(contract),
            runner.build_verify_execution_plan(contract, items),
            runner.build_polish_execution_plan(contract),
            artifact_paths,
        )

        queue = runner.build_execute_queue(handoff)["queue"]
        verify_task = next(item for item in queue if item["phase"] == "verify")
        render_task = next(item for item in queue if item["phase"] == "render")

        self.assertIsInstance(verify_task["merge_command_argv"], list)
        self.assertEqual(
            verify_task["merge_command_hint"],
            shlex.join(verify_task["merge_command_argv"]),
        )
        self.assertIsInstance(render_task["command_argv"], list)
        self.assertIn("items with spaces.json", render_task["command_argv"])

    def test_invalid_contract_enums_are_rejected(self) -> None:
        args = argparse.Namespace(
            specialty="",
            depth=None,
            audience=None,
            specialty_keywords="",
            specialty_scope="",
            specialty_exclusions="",
            specialty_geography="",
            specialty_priority="",
            topic_mix="default",
            company_watchlist="",
            institution_watchlist="",
            community_watchlist="",
            time_window="someday",
            cadence="sometimes",
            mode=None,
            format="nonsense",
            source_roles="invalid-role",
        )

        with self.assertRaises(ValueError):
            runner.build_contract(args)

    def test_adapter_availability_requires_health_and_license(self) -> None:
        discovery = runner.discover_vendored_adapters()

        for skill in discovery["skills"]:
            self.assertIn("health_status", skill)
            self.assertIn("license_status", skill)
            if skill["name"] in discovery["available_adapters"]:
                self.assertEqual(skill["health_status"], "ready")
                self.assertEqual(skill["license_status"], "verified")

    def test_adapter_manifest_routes_only_healthy_licensed_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for name in ("ready", "unlicensed", "credentialed"):
                snapshot = root / name
                snapshot.mkdir()
                (snapshot / "entry.py").write_text("", encoding="utf-8")
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "skills": [
                            {
                                "name": "ready",
                                "snapshot_path": str(root / "ready"),
                                "entrypoints": ["entry.py"],
                                "license_status": "verified",
                            },
                            {
                                "name": "unlicensed",
                                "snapshot_path": str(root / "unlicensed"),
                                "entrypoints": ["entry.py"],
                                "license_status": "unresolved",
                            },
                            {
                                "name": "credentialed",
                                "snapshot_path": str(root / "credentialed"),
                                "entrypoints": ["entry.py"],
                                "credential_required": True,
                                "credential_env": "MNB_TEST_TOKEN",
                                "license_status": "verified",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.dict("os.environ", {}, clear=True):
                discovery = runner.discover_vendored_adapters(manifest_path)

            self.assertEqual(discovery["available_adapters"], ["ready"])

    def test_item_limit_must_be_positive(self) -> None:
        with self.assertRaisesRegex(ValueError, "item limit must be positive"):
            runner.choose_item_limit(runner.Contract(), -1)

    def test_acceptance_report_blocks_missing_evidence(self) -> None:
        report = runner.build_acceptance_report(
            runner.Contract(),
            [{"title": "A"}],
        )

        self.assertFalse(report["passed"])
        self.assertTrue(report["blocking_issues"])

    def test_cognitive_features_are_configurable_and_validated(self) -> None:
        parser = runner.build_parser()
        default_contract = runner.build_contract(parser.parse_args(["contract"]))
        off_contract = runner.build_contract(
            parser.parse_args(["contract", "--cognitive-features", "off"])
        )

        self.assertEqual(default_contract.cognitive_features, ["interrogate"])
        self.assertEqual(off_contract.cognitive_features, [])
        with self.assertRaisesRegex(ValueError, "invalid cognitive features"):
            runner.build_contract(
                parser.parse_args(["contract", "--cognitive-features", "interrogate,guess"])
            )

    def test_sprout_rendering_requires_basis_and_labels_inference(self) -> None:
        item = {
            "title": "Policy update",
            "what": "A regulator published a rule.",
            "why": "The rule changes procurement requirements.",
            "bucket": "政治与政策",
            "source_level": "首选证据",
            "evidence_status": "已确认",
            "sources": ["official rule", "direct report"],
            "insight_extensions": [
                {"insight": "Suppliers may adjust qualification plans", "basis": "new procurement threshold"},
                {"insight": "This incomplete extension must not render"},
            ],
        }

        output = runner.render_digest(
            runner.Contract(cognitive_features=["interrogate", "sprout"]),
            [item],
        )

        self.assertIn("认知延伸", output)
        self.assertIn("依据：new procurement threshold；性质：推断", output)
        self.assertNotIn("incomplete extension", output)

    def test_acceptance_blocks_unlabeled_visible_extension(self) -> None:
        item = {
            "title": "Policy update",
            "what": "A regulator published a rule.",
            "why": "The rule changes procurement requirements.",
            "bucket": "政治与政策",
            "source_level": "首选证据",
            "evidence_status": "已确认",
            "sources": ["official rule", "direct report"],
        }
        rendered = "来源：official rule\n\n认知延伸\n- Policy update：可能改变采购节奏\n"

        report = runner.build_acceptance_report(
            runner.Contract(cognitive_features=["sprout"]),
            [item],
            rendered,
        )

        self.assertFalse(report["passed"])
        self.assertIn("cognitive_extension_missing_inference_label", report["blocking_issues"])

    def test_off_disables_cognition_queue_stage(self) -> None:
        contract = runner.Contract(cognitive_features=[])
        handoff = runner.build_handoff_package(
            contract,
            runner.build_collect_execution_plan(contract),
            runner.build_verify_execution_plan(contract, []),
            runner.build_polish_execution_plan(contract),
            runner.build_artifact_paths(),
        )

        queue = runner.build_execute_queue(handoff)["queue"]
        phases = [item["phase"] for item in queue]
        acceptance = next(item for item in queue if item["phase"] == "acceptance")

        self.assertNotIn("cognition", phases)
        self.assertEqual(acceptance["consumes_artifact"], "draft_briefing")

    def test_interrogate_review_warns_on_single_source_high_impact_item(self) -> None:
        report = runner.build_acceptance_report(
            runner.Contract(cognitive_features=["interrogate"]),
            [
                {
                    "title": "Market event",
                    "what": "A company changed guidance.",
                    "why": "The change may affect pricing.",
                    "bucket": "商业与市场",
                    "source_level": "首选证据",
                    "evidence_status": "已确认",
                    "sources": ["company filing"],
                }
            ],
        )

        self.assertTrue(report["passed"])
        self.assertTrue(report["cognitive_review"]["enabled"])
        self.assertTrue(any(issue.startswith("single_source_high_impact:") for issue in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
