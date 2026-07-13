import argparse
import shlex
import unittest

from scripts import standalone_runner as runner


class RunnerHardeningTests(unittest.TestCase):
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
            ["collect", "normalize", "rank", "verify", "render", "acceptance", "polish"],
        )
        produced = {item.get("produces_artifact") for item in queue}
        consumed = {item.get("consumes_artifact") for item in queue}
        self.assertIn("candidate_pool", produced)
        self.assertIn("candidate_pool", consumed)
        self.assertIn("retained_items", produced)
        self.assertIn("retained_items", consumed)
        self.assertIn("final_briefing", produced)

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


if __name__ == "__main__":
    unittest.main()
