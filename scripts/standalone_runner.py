#!/usr/bin/env python3
"""Standalone helper for the more-news-briefing skill.

This runner keeps the core orchestration local to the skill:
- contract normalization
- query-pack generation
- template-based digest rendering
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


OPENING_LINE = "一次刷尽近期热点，高效工作一整天"
REPO_ROOT = Path(__file__).resolve().parent.parent
VENDOR_MANIFEST_PATH = REPO_ROOT / "references" / "skills" / "vendor-manifest.json"
DEFAULT_TIME_WINDOW = "last_7d"
DEFAULT_CADENCE = "one_off"
DEFAULT_DEPTH = "standard"
DEFAULT_FORMAT = "standard_digest"
DEFAULT_AUDIENCE = "research"
DEFAULT_MODE = "full"
DEFAULT_SOURCE_ROLES = ["discovery", "verification"]
SPECIALTY_SOURCE_ROLES = ["discovery", "verification", "context", "watch"]
DEFAULT_TOPICS = ["AI与科技", "政治与政策", "商业与市场", "文化与社会", "体育"]
DEFAULT_COUNT_TARGETS = {"quick": 5, "standard": 8, "analyst": 8}
VERIFICATION_RESULT_REQUIRED_FIELDS = ["title", "verdict"]
VERIFICATION_RESULT_OPTIONAL_FIELDS = [
    "claim",
    "why",
    "source_level",
    "evidence_status",
    "sources",
    "need_confirm",
    "follow_up",
]
FORMAT_ALIASES = {
    "quick_brief": "quick_brief",
    "short_brief": "quick_brief",
    "standard_digest": "standard_digest",
    "analyst_watch": "analyst_watch",
    "long_message": "long_message",
    "wechat_long": "long_message",
    "feishu_long": "long_message",
    "long_message_exec": "long_message_exec",
    "leader_brief": "long_message_exec",
}

QUERY_LIBRARY = {
    "AI与科技": {
        "core": [
            "AI latest news",
            "artificial intelligence major developments this week",
            "生成式AI 最新 动态",
        ],
        "news": [
            "AI funding launches regulation latest",
            "人工智能 政策 融资 发布 最新",
        ],
        "institutional": [
            "OpenAI Anthropic Google Meta Microsoft latest",
            "AI regulation White House EU China latest",
        ],
        "community": [
            "Hacker News AI open source this week",
            "GitHub release LLM agent RAG latest",
        ],
    },
    "政治与政策": {
        "core": [
            "global politics latest news",
            "official statements and policy changes this week major economies",
            "政治 政策 最新 动态",
        ],
        "news": [
            "US China EU official statement policy latest",
            "美国 中国 欧盟 官方声明 政策 最新",
        ],
        "institutional": [
            "official statement ministry white house european commission law latest",
            "国务院 部委 发布 法案 最新",
        ],
        "community": [],
    },
    "商业与市场": {
        "core": [
            "business news latest",
            "market-moving developments this week",
            "商业 市场 最新 动态",
        ],
        "news": [
            "earnings guidance layoff merger funding latest",
            "interest rates inflation jobs market latest",
        ],
        "institutional": [
            "Fed ECB PBOC latest",
            "美联储 欧洲央行 央行 最新",
        ],
        "community": [
            "market moving news flash latest",
        ],
    },
    "文化与社会": {
        "core": [
            "culture society latest news",
            "festival release platform controversy latest",
            "文化 社会 最新 动态",
        ],
        "news": [
            "festival release platform controversy survey",
            "education survey social cohesion latest",
        ],
        "institutional": [
            "UNESCO OECD society education report latest",
        ],
        "community": [],
    },
    "体育": {
        "core": [
            "sports latest news",
            "championship transfer injury roster final",
            "体育 最新 动态",
        ],
        "news": [
            "championship final roster injury latest",
            "tournament result official latest",
        ],
        "institutional": [
            "official tournament results latest",
        ],
        "community": [],
    },
}

DEFAULT_ANySEARCH_MAX_RESULTS = {
    "quick": 3,
    "standard": 5,
    "analyst": 6,
}


@dataclass
class Contract:
    time_window: str = DEFAULT_TIME_WINDOW
    cadence: str = DEFAULT_CADENCE
    topic_mix: list[str] = field(default_factory=lambda: DEFAULT_TOPICS.copy())
    depth: str = DEFAULT_DEPTH
    format: str = DEFAULT_FORMAT
    audience: str = DEFAULT_AUDIENCE
    mode: str = DEFAULT_MODE
    source_roles: list[str] = field(default_factory=lambda: DEFAULT_SOURCE_ROLES.copy())
    specialty: str = ""
    specialty_keywords: list[str] = field(default_factory=list)
    specialty_geography: str = ""
    specialty_priority: str = ""
    company_watchlist: list[str] = field(default_factory=list)
    institution_watchlist: list[str] = field(default_factory=list)
    community_watchlist: list[str] = field(default_factory=list)
    adapter_discovery: dict[str, Any] = field(default_factory=dict)
    inferred_assumptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "time_window": self.time_window,
            "cadence": self.cadence,
            "topic_mix": self.topic_mix,
            "depth": self.depth,
            "format": self.format,
            "audience": self.audience,
            "mode": self.mode,
            "source_roles": self.source_roles,
            "specialty": self.specialty,
            "specialty_keywords": self.specialty_keywords,
            "specialty_geography": self.specialty_geography,
            "specialty_priority": self.specialty_priority,
            "company_watchlist": self.company_watchlist,
            "institution_watchlist": self.institution_watchlist,
            "community_watchlist": self.community_watchlist,
            "adapter_discovery": self.adapter_discovery,
            "inferred_assumptions": self.inferred_assumptions,
        }


def load_vendor_manifest(path: Path = VENDOR_MANIFEST_PATH) -> dict[str, Any]:
    if not path.exists():
        return {
            "manifest_found": False,
            "manifest_path": str(path),
            "policy": {},
            "skills": [],
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("vendor-manifest.json must contain a JSON object")
    return {
        "manifest_found": True,
        "manifest_path": str(path),
        "policy": data.get("policy", {}),
        "skills": data.get("skills", []),
    }


def discover_vendored_adapters(path: Path = VENDOR_MANIFEST_PATH) -> dict[str, Any]:
    manifest = load_vendor_manifest(path)
    discovered: list[dict[str, Any]] = []
    for skill in manifest.get("skills", []):
        snapshot_rel = skill.get("snapshot_path", "")
        snapshot_abs = (REPO_ROOT / snapshot_rel).resolve() if snapshot_rel else None
        present = bool(snapshot_abs and snapshot_abs.exists())
        entry = {
            "name": skill.get("name", ""),
            "role": skill.get("role", ""),
            "bundled": bool(skill.get("bundled", False)),
            "required_by_default": bool(skill.get("required_by_default", False)),
            "snapshot_path": snapshot_rel,
            "snapshot_present": present,
            "snapshot_abspath": str(snapshot_abs) if snapshot_abs else "",
            "license_note": skill.get("license_note", ""),
            "update_policy": skill.get("update_policy", ""),
        }
        discovered.append(entry)
    available = [entry["name"] for entry in discovered if entry["snapshot_present"]]
    return {
        "manifest_found": manifest["manifest_found"],
        "manifest_path": manifest["manifest_path"],
        "policy": manifest.get("policy", {}),
        "available_count": len(available),
        "available_adapters": available,
        "skills": discovered,
    }


def split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def normalize_topic_mix(topic_mix: str, specialty: str) -> list[str]:
    if not topic_mix or topic_mix == "default":
        topics = DEFAULT_TOPICS.copy()
    else:
        topics = [part.strip() for part in topic_mix.split(",") if part.strip()]
    if specialty and "专项关注" not in topics:
        topics.append("专项关注")
    return topics


def normalize_format(raw_format: str | None, depth: str, audience: str) -> str:
    if raw_format:
        return FORMAT_ALIASES.get(raw_format, raw_format)
    if audience == "executive":
        return "long_message_exec"
    if depth == "quick":
        return "quick_brief"
    if depth == "analyst":
        return "analyst_watch"
    return DEFAULT_FORMAT


def infer_source_roles(specialty: str, explicit_roles: list[str]) -> list[str]:
    if explicit_roles:
        return explicit_roles
    if specialty:
        return SPECIALTY_SOURCE_ROLES.copy()
    return DEFAULT_SOURCE_ROLES.copy()


def build_contract(args: argparse.Namespace) -> Contract:
    specialty = args.specialty or ""
    depth = args.depth or DEFAULT_DEPTH
    audience = args.audience or DEFAULT_AUDIENCE
    contract = Contract()
    contract.specialty = specialty
    contract.specialty_keywords = split_csv(args.specialty_keywords) or split_csv(specialty.replace("/", ","))
    contract.specialty_geography = args.specialty_geography or ""
    contract.specialty_priority = args.specialty_priority or ""
    contract.topic_mix = normalize_topic_mix(args.topic_mix, specialty)
    contract.company_watchlist = split_csv(args.company_watchlist)
    contract.institution_watchlist = split_csv(args.institution_watchlist)
    contract.community_watchlist = split_csv(args.community_watchlist)
    contract.adapter_discovery = discover_vendored_adapters()

    if args.time_window:
        contract.time_window = args.time_window
    else:
        contract.inferred_assumptions.append(f"time_window={DEFAULT_TIME_WINDOW}")

    if args.cadence:
        contract.cadence = args.cadence
    else:
        contract.inferred_assumptions.append(f"cadence={DEFAULT_CADENCE}")

    contract.depth = depth
    if not args.depth:
        contract.inferred_assumptions.append(f"depth={DEFAULT_DEPTH}")

    contract.audience = audience
    if not args.audience:
        contract.inferred_assumptions.append(f"audience={DEFAULT_AUDIENCE}")

    contract.mode = args.mode or DEFAULT_MODE
    if not args.mode:
        contract.inferred_assumptions.append(f"mode={DEFAULT_MODE}")

    contract.format = normalize_format(args.format, contract.depth, contract.audience)
    if not args.format:
        contract.inferred_assumptions.append(f"format={contract.format}")

    contract.source_roles = infer_source_roles(specialty, split_csv(args.source_roles))
    if not args.source_roles:
        contract.inferred_assumptions.append(
            "source_roles=" + "+".join(contract.source_roles)
        )
    return contract


def cmd_contract(args: argparse.Namespace) -> int:
    print(json.dumps(build_contract(args).to_dict(), ensure_ascii=False, indent=2))
    return 0


def build_specialty_queries(contract: Contract) -> dict[str, list[str]]:
    base_terms = contract.specialty_keywords or [contract.specialty]
    geography = contract.specialty_geography.strip()
    priority = contract.specialty_priority.strip()
    core = " ".join(base_terms[:4]).strip()
    news_parts = [core, "latest developments last 7 days"]
    institutional_seed = "policy official statement"
    if priority.lower() == "policy":
        institutional_seed = "official statement"
    institutional_parts = [core, institutional_seed]
    if priority and priority.lower() != "policy":
        institutional_parts.append(priority)
    if geography:
        news_parts.append(geography)
        institutional_parts.append(geography)
    news = " ".join(part for part in news_parts if part).strip()
    institutional = " ".join(part for part in institutional_parts if part).strip()
    community = f"{core} repo forum community latest".strip()
    return {
        "core": [core] if core else [],
        "news": [news] if news else [],
        "institutional": [institutional] if institutional else [],
        "community": [community] if community else [],
    }


def build_queries(contract: Contract, grouped: bool = True) -> dict[str, Any]:
    queries: dict[str, Any] = {}
    for topic in contract.topic_mix:
        if topic == "专项关注":
            groups = build_specialty_queries(contract)
        else:
            groups = QUERY_LIBRARY.get(topic, {"core": [topic], "news": [], "institutional": [], "community": []})
        if grouped:
            queries[topic] = groups
        else:
            flattened: list[str] = []
            for group_name in ("core", "news", "institutional", "community"):
                flattened.extend(groups.get(group_name, []))
            queries[topic] = flattened
    return queries


def has_adapter(contract: Contract, name: str) -> bool:
    return name in contract.adapter_discovery.get("available_adapters", [])


def build_route_recommendation(contract: Contract) -> dict[str, Any]:
    topic_count = len(contract.topic_mix)
    specialty_present = "专项关注" in contract.topic_mix and bool(contract.specialty)
    high_coverage = topic_count >= 4
    medium_coverage = topic_count >= 3
    needs_deep_verify = (
        contract.depth == "analyst"
        or "watch" in contract.source_roles
        or contract.specialty_priority in {"policy", "safety", "standards", "financing"}
    )
    long_message_output = contract.format in {"long_message", "long_message_exec"} or contract.audience == "executive"

    anysearch_available = has_adapter(contract, "anysearch")
    deep_research_available = has_adapter(contract, "deep-research")
    humanizer_available = has_adapter(contract, "humanizer-zh")

    collect_route = "native_web"
    collect_reason = "默认使用内置 open web 路线。"
    if anysearch_available and high_coverage:
        collect_route = "vendored_anysearch"
        collect_reason = "多主题广覆盖且已发现 anysearch，优先用它做第一轮 recall 扩展。"
    elif anysearch_available and (medium_coverage or specialty_present) and contract.mode == "full":
        collect_route = "vendored_anysearch"
        collect_reason = "当前主题数不低或含专项关注，已发现 anysearch，可用它加快候选池铺开。"

    verify_route = "built_in_verification"
    verify_reason = "默认使用内置证据分级与交叉核验规则。"
    if deep_research_available and needs_deep_verify:
        verify_route = "vendored_deep_research"
        verify_reason = "当前合同更偏高影响/深核验，已发现 deep-research，建议用于 retained items 的二次核验。"

    polish_route = "built_in_polish"
    polish_reason = "默认使用内置模板成稿。"
    if humanizer_available and long_message_output and contract.mode == "full":
        polish_route = "vendored_humanizer_zh"
        polish_reason = "当前输出偏中文长消息，已发现 humanizer-zh，可用于最后一轮压缩和去 AI 味。"

    route_steps = [
        {
            "step": 1,
            "name": "collect",
            "recommended_adapter": collect_route,
            "reason": collect_reason,
        },
        {
            "step": 2,
            "name": "verify",
            "recommended_adapter": verify_route,
            "reason": verify_reason,
        },
        {
            "step": 3,
            "name": "polish",
            "recommended_adapter": polish_route,
            "reason": polish_reason,
        },
    ]

    fallbacks = {
        "collect": "native_web",
        "verify": "built_in_verification",
        "polish": "built_in_polish",
    }
    return {
        "contract_shape": {
            "topic_count": topic_count,
            "specialty_present": specialty_present,
            "depth": contract.depth,
            "format": contract.format,
            "audience": contract.audience,
            "mode": contract.mode,
        },
        "available_adapters": contract.adapter_discovery.get("available_adapters", []),
        "route_steps": route_steps,
        "fallbacks": fallbacks,
        "notes": [
            "collect 阶段只借用 recall，不外包最终排序。",
            "verify 阶段优先用于高影响、政策、市场和专项条目。",
            "polish 阶段是可选增强，不能覆盖事实与证据判断。",
        ],
    }


def map_time_window_to_freshness(time_window: str) -> str:
    mapping = {
        "today": "day",
        "last_24h": "day",
        "last_3d": "week",
        "last_7d": "week",
    }
    return mapping.get(time_window, "week")


def choose_collect_query(groups: dict[str, list[str]]) -> str:
    for key in ("news", "core", "institutional", "community"):
        values = groups.get(key, [])
        if values:
            return values[0]
    return ""


def build_anysearch_batches(contract: Contract) -> list[dict[str, Any]]:
    grouped_queries = build_queries(contract, grouped=True)
    batch_topics = [
        ("Batch A", ["AI与科技", "政治与政策", "商业与市场"]),
        ("Batch B", ["文化与社会", "体育", "专项关注"]),
    ]
    freshness = map_time_window_to_freshness(contract.time_window)
    max_results = DEFAULT_ANySEARCH_MAX_RESULTS.get(contract.depth, 5)
    batches: list[dict[str, Any]] = []
    anysearch_script = REPO_ROOT / "references" / "skills" / "anysearch" / "scripts" / "anysearch_cli.py"

    for batch_name, topics in batch_topics:
        query_objects: list[dict[str, Any]] = []
        for topic in topics:
            groups = grouped_queries.get(topic)
            if not groups:
                continue
            query = choose_collect_query(groups)
            if not query:
                continue
            query_objects.append(
                {
                    "topic": topic,
                    "query": query,
                    "content_types": "news",
                    "freshness": freshness,
                    "max_results": max_results,
                }
            )
        if not query_objects:
            continue
        compact_payload = [
            {
                "query": item["query"],
                "content_types": item["content_types"],
                "freshness": item["freshness"],
                "max_results": item["max_results"],
            }
            for item in query_objects
        ]
        batches.append(
            {
                "batch_name": batch_name,
                "topics": [item["topic"] for item in query_objects],
                "query_objects": query_objects,
                "payload": compact_payload,
                "command_hint": (
                    f"python3 {anysearch_script} batch_search --queries "
                    f"'{json.dumps(compact_payload, ensure_ascii=False)}'"
                ),
            }
        )
    return batches


def build_collect_execution_plan(contract: Contract) -> dict[str, Any]:
    route = build_route_recommendation(contract)
    collect_step = next(step for step in route["route_steps"] if step["name"] == "collect")
    grouped_queries = build_queries(contract, grouped=True)
    plan = {
        "recommended_adapter": collect_step["recommended_adapter"],
        "reason": collect_step["reason"],
        "freshness": map_time_window_to_freshness(contract.time_window),
        "grouped_queries": grouped_queries,
        "fallback_web_queries": {
            topic: choose_collect_query(groups) for topic, groups in grouped_queries.items()
        },
    }
    if collect_step["recommended_adapter"] == "vendored_anysearch":
        plan["execution_mode"] = "anysearch_batch_search"
        plan["anysearch_batches"] = build_anysearch_batches(contract)
    else:
        plan["execution_mode"] = "native_web_search"
        plan["anysearch_batches"] = []
    return plan


def choose_verify_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prioritized: list[dict[str, Any]] = []
    for item in items:
        normalized = normalize_item(item)
        if normalized["source_level"] != "首选证据" or normalized["evidence_status"] != "已确认":
            prioritized.append(normalized)
            continue
        if normalized["bucket"] in {"政治与政策", "商业与市场", "专项关注"}:
            prioritized.append(normalized)
    return prioritized


def build_deep_research_verify_tasks(contract: Contract, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deep_research_skill = REPO_ROOT / "references" / "skills" / "deep-research"
    tasks: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        verification_questions = [
            f"核验事件是否准确：{item['title']}",
            f"核对关键事实、时间、数字与主体：{item['what']}",
            f"评估为什么重要这条判断是否被现有证据支持：{item['why']}",
        ]
        if item["bucket"] in {"政治与政策", "商业与市场", "专项关注"}:
            verification_questions.append("优先检查是否存在官方、监管、公司公告或一手文件。")
        tasks.append(
            {
                "task_id": f"verify-{idx}",
                "title": item["title"],
                "bucket": item["bucket"],
                "recommended_mode": "fact-check",
                "recommended_skill_path": str(deep_research_skill),
                "input_brief": {
                    "claim": item["what"],
                    "importance_judgment": item["why"],
                    "current_source_level": item["source_level"],
                    "current_evidence_status": item["evidence_status"],
                    "known_sources": item.get("sources", []),
                },
                "verification_questions": verification_questions,
                "success_criteria": [
                    "确认关键事实与时间线是否一致",
                    "找到至少一个更强来源或明确说明为什么做不到",
                    "给出保留、降级或移入继续跟踪的判断",
                ],
                "command_prompt": (
                    f"Use vendored deep-research in fact-check mode to verify this news item: "
                    f"title={item['title']}; claim={item['what']}; why_it_matters={item['why']}."
                ),
            }
        )
    return tasks


def build_builtin_verify_checks(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        checks.append(
            {
                "task_id": f"builtin-verify-{idx}",
                "title": item["title"],
                "checks": [
                    "交叉核对事件时间、地点、主体与数字",
                    "确认是否已有首选证据",
                    "若仍是次选证据或待确认，移入继续跟踪",
                ],
            }
        )
    return checks


def make_result_stub_path(output_file: str, title: str) -> str:
    if not output_file:
        return ""
    output_path = Path(output_file)
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", title).strip("-").lower() or "result"
    suffix = "".join(output_path.suffixes) or ".json"
    base_name = output_path.name[: -len(suffix)] if suffix else output_path.name
    return str(output_path.with_name(f"{base_name}.{slug}.json"))


def build_verification_result_contract() -> dict[str, Any]:
    return {
        "version": 1,
        "required_fields": VERIFICATION_RESULT_REQUIRED_FIELDS,
        "optional_fields": VERIFICATION_RESULT_OPTIONAL_FIELDS,
        "verdicts": {
            "keep": "保留在主简报，并可用更强证据字段覆盖原字段。",
            "confirm": "等同 keep，用于已核实通过的条目。",
            "downgrade": "保留条目，但下调证据展示等级。",
            "watch": "移入继续跟踪，不进入主简报。",
            "move_to_watch": "等同 watch。",
            "continue_tracking": "等同 watch。",
        },
    }


def build_verification_result_template(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": item["title"],
        "verdict": "",
        "claim": item["what"],
        "why": item["why"],
        "source_level": item["source_level"],
        "evidence_status": item["evidence_status"],
        "sources": item.get("sources", []),
        "need_confirm": item.get("need_confirm", ""),
        "follow_up": item.get("follow_up", ""),
    }


def build_verification_result_templates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [build_verification_result_template(item) for item in items]


def build_builtin_verification_tasks(
    items: list[dict[str, Any]],
    verification_results_file: str = "",
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        result_stub_file = make_result_stub_path(verification_results_file, item["title"])
        tasks.append(
            {
                "task_id": f"builtin-verify-{idx}",
                "title": item["title"],
                "checks": [
                    "交叉核对事件时间、地点、主体与数字",
                    "确认是否已有首选证据",
                    "若仍是次选证据或待确认，移入继续跟踪",
                ],
                "result_template": build_verification_result_template(item),
                "judgment_options": ["keep", "confirm", "downgrade", "watch"],
                "result_stub_file": result_stub_file,
            }
        )
    return tasks


def build_verify_execution_plan(contract: Contract, items: list[dict[str, Any]]) -> dict[str, Any]:
    route = build_route_recommendation(contract)
    verify_step = next(step for step in route["route_steps"] if step["name"] == "verify")
    main_items, _follow_ups = split_items(items)
    verify_items = choose_verify_items(main_items)
    plan = {
        "recommended_adapter": verify_step["recommended_adapter"],
        "reason": verify_step["reason"],
        "verify_candidate_count": len(verify_items),
        "verify_candidates": [item["title"] for item in verify_items],
        "verification_result_contract": build_verification_result_contract(),
        "verification_result_templates": build_verification_result_templates(verify_items),
        "builtin_checks": build_builtin_verify_checks(verify_items),
        "builtin_verification_tasks": build_builtin_verification_tasks(verify_items),
    }
    if verify_step["recommended_adapter"] == "vendored_deep_research":
        plan["execution_mode"] = "deep_research_fact_check_tasks"
        plan["deep_research_tasks"] = build_deep_research_verify_tasks(contract, verify_items)
    else:
        plan["execution_mode"] = "built_in_verification"
        plan["deep_research_tasks"] = []
    return plan


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_polish_goals(contract: Contract) -> list[str]:
    goals = [
        "删除填充开场和过强的连接词",
        "保持事实与证据字段不被改写出新含义",
        "压缩 AI 味明显的套话与总结腔",
    ]
    if contract.format in {"long_message", "long_message_exec"}:
        goals.extend(
            [
                "保持长消息信息密度高，避免空泛转场",
                "让标题、概览、重点新闻之间的节奏更自然",
            ]
        )
    if contract.audience == "executive":
        goals.append("优先保留判断句，减少背景铺垫。")
    return goals


def build_builtin_polish_checks(contract: Contract) -> list[str]:
    checks = [
        "检查标题是否事实化，避免 clickbait",
        "检查为什么重要是否短于发生了什么",
        "检查来源级别、证据状态、来源字段顺序是否一致",
        "检查是否删除了空节和占位文字",
    ]
    if contract.format in {"long_message", "long_message_exec"}:
        checks.extend(
            [
                "检查分主题速览是否比重点新闻更紧凑",
                "检查结尾停在继续跟踪，不加礼貌性尾巴",
            ]
        )
    return checks


def build_polish_execution_plan(
    contract: Contract,
    items: list[dict[str, Any]] | None = None,
    draft_file: Path | None = None,
) -> dict[str, Any]:
    route = build_route_recommendation(contract)
    polish_step = next(step for step in route["route_steps"] if step["name"] == "polish")
    draft_preview = ""
    if draft_file and draft_file.exists():
        draft_preview = load_text(draft_file)[:500]
    item_titles = [normalize_item(item)["title"] for item in items] if items else []
    plan = {
        "recommended_adapter": polish_step["recommended_adapter"],
        "reason": polish_step["reason"],
        "draft_file": str(draft_file) if draft_file else "",
        "draft_preview": draft_preview,
        "item_titles": item_titles,
    }
    if polish_step["recommended_adapter"] == "vendored_humanizer_zh":
        humanizer_skill = REPO_ROOT / "references" / "skills" / "humanizer-zh"
        plan["execution_mode"] = "humanizer_zh_edit_task"
        plan["humanizer_task"] = {
            "recommended_skill_path": str(humanizer_skill),
            "editing_goals": build_polish_goals(contract),
            "protected_invariants": [
                "不新增未核验事实",
                "不改写来源级别、证据状态和来源含义",
                "不删除继续跟踪中仍需保留的观察点",
            ],
            "command_prompt": (
                "Use vendored humanizer-zh to revise the Chinese briefing draft so it reads more naturally "
                "while preserving facts, evidence labels, and source lines."
            ),
        }
        plan["builtin_checks"] = []
    else:
        plan["execution_mode"] = "built_in_polish"
        plan["humanizer_task"] = {}
        plan["builtin_checks"] = build_builtin_polish_checks(contract)
    return plan


def build_artifact_paths(
    items_file: Path | None = None,
    draft_file: Path | None = None,
) -> dict[str, str]:
    verification_results_file = ""
    digest_input_items_file = str(items_file) if items_file else ""
    base_name = ""
    if items_file:
        suffix = "".join(items_file.suffixes) or ".json"
        base_name = items_file.name[: -len(suffix)] if suffix else items_file.name
        verification_results_file = str(
            items_file.with_name(f"{base_name}.verification-results.json")
        )

    digest_output_file = ""
    if draft_file:
        digest_output_file = str(draft_file)
    elif items_file:
        digest_output_file = str(items_file.with_name(f"{base_name}.digest.txt"))

    return {
        "items_file": digest_input_items_file,
        "verification_results_file": verification_results_file,
        "digest_output_file": digest_output_file,
    }


def build_handoff_package(
    contract: Contract,
    collect_plan: dict[str, Any],
    verify_plan: dict[str, Any] | None = None,
    polish_plan: dict[str, Any] | None = None,
    artifact_paths: dict[str, str] | None = None,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    artifact_paths = artifact_paths or build_artifact_paths()

    if collect_plan:
        if collect_plan.get("execution_mode") == "anysearch_batch_search":
            steps.append(
                {
                    "step": "collect",
                    "status": "ready",
                    "adapter": collect_plan.get("recommended_adapter"),
                    "execution_mode": collect_plan.get("execution_mode"),
                    "primary_inputs": {
                        "freshness": collect_plan.get("freshness"),
                        "batch_count": len(collect_plan.get("anysearch_batches", [])),
                    },
                    "artifacts": collect_plan.get("anysearch_batches", []),
                    "fallback": {
                        "execution_mode": "native_web_search",
                        "queries": collect_plan.get("fallback_web_queries", {}),
                    },
                }
            )
        else:
            steps.append(
                {
                    "step": "collect",
                    "status": "ready",
                    "adapter": collect_plan.get("recommended_adapter"),
                    "execution_mode": collect_plan.get("execution_mode"),
                    "primary_inputs": {
                        "queries": collect_plan.get("fallback_web_queries", {}),
                    },
                    "artifacts": [],
                    "fallback": {},
                }
            )

    if verify_plan:
        if verify_plan.get("execution_mode") == "deep_research_fact_check_tasks":
            steps.append(
                {
                    "step": "verify",
                    "status": "ready",
                    "adapter": verify_plan.get("recommended_adapter"),
                    "execution_mode": verify_plan.get("execution_mode"),
                    "primary_inputs": {
                        "verify_candidate_count": verify_plan.get("verify_candidate_count", 0),
                        "verify_candidates": verify_plan.get("verify_candidates", []),
                        "verification_results_file": artifact_paths.get("verification_results_file", ""),
                    },
                    "artifacts": verify_plan.get("deep_research_tasks", []),
                    "fallback": {
                        "execution_mode": "built_in_verification",
                        "checks": verify_plan.get("builtin_checks", []),
                    },
                }
            )
        else:
            steps.append(
                {
                    "step": "verify",
                    "status": "ready",
                    "adapter": verify_plan.get("recommended_adapter"),
                    "execution_mode": verify_plan.get("execution_mode"),
                    "primary_inputs": {
                        "verify_candidate_count": verify_plan.get("verify_candidate_count", 0),
                        "verify_candidates": verify_plan.get("verify_candidates", []),
                        "verification_results_file": artifact_paths.get("verification_results_file", ""),
                    },
                    "artifacts": verify_plan.get("builtin_verification_tasks", []),
                    "fallback": {},
                }
            )

    if polish_plan:
        if polish_plan.get("execution_mode") == "humanizer_zh_edit_task":
            steps.append(
                {
                    "step": "polish",
                    "status": "ready",
                    "adapter": polish_plan.get("recommended_adapter"),
                    "execution_mode": polish_plan.get("execution_mode"),
                    "primary_inputs": {
                        "draft_file": polish_plan.get("draft_file", ""),
                        "item_titles": polish_plan.get("item_titles", []),
                    },
                    "artifacts": [polish_plan.get("humanizer_task", {})],
                    "fallback": {
                        "execution_mode": "built_in_polish",
                        "checks": polish_plan.get("builtin_checks", []),
                    },
                }
            )
        else:
            steps.append(
                {
                    "step": "polish",
                    "status": "ready",
                    "adapter": polish_plan.get("recommended_adapter"),
                    "execution_mode": polish_plan.get("execution_mode"),
                    "primary_inputs": {
                        "draft_file": polish_plan.get("draft_file", ""),
                        "item_titles": polish_plan.get("item_titles", []),
                    },
                    "artifacts": polish_plan.get("builtin_checks", []),
                    "fallback": {},
                }
            )

    return {
        "version": 1,
        "contract_summary": {
            "time_window": contract.time_window,
            "topic_mix": contract.topic_mix,
            "depth": contract.depth,
            "format": contract.format,
            "audience": contract.audience,
            "mode": contract.mode,
        },
        "adapter_inventory": contract.adapter_discovery.get("available_adapters", []),
        "artifact_paths": artifact_paths,
        "steps": steps,
    }


def build_execute_queue(handoff_package: dict[str, Any]) -> dict[str, Any]:
    queue: list[dict[str, Any]] = []
    ordinal = 1
    artifact_paths = handoff_package.get("artifact_paths", {})
    runner_path = Path(__file__).resolve()
    for step in handoff_package.get("steps", []):
        execution_mode = step.get("execution_mode", "")
        if execution_mode == "anysearch_batch_search":
            for batch in step.get("artifacts", []):
                queue.append(
                    {
                        "order": ordinal,
                        "phase": step["step"],
                        "executor": step.get("adapter"),
                        "action": "run_batch_search",
                        "target": batch.get("batch_name", ""),
                        "command": batch.get("command_hint", ""),
                        "payload": batch.get("payload", []),
                        "requires_network": True,
                        "consumes_artifact": "query_pack",
                        "produces_artifact": "candidate_pool",
                        "success_signal": "batch_search returns result set for every query object",
                    }
                )
                ordinal += 1
        elif execution_mode == "native_web_search":
            queue.append(
                {
                    "order": ordinal,
                    "phase": step["step"],
                        "executor": step.get("adapter"),
                        "action": "run_native_web_queries",
                        "target": step["step"],
                        "command": "",
                        "payload": step.get("primary_inputs", {}).get("queries", {}),
                        "requires_network": True,
                        "consumes_artifact": "query_pack",
                        "produces_artifact": "candidate_pool",
                        "success_signal": "top queries return enough candidate headlines to move into ranking",
                    }
                )
            ordinal += 1
        elif execution_mode == "deep_research_fact_check_tasks":
            for task in step.get("artifacts", []):
                result_stub_file = make_result_stub_path(
                    step.get("primary_inputs", {}).get("verification_results_file", ""),
                    task.get("title", ""),
                )
                queue.append(
                    {
                        "order": ordinal,
                        "phase": step["step"],
                        "executor": step.get("adapter"),
                        "action": "run_fact_check_task",
                        "target": task.get("title", ""),
                        "command": task.get("command_prompt", ""),
                        "payload": task,
                        "requires_network": True,
                        "consumes_artifact": "retained_item",
                        "produces_artifact": "verification_result",
                        "output_file": step.get("primary_inputs", {}).get("verification_results_file", ""),
                        "result_stub_file": result_stub_file,
                        "success_signal": "task returns keep/downgrade/watch judgment with stronger evidence",
                        "next_action_summary": "append normalized verification result into the shared verification-results file",
                        "merge_command_hint": (
                            f"python3 {runner_path} verify-results "
                            f"--items-file {artifact_paths.get('items_file', '')} "
                            f"--results-file {result_stub_file} "
                            f"--output-file {step.get('primary_inputs', {}).get('verification_results_file', '')} "
                            f"--merge"
                            if artifact_paths.get("items_file") and result_stub_file
                            else ""
                        ),
                    }
                )
                ordinal += 1
        elif execution_mode == "built_in_verification":
            queue.append(
                {
                    "order": ordinal,
                    "phase": step["step"],
                        "executor": step.get("adapter"),
                        "action": "run_builtin_checks",
                        "target": step["step"],
                        "command": "",
                        "payload": step.get("artifacts", []),
                        "requires_network": False,
                        "consumes_artifact": "retained_item",
                        "produces_artifact": "verification_results_file",
                        "output_file": step.get("primary_inputs", {}).get("verification_results_file", ""),
                        "success_signal": "each candidate is normalized into keep/downgrade/watch style verification results",
                        "next_action_summary": "write the built-in verification judgments into the shared verification-results file",
                        "merge_command_hint": (
                            f"python3 {runner_path} verify-results "
                            f"--items-file {artifact_paths.get('items_file', '')} "
                            f"--results-file <built-in-results.json> "
                            f"--output-file {step.get('primary_inputs', {}).get('verification_results_file', '')} "
                            f"--merge"
                            if artifact_paths.get("items_file")
                            else ""
                        ),
                    }
                )
            ordinal += 1
        elif execution_mode == "humanizer_zh_edit_task":
            artifact = step.get("artifacts", [{}])[0]
            queue.append(
                {
                    "order": ordinal,
                    "phase": step["step"],
                        "executor": step.get("adapter"),
                        "action": "run_humanizer_edit",
                        "target": step.get("primary_inputs", {}).get("draft_file", ""),
                        "command": artifact.get("command_prompt", ""),
                        "payload": artifact,
                        "requires_network": False,
                        "consumes_artifact": "draft_briefing",
                        "produces_artifact": "polished_briefing",
                        "success_signal": "draft reads more naturally without changing facts or evidence labels",
                    }
                )
            ordinal += 1
        elif execution_mode == "built_in_polish":
            queue.append(
                {
                    "order": ordinal,
                    "phase": step["step"],
                        "executor": step.get("adapter"),
                        "action": "run_builtin_polish_checks",
                        "target": step.get("primary_inputs", {}).get("draft_file", "") or step["step"],
                        "command": "",
                        "payload": step.get("artifacts", []),
                        "requires_network": False,
                        "consumes_artifact": "draft_briefing",
                        "produces_artifact": "polish_checklist_result",
                        "success_signal": "draft passes structure and wording checks",
                    }
                )
            ordinal += 1
    next_action_summary = queue[0] if queue else {}
    return {
        "version": 1,
        "queue_length": len(queue),
        "artifact_paths": artifact_paths,
        "queue": queue,
        "next_action_summary": next_action_summary,
    }


def cmd_queries(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    payload = {
        "adapter_discovery": contract.adapter_discovery,
        "route_recommendation": build_route_recommendation(contract),
        "queries": build_queries(contract, grouped=not args.flat),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_adapters(args: argparse.Namespace) -> int:
    discovery = discover_vendored_adapters()
    if args.available_only:
        discovery = {
            **discovery,
            "skills": [skill for skill in discovery["skills"] if skill["snapshot_present"]],
        }
    print(json.dumps(discovery, ensure_ascii=False, indent=2))
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    payload = {
        "adapter_discovery": contract.adapter_discovery,
        "route_recommendation": build_route_recommendation(contract),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    payload = {
        "adapter_discovery": contract.adapter_discovery,
        "route_recommendation": build_route_recommendation(contract),
        "collect_execution_plan": build_collect_execution_plan(contract),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items = load_items(Path(args.items_file))
    payload = {
        "adapter_discovery": contract.adapter_discovery,
        "route_recommendation": build_route_recommendation(contract),
        "verify_execution_plan": build_verify_execution_plan(contract, items),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_polish(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items = load_items(Path(args.items_file)) if args.items_file else None
    draft_file = Path(args.draft_file) if args.draft_file else None
    payload = {
        "adapter_discovery": contract.adapter_discovery,
        "route_recommendation": build_route_recommendation(contract),
        "polish_execution_plan": build_polish_execution_plan(contract, items, draft_file),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items = load_items(Path(args.items_file)) if args.items_file else None
    draft_file = Path(args.draft_file) if args.draft_file else None
    artifact_paths = build_artifact_paths(Path(args.items_file) if args.items_file else None, draft_file)
    route = build_route_recommendation(contract)
    collect_plan = build_collect_execution_plan(contract)
    verify_plan = build_verify_execution_plan(contract, items) if items else {}
    polish_plan = build_polish_execution_plan(contract, items, draft_file)
    payload = {
        "contract": contract.to_dict(),
        "route_recommendation": route,
        "collect_execution_plan": collect_plan,
        "verify_execution_plan": verify_plan,
        "polish_execution_plan": polish_plan,
        "artifact_paths": artifact_paths,
        "handoff_package": build_handoff_package(contract, collect_plan, verify_plan, polish_plan, artifact_paths),
    }
    payload["execute_queue"] = build_execute_queue(payload["handoff_package"])
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_execute(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items = load_items(Path(args.items_file)) if args.items_file else None
    draft_file = Path(args.draft_file) if args.draft_file else None
    artifact_paths = build_artifact_paths(Path(args.items_file) if args.items_file else None, draft_file)
    collect_plan = build_collect_execution_plan(contract)
    verify_plan = build_verify_execution_plan(contract, items) if items else {}
    polish_plan = build_polish_execution_plan(contract, items, draft_file)
    handoff = build_handoff_package(contract, collect_plan, verify_plan, polish_plan, artifact_paths)
    payload = {
        "contract_summary": {
            "topic_mix": contract.topic_mix,
            "depth": contract.depth,
            "format": contract.format,
            "audience": contract.audience,
        },
        "artifact_paths": artifact_paths,
        "handoff_package": handoff,
        "execute_queue": build_execute_queue(handoff),
        "verification_results_init_command_hint": (
            f"python3 {Path(__file__).resolve()} verify-results --items-file {artifact_paths['items_file']} "
            f"--output-file {artifact_paths['verification_results_file']}"
            if artifact_paths["items_file"] and artifact_paths["verification_results_file"]
            else ""
        ),
        "digest_command_hint": (
            f"python3 {Path(__file__).resolve()} digest --items-file {artifact_paths['items_file']} "
            f"--verification-results-file {artifact_paths['verification_results_file']}"
            if artifact_paths["items_file"] and artifact_paths["verification_results_file"]
            else ""
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def load_items(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("items file must contain a JSON array")
    return data


def load_verification_results(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if isinstance(data.get("results"), list):
            return data["results"]
        if isinstance(data.get("verification_results"), list):
            return data["verification_results"]
        raise ValueError(
            "verification results object must contain a results or verification_results array"
        )
    if isinstance(data, list):
        return data
    raise ValueError(
        "verification results must be a JSON array or object with results or verification_results"
    )


def normalize_verification_result(result: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "title": str(result.get("title", "")).strip(),
        "verdict": str(result.get("verdict", "")).strip().lower(),
    }
    for field in VERIFICATION_RESULT_OPTIONAL_FIELDS:
        value = result.get(field)
        if value not in (None, "", []):
            normalized[field] = value
    return normalized


def merge_verification_results(
    existing_results: list[dict[str, Any]],
    incoming_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged_by_title = {
        result["title"]: normalize_verification_result(result)
        for result in existing_results
        if normalize_verification_result(result)["title"]
    }
    for result in incoming_results:
        normalized = normalize_verification_result(result)
        if not normalized["title"]:
            continue
        merged_by_title[normalized["title"]] = normalized
    return list(merged_by_title.values())


def build_verification_result_package(
    items: list[dict[str, Any]],
    raw_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    main_items, _follow_ups = split_items(items)
    verify_items = choose_verify_items(main_items)
    contract = build_verification_result_contract()
    templates = build_verification_result_templates(verify_items)
    normalized_results: list[dict[str, Any]] = []
    if raw_results:
        allowed_titles = {item["title"] for item in verify_items}
        for raw in raw_results:
            normalized = normalize_verification_result(raw)
            if not normalized["title"] or normalized["title"] not in allowed_titles:
                continue
            normalized_results.append(normalized)
    return {
        "version": 1,
        "result_contract": contract,
        "result_templates": templates,
        "results": normalized_results,
        "verification_results": normalized_results,
        "digest_overlay_ready_results": normalized_results,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_sources(sources: Any) -> str:
    if isinstance(sources, list):
        return "、".join(str(item) for item in sources)
    return str(sources or "")


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(item)
    normalized.setdefault("title", "未命名条目")
    normalized.setdefault("what", "待补充")
    normalized.setdefault("why", "待补充")
    normalized.setdefault("bucket", "未分类")
    normalized.setdefault("source_level", "次选证据")
    normalized.setdefault("evidence_status", "交叉验证中")
    normalized.setdefault("sources", [])
    return normalized


def apply_verification_results(
    items: list[dict[str, Any]],
    verification_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_title = {
        str(result.get("title", "")).strip(): result
        for result in verification_results
        if str(result.get("title", "")).strip()
    }
    updated_items: list[dict[str, Any]] = []
    for item in items:
        normalized = normalize_item(item)
        result = by_title.get(normalized["title"])
        if not result:
            updated_items.append(normalized)
            continue

        merged = dict(normalized)
        if result.get("claim"):
            merged["what"] = result["claim"]
        if result.get("why"):
            merged["why"] = result["why"]
        if result.get("source_level"):
            merged["source_level"] = result["source_level"]
        if result.get("evidence_status"):
            merged["evidence_status"] = result["evidence_status"]
        if result.get("sources"):
            merged["sources"] = result["sources"]
        if result.get("need_confirm"):
            merged["need_confirm"] = result["need_confirm"]
        verdict = str(result.get("verdict", "")).strip().lower()
        if verdict in {"watch", "move_to_watch", "continue_tracking"}:
            # A watch verdict should reliably move the item into the follow-up section.
            merged["source_level"] = "线索待证"
            merged["evidence_status"] = "待确认"
            merged["follow_up"] = result.get("follow_up", merged.get("follow_up", merged["title"]))
        elif verdict in {"downgrade"}:
            merged["source_level"] = result.get("source_level", "次选证据")
            merged["evidence_status"] = result.get("evidence_status", "交叉验证中")
        elif verdict in {"keep", "confirm"}:
            merged["source_level"] = result.get("source_level", merged["source_level"])
            merged["evidence_status"] = result.get("evidence_status", merged["evidence_status"])
        updated_items.append(merged)
    return updated_items


def split_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    main_items: list[dict[str, Any]] = []
    follow_ups: list[str] = []
    for item in items:
        normalized = normalize_item(item)
        if normalized["source_level"] == "线索待证" or normalized["evidence_status"] == "待确认":
            follow_ups.append(normalized["title"])
            if normalized.get("follow_up"):
                follow_ups.append(str(normalized["follow_up"]))
            continue
        main_items.append(normalized)
        if normalized.get("follow_up"):
            follow_ups.append(str(normalized["follow_up"]))
    return main_items, follow_ups


def choose_item_limit(contract: Contract, explicit_limit: int | None) -> int:
    if explicit_limit:
        return explicit_limit
    return DEFAULT_COUNT_TARGETS.get(contract.depth, DEFAULT_COUNT_TARGETS["standard"])


def summarize_overview(contract: Contract, items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["本期未提供可保留条目，建议先补齐候选新闻再生成正式简报。"]
    top_titles = [item["title"] for item in items[:3]]
    overview = []
    overview.append(f"本期重点聚焦 {top_titles[0]}。")
    if len(top_titles) > 1:
        overview.append(f"同时还需关注 {top_titles[1]}。")
    if len(top_titles) > 2:
        overview.append(f"第三个值得跟进的主题是 {top_titles[2]}。")
    if contract.specialty:
        overview.append(f"专项关注维持在 {contract.specialty}。")
    return overview[:4]


def bucket_lines(items: list[dict[str, Any]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for item in items:
        grouped.setdefault(item["bucket"], []).append(f"{item['title']}：{item['why']}")
    return grouped


def render_item_block(
    item: dict[str, Any],
    index: int,
    importance_label: str = "为什么重要",
    include_followup_prompt: bool = False,
) -> list[str]:
    lines = [
        f"{index}. {item['title']}",
        f"发生了什么：{item['what']}",
        f"{importance_label}：{item['why']}",
        f"来源级别：{item['source_level']}",
        f"证据状态：{item['evidence_status']}",
    ]
    if include_followup_prompt and item.get("need_confirm"):
        lines.append(f"需要确认：{item['need_confirm']}")
    lines.append(f"来源：{render_sources(item['sources'])}")
    return lines


def render_quick_brief(contract: Contract, items: list[dict[str, Any]], follow_ups: list[str]) -> str:
    lines = [OPENING_LINE, "", f"简报时间：{date.today().isoformat()}", "", "今日概览"]
    lines.extend(summarize_overview(contract, items)[:2])
    lines.extend(["", "重点新闻"])
    for idx, item in enumerate(items[: choose_item_limit(contract, None)], start=1):
        lines.extend(render_item_block(item, idx))
        lines.append("")
    if follow_ups:
        lines.append("继续跟踪")
        for topic in follow_ups[:3]:
            lines.append(f"- {topic}")
    return "\n".join(lines).rstrip() + "\n"


def render_standard_digest(contract: Contract, items: list[dict[str, Any]], follow_ups: list[str]) -> str:
    lines = [
        OPENING_LINE,
        "",
        f"简报时间：{date.today().isoformat()}",
        f"覆盖范围：{'、'.join(contract.topic_mix)}",
        "",
        "今日概览",
    ]
    lines.extend(summarize_overview(contract, items))
    lines.extend(["", "重点新闻"])
    for idx, item in enumerate(items[: choose_item_limit(contract, None)], start=1):
        lines.extend(render_item_block(item, idx))
        if item.get("time_window"):
            lines.append(f"时间窗口：{item['time_window']}")
        lines.append("")
    lines.extend(["分主题速览", ""])
    for bucket, snippets in bucket_lines(items).items():
        lines.append(bucket)
        for snippet in snippets[:2]:
            lines.append(f"- {snippet}")
        lines.append("")
    lines.append("继续跟踪")
    for topic in follow_ups[:5] or ["暂无额外待确认条目"]:
        lines.append(f"- {topic}")
    return "\n".join(lines).rstrip() + "\n"


def render_analyst_watch(contract: Contract, items: list[dict[str, Any]], follow_ups: list[str]) -> str:
    lines = [OPENING_LINE, "", f"观察窗口：{contract.time_window}", "", "核心判断"]
    lines.extend(summarize_overview(contract, items))
    lines.extend(["", "高优先级项目"])
    for idx, item in enumerate(items[: choose_item_limit(contract, None)], start=1):
        lines.extend(render_item_block(item, idx, include_followup_prompt=True))
        lines.append("")
    lines.extend(["主题观察"])
    for bucket, snippets in bucket_lines(items).items():
        lines.append(bucket)
        for snippet in snippets[:2]:
            lines.append(f"- {snippet}")
        lines.append("")
    lines.append("继续跟踪")
    for topic in follow_ups[:6] or ["暂无额外待确认条目"]:
        lines.append(f"- {topic}")
    return "\n".join(lines).rstrip() + "\n"


def render_long_message(contract: Contract, items: list[dict[str, Any]], follow_ups: list[str]) -> str:
    top_items = items[:3]
    lines = [OPENING_LINE, "", f"今日热点简报 | {date.today().isoformat()}", "", "今日概览"]
    lines.extend(summarize_overview(contract, items))
    lines.extend(["", "重点新闻"])
    for idx, item in enumerate(top_items, start=1):
        lines.extend(render_item_block(item, idx))
        lines.append("")
    lines.extend(["分主题速览", ""])
    for bucket, snippets in bucket_lines(items).items():
        lines.append(bucket)
        for snippet in snippets[:2]:
            lines.append(f"- {snippet}")
        lines.append("")
    lines.append("继续跟踪")
    for topic in follow_ups[:5] or ["暂无额外待确认条目"]:
        lines.append(f"- {topic}")
    return "\n".join(lines).rstrip() + "\n"


def render_long_message_exec(contract: Contract, items: list[dict[str, Any]], follow_ups: list[str]) -> str:
    top_items = items[:3]
    lines = [OPENING_LINE, "", f"今日热点速览 | {date.today().isoformat()}", "", "一句话判断"]
    lines.extend(summarize_overview(contract, items)[:2])
    lines.extend(["", "最重要的三件事"])
    for idx, item in enumerate(top_items, start=1):
        lines.extend(render_item_block(item, idx, importance_label="影响判断"))
        lines.append("")
    lines.extend(["其他值得看"])
    grouped = bucket_lines(items)
    for bucket in ("AI与科技", "政治与政策", "商业与市场", "文化与社会", "体育", "专项关注"):
        snippets = grouped.get(bucket)
        if snippets:
            lines.append(f"- {bucket}：{snippets[0].split('：', 1)[-1]}")
    lines.extend(["", "继续跟踪"])
    for topic in follow_ups[:3] or ["暂无额外待确认条目"]:
        lines.append(f"- {topic}")
    return "\n".join(lines).rstrip() + "\n"


def render_digest(contract: Contract, items: list[dict[str, Any]], item_limit: int | None = None) -> str:
    main_items, follow_ups = split_items(items)
    limited_items = main_items[: choose_item_limit(contract, item_limit)]
    renderers = {
        "quick_brief": render_quick_brief,
        "standard_digest": render_standard_digest,
        "analyst_watch": render_analyst_watch,
        "long_message": render_long_message,
        "long_message_exec": render_long_message_exec,
    }
    renderer = renderers.get(contract.format, render_standard_digest)
    output = renderer(contract, limited_items, follow_ups)
    if contract.inferred_assumptions:
        output = output.rstrip() + "\n\n推断假设\n"
        for assumption in contract.inferred_assumptions:
            output += f"- {assumption}\n"
    return output


def cmd_digest(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items = load_items(Path(args.items_file))
    if args.verification_results_file:
        verification_results = load_verification_results(Path(args.verification_results_file))
        items = apply_verification_results(items, verification_results)
    print(render_digest(contract, items, args.item_limit))
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items_file = Path(args.items_file)
    items = load_items(items_file)
    artifact_paths = build_artifact_paths(items_file, Path(args.output_file) if args.output_file else None)
    verification_results_file = args.verification_results_file or artifact_paths["verification_results_file"]
    if verification_results_file and Path(verification_results_file).exists():
        verification_results = load_verification_results(Path(verification_results_file))
        items = apply_verification_results(items, verification_results)
    output = render_digest(contract, items, args.item_limit)
    output_file = args.output_file or artifact_paths["digest_output_file"]
    payload = {
        "artifact_paths": artifact_paths,
        "verification_results_file_used": verification_results_file if verification_results_file else "",
        "output_file": output_file,
        "rendered": output,
    }
    if output_file:
        Path(output_file).write_text(output, encoding="utf-8")
        payload["written_to"] = output_file
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_verify_results(args: argparse.Namespace) -> int:
    items = load_items(Path(args.items_file))
    raw_results = load_verification_results(Path(args.results_file)) if args.results_file else None
    package = build_verification_result_package(items, raw_results)

    if args.output_file:
        output_path = Path(args.output_file)
        if args.merge and output_path.exists():
            existing_results = load_verification_results(output_path)
            merged_results = merge_verification_results(existing_results, package["results"])
            package = build_verification_result_package(items, merged_results)
        write_json(output_path, package)
        package = {
            **package,
            "written_to": str(output_path),
            "write_mode": "merge" if args.merge else "overwrite",
        }

    print(
        json.dumps(
            package,
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone runner for more-news-briefing")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--time-window", dest="time_window")
        subparser.add_argument("--cadence")
        subparser.add_argument("--topic-mix", default="default")
        subparser.add_argument("--depth", choices=["quick", "standard", "analyst"])
        subparser.add_argument("--format")
        subparser.add_argument("--audience", choices=["personal", "executive", "research", "public"])
        subparser.add_argument("--mode", choices=["full", "standard", "minimal"])
        subparser.add_argument("--specialty", default="")
        subparser.add_argument("--specialty-keywords", default="")
        subparser.add_argument("--specialty-geography", default="")
        subparser.add_argument("--specialty-priority", default="")
        subparser.add_argument("--source-roles", default="")
        subparser.add_argument("--company-watchlist", default="")
        subparser.add_argument("--institution-watchlist", default="")
        subparser.add_argument("--community-watchlist", default="")

    contract_parser = subparsers.add_parser("contract", help="Resolve the briefing contract")
    add_common(contract_parser)
    contract_parser.set_defaults(func=cmd_contract)

    query_parser = subparsers.add_parser("queries", help="Emit built-in query packs")
    add_common(query_parser)
    query_parser.add_argument("--flat", action="store_true", help="Flatten grouped query packs")
    query_parser.set_defaults(func=cmd_queries)

    adapters_parser = subparsers.add_parser("adapters", help="Discover vendored adapters from vendor-manifest")
    adapters_parser.add_argument("--available-only", action="store_true")
    adapters_parser.set_defaults(func=cmd_adapters)

    route_parser = subparsers.add_parser("route", help="Recommend retrieval, verification, and polish routes")
    add_common(route_parser)
    route_parser.set_defaults(func=cmd_route)

    collect_parser = subparsers.add_parser("collect", help="Build the collect-stage execution plan")
    add_common(collect_parser)
    collect_parser.set_defaults(func=cmd_collect)

    verify_parser = subparsers.add_parser("verify", help="Build the verify-stage execution plan")
    add_common(verify_parser)
    verify_parser.add_argument("--items-file", required=True)
    verify_parser.set_defaults(func=cmd_verify)

    verify_results_parser = subparsers.add_parser(
        "verify-results",
        help="Emit or normalize the stable verification-results contract",
    )
    verify_results_parser.add_argument("--items-file", required=True)
    verify_results_parser.add_argument("--results-file")
    verify_results_parser.add_argument("--output-file")
    verify_results_parser.add_argument("--merge", action="store_true")
    verify_results_parser.set_defaults(func=cmd_verify_results)

    polish_parser = subparsers.add_parser("polish", help="Build the polish-stage execution plan")
    add_common(polish_parser)
    polish_parser.add_argument("--items-file")
    polish_parser.add_argument("--draft-file")
    polish_parser.set_defaults(func=cmd_polish)

    pipeline_parser = subparsers.add_parser("pipeline", help="Build the full collect/verify/polish execution plan")
    add_common(pipeline_parser)
    pipeline_parser.add_argument("--items-file")
    pipeline_parser.add_argument("--draft-file")
    pipeline_parser.set_defaults(func=cmd_pipeline)

    execute_parser = subparsers.add_parser("execute", help="Build a sequential execute-ready queue")
    add_common(execute_parser)
    execute_parser.add_argument("--items-file")
    execute_parser.add_argument("--draft-file")
    execute_parser.set_defaults(func=cmd_execute)

    digest_parser = subparsers.add_parser("digest", help="Render a digest from JSON items")
    add_common(digest_parser)
    digest_parser.add_argument("--items-file", required=True)
    digest_parser.add_argument("--verification-results-file")
    digest_parser.add_argument("--item-limit", type=int)
    digest_parser.set_defaults(func=cmd_digest)

    finalize_parser = subparsers.add_parser("finalize", help="Render and optionally write the final digest artifact")
    add_common(finalize_parser)
    finalize_parser.add_argument("--items-file", required=True)
    finalize_parser.add_argument("--verification-results-file")
    finalize_parser.add_argument("--output-file")
    finalize_parser.add_argument("--item-limit", type=int)
    finalize_parser.set_defaults(func=cmd_finalize)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
