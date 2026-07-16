#!/usr/bin/env python3
"""Standalone helper for the more-news-briefing skill.

This runner keeps the core orchestration local to the skill:
- contract normalization
- query-pack generation
- template-based digest rendering
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import sys
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
DEFAULT_COGNITIVE_FEATURES = ["interrogate"]
DEFAULT_SOURCE_ROLES = ["discovery", "verification"]
SPECIALTY_SOURCE_ROLES = ["discovery", "verification", "context", "watch"]
DEFAULT_TOPICS = ["AI与科技", "政治与政策", "商业与市场", "文化与社会", "体育"]
DEFAULT_COUNT_TARGETS = {"quick": 5, "standard": 8, "analyst": 8}
VERIFICATION_RESULT_REQUIRED_FIELDS = ["verdict"]
VERIFICATION_RESULT_OPTIONAL_FIELDS = [
    "item_id",
    "canonical_url",
    "title",
    "claim",
    "why",
    "source_level",
    "evidence_status",
    "sources",
    "need_confirm",
    "follow_up",
]
VERIFICATION_VERDICTS = {
    "keep",
    "confirm",
    "downgrade",
    "watch",
    "move_to_watch",
    "continue_tracking",
}
SOURCE_LEVELS = {"首选证据", "次选证据", "线索待证"}
EVIDENCE_STATUSES = {"已确认", "交叉验证中", "待确认"}
SOURCE_ROLES = {"discovery", "verification", "context", "watch"}
CADENCES = {"one_off", "daily", "weekly", "custom"}
COGNITIVE_FEATURES = {"interrogate", "sprout", "commentary", "continuity"}
SPECIALTY_PRIORITIES = {
    "policy",
    "product",
    "products",
    "financing",
    "safety",
    "standards",
    "bids",
    "deployments",
    "research",
}
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

SOURCE_PACKS = {
    "AI与科技": {
        "discovery": ["Google News RSS", "IT之家", "Hacker News"],
        "verification": ["官方公司或实验室博客", "论文或模型卡", "GitHub Releases"],
        "context": ["OSS Insight", "Reddit"],
    },
    "政治与政策": {
        "discovery": ["澎湃新闻", "中国日报", "GDELT"],
        "verification": ["政府或监管机构", "法案或正式文件", "权威直接报道"],
    },
    "商业与市场": {
        "discovery": ["Google News RSS", "腾讯财经", "网易财经"],
        "verification": ["交易所公告", "公司投资者关系", "监管披露"],
        "context": ["OpenBB"],
    },
    "文化与社会": {
        "discovery": ["网易新闻", "腾讯新闻", "搜狐新闻"],
        "verification": ["原始发布方", "平台或主办方", "权威直接报道"],
    },
    "体育": {
        "discovery": ["腾讯体育", "中国日报体育"],
        "verification": ["官方赛事", "联盟或俱乐部", "正式成绩页"],
    },
    "专项关注": {
        "discovery": ["Google News RSS", "行业垂直来源"],
        "verification": ["官方机构", "公司公告", "标准或招投标文件"],
        "context": ["GitHub", "专业社区"],
    },
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
    cognitive_features: list[str] = field(default_factory=lambda: DEFAULT_COGNITIVE_FEATURES.copy())
    source_roles: list[str] = field(default_factory=lambda: DEFAULT_SOURCE_ROLES.copy())
    specialty: str = ""
    specialty_scope: str = ""
    specialty_keywords: list[str] = field(default_factory=list)
    specialty_exclusions: list[str] = field(default_factory=list)
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
            "cognitive_features": self.cognitive_features,
            "source_roles": self.source_roles,
            "specialty": self.specialty,
            "specialty_scope": self.specialty_scope,
            "specialty_keywords": self.specialty_keywords,
            "specialty_exclusions": self.specialty_exclusions,
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
        entrypoints = [str(value) for value in skill.get("entrypoints", []) if str(value)]
        entrypoint_paths = [
            (snapshot_abs / entrypoint).resolve() for entrypoint in entrypoints
        ] if snapshot_abs else []
        entrypoints_ready = bool(entrypoint_paths) and all(path.exists() for path in entrypoint_paths)
        credential_env = str(skill.get("credential_env", "")).strip()
        credential_required = bool(skill.get("credential_required", False))
        credential_ready = not credential_required or bool(os.environ.get(credential_env))
        health_status = "ready" if present and entrypoints_ready and credential_ready else "unavailable"
        license_status = str(skill.get("license_status", "unresolved")).strip().lower()
        routable = health_status == "ready" and license_status == "verified"
        entry = {
            "name": skill.get("name", ""),
            "role": skill.get("role", ""),
            "bundled": bool(skill.get("bundled", False)),
            "required_by_default": bool(skill.get("required_by_default", False)),
            "snapshot_path": snapshot_rel,
            "snapshot_present": present,
            "snapshot_abspath": str(snapshot_abs) if snapshot_abs else "",
            "entrypoints": entrypoints,
            "entrypoints_ready": entrypoints_ready,
            "credential_env": credential_env,
            "credential_required": credential_required,
            "credential_ready": credential_ready,
            "health_status": health_status,
            "license_status": license_status,
            "routable": routable,
            "license_note": skill.get("license_note", ""),
            "update_policy": skill.get("update_policy", ""),
        }
        discovered.append(entry)
    available = [entry["name"] for entry in discovered if entry["routable"]]
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


def validate_time_window(value: str) -> None:
    if value in {"today", "last_24h", "last_3d", "last_7d"}:
        return
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:\.\.|:)\d{4}-\d{2}-\d{2}", value):
        return
    raise ValueError(f"invalid time_window: {value}")


def validate_contract_values(args: argparse.Namespace) -> None:
    if args.time_window:
        validate_time_window(args.time_window)
    if args.cadence and args.cadence not in CADENCES:
        raise ValueError(f"invalid cadence: {args.cadence}")
    if args.format and args.format not in FORMAT_ALIASES:
        raise ValueError(f"invalid format: {args.format}")
    roles = split_csv(args.source_roles)
    unknown_roles = sorted(set(roles) - SOURCE_ROLES)
    if unknown_roles:
        raise ValueError("invalid source roles: " + ", ".join(unknown_roles))
    priority = str(args.specialty_priority or "").strip().lower()
    if priority and priority not in SPECIALTY_PRIORITIES:
        raise ValueError(f"invalid specialty priority: {args.specialty_priority}")
    raw_features = getattr(args, "cognitive_features", None)
    features = normalize_cognitive_features(raw_features) if raw_features is not None else []
    unknown_features = sorted(set(features) - COGNITIVE_FEATURES)
    if unknown_features:
        raise ValueError("invalid cognitive features: " + ", ".join(unknown_features))


def normalize_cognitive_features(value: str | None) -> list[str]:
    if value is None or value.strip().lower() == "default":
        return DEFAULT_COGNITIVE_FEATURES.copy()
    if value.strip().lower() in {"", "off", "none"}:
        return []
    if value.strip().lower() == "all":
        return ["interrogate", "sprout", "commentary", "continuity"]

    return list(dict.fromkeys(part.lower() for part in split_csv(value)))


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
    validate_contract_values(args)
    specialty = args.specialty or ""
    depth = args.depth or DEFAULT_DEPTH
    audience = args.audience or DEFAULT_AUDIENCE
    contract = Contract()
    contract.specialty = specialty
    contract.specialty_scope = getattr(args, "specialty_scope", "") or ""
    contract.specialty_keywords = split_csv(args.specialty_keywords) or split_csv(specialty.replace("/", ","))
    contract.specialty_exclusions = split_csv(getattr(args, "specialty_exclusions", ""))
    contract.specialty_geography = args.specialty_geography or ""
    contract.specialty_priority = (args.specialty_priority or "").lower()
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

    contract.cognitive_features = normalize_cognitive_features(
        getattr(args, "cognitive_features", None)
    )
    if getattr(args, "cognitive_features", None) is None:
        contract.inferred_assumptions.append(
            "cognitive_features=" + "+".join(DEFAULT_COGNITIVE_FEATURES)
        )

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


def build_watch_queries(contract: Contract) -> list[str]:
    queries = [f"{name} official newsroom latest" for name in contract.company_watchlist]
    queries.extend(
        f"{name} official announcement policy latest"
        for name in contract.institution_watchlist
    )
    queries.extend(
        f"{name} latest release discussion"
        for name in contract.community_watchlist
    )
    return queries


def exclusion_terms(values: list[str]) -> str:
    return " ".join(f'-"{value}"' if " " in value else f"-{value}" for value in values)


def build_specialty_queries(contract: Contract) -> dict[str, list[str]]:
    base_terms = contract.specialty_keywords or [contract.specialty]
    geography = contract.specialty_geography.strip()
    priority = contract.specialty_priority.strip()
    scope = contract.specialty_scope.strip()
    excluded = exclusion_terms(contract.specialty_exclusions)
    core = " ".join([*base_terms[:4], scope, excluded]).strip()
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
        "watch": build_watch_queries(contract),
    }


def build_queries(contract: Contract, grouped: bool = True) -> dict[str, Any]:
    queries: dict[str, Any] = {}
    for topic in contract.topic_mix:
        if topic == "专项关注":
            groups = build_specialty_queries(contract)
        else:
            raw_groups = QUERY_LIBRARY.get(
                topic,
                {"core": [topic], "news": [], "institutional": [], "community": []},
            )
            groups = {name: list(values) for name, values in raw_groups.items()}
            groups.setdefault("watch", [])
        if grouped:
            queries[topic] = groups
        else:
            flattened: list[str] = []
            for group_name in ("core", "news", "institutional", "community", "watch"):
                flattened.extend(groups.get(group_name, []))
            queries[topic] = flattened
    watch_queries = build_watch_queries(contract)
    if watch_queries and "专项关注" not in queries:
        queries["观察名单"] = {"watch": watch_queries} if grouped else watch_queries
    return queries


def build_source_targets(contract: Contract) -> dict[str, Any]:
    return {
        "catalog": "references/borrowed-source-catalog.md",
        "source_roles": contract.source_roles,
        "source_packs": {
            topic: SOURCE_PACKS.get(topic, SOURCE_PACKS["专项关注"])
            for topic in contract.topic_mix
        },
        "watchlists": {
            "companies": contract.company_watchlist,
            "institutions": contract.institution_watchlist,
            "communities": contract.community_watchlist,
        },
    }


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
    for key in ("news", "core", "institutional", "community", "watch"):
        values = groups.get(key, [])
        if values:
            return values[0]
    return ""


def build_anysearch_batches(contract: Contract) -> list[dict[str, Any]]:
    grouped_queries = build_queries(contract, grouped=True)
    batch_topics = [
        ("Batch A", ["AI与科技", "政治与政策", "商业与市场"]),
        ("Batch B", ["文化与社会", "体育", "专项关注", "观察名单"]),
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
        payload_json = json.dumps(compact_payload, ensure_ascii=False)
        command_argv = [
            sys.executable,
            str(anysearch_script),
            "batch_search",
            "--queries",
            payload_json,
        ]
        batches.append(
            {
                "batch_name": batch_name,
                "topics": [item["topic"] for item in query_objects],
                "query_objects": query_objects,
                "payload": compact_payload,
                "command_argv": command_argv,
                "command_hint": shlex.join(command_argv),
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
        "source_targets": build_source_targets(contract),
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
                "item_id": item.get("item_id", ""),
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


def make_result_stub_path(output_file: str, title: str, item_id: str = "") -> str:
    if not output_file:
        return ""
    output_path = Path(output_file)
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", title).strip("-").lower() or "result"
    if item_id:
        slug = f"{slug}-{item_id[-8:]}"
    suffix = "".join(output_path.suffixes) or ".json"
    base_name = output_path.name[: -len(suffix)] if suffix else output_path.name
    return str(output_path.with_name(f"{base_name}.{slug}.json"))


def build_verification_result_contract() -> dict[str, Any]:
    return {
        "version": 1,
        "required_fields": VERIFICATION_RESULT_REQUIRED_FIELDS,
        "identity_fields": {
            "at_least_one": ["item_id", "canonical_url", "title"],
            "preference_order": ["item_id", "canonical_url", "title"],
            "title_fallback": "unique_titles_only",
        },
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
        "item_id": item["item_id"],
        "canonical_url": item.get("canonical_url", ""),
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
        result_stub_file = make_result_stub_path(
            verification_results_file,
            item["title"],
            item.get("item_id", ""),
        )
        tasks.append(
            {
                "task_id": f"builtin-verify-{idx}",
                "item_id": item.get("item_id", ""),
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
    if set(contract.cognitive_features) & {"sprout", "commentary", "continuity"}:
        goals.append("保持事实、编辑判断、推断和下期追踪之间的边界。")
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
    if "sprout" in contract.cognitive_features:
        checks.append("检查认知延伸是否保留依据与性质：推断标签")
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
                "不删除认知延伸的依据与性质：推断标签",
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
        digest_output_file = str(
            items_file.with_name(f"daily-news-{date.today().isoformat()}.md")
        )

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

    steps.extend(
        [
            {
                "step": "normalize",
                "status": "ready",
                "adapter": "built_in",
                "execution_mode": "normalize_deduplicate",
                "primary_inputs": {"source_targets": collect_plan.get("source_targets", {})},
                "artifacts": [],
                "fallback": {},
            },
            {
                "step": "rank",
                "status": "ready",
                "adapter": "built_in",
                "execution_mode": "rank_retain",
                "primary_inputs": {
                    "ranking_order": ["consequence", "recency", "attention", "relevance", "novelty"],
                    "items_file": artifact_paths.get("items_file", ""),
                },
                "artifacts": [],
                "fallback": {},
            },
        ]
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
    else:
        steps.append(
            {
                "step": "verify",
                "status": "blocked_on_retained_items",
                "adapter": "built_in_verification",
                "execution_mode": "built_in_verification",
                "primary_inputs": {
                    "verify_candidate_count": 0,
                    "verify_candidates": [],
                    "verification_results_file": artifact_paths.get("verification_results_file", ""),
                },
                "artifacts": [],
                "fallback": {},
            }
        )

    steps.extend(
        [
            {
                "step": "render",
                "status": "ready" if artifact_paths.get("items_file") else "blocked_on_retained_items",
                "adapter": "built_in",
                "execution_mode": "render_digest",
                "primary_inputs": {
                    "items_file": artifact_paths.get("items_file", ""),
                    "verification_results_file": artifact_paths.get("verification_results_file", ""),
                    "digest_output_file": artifact_paths.get("digest_output_file", ""),
                    "cognitive_features": contract.cognitive_features,
                },
                "artifacts": [],
                "fallback": {},
            },
            {
                "step": "cognition",
                "status": "ready" if contract.cognitive_features else "disabled",
                "adapter": "built_in",
                "execution_mode": "cognitive_layer",
                "primary_inputs": {
                    "items_file": artifact_paths.get("items_file", ""),
                    "digest_output_file": artifact_paths.get("digest_output_file", ""),
                    "features": contract.cognitive_features,
                },
                "artifacts": [],
                "fallback": {},
            },
            {
                "step": "acceptance",
                "status": "ready",
                "adapter": "built_in",
                "execution_mode": "acceptance_gate",
                "primary_inputs": {
                    "digest_output_file": artifact_paths.get("digest_output_file", ""),
                    "cognitive_features": contract.cognitive_features,
                },
                "artifacts": [],
                "fallback": {},
            },
        ]
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
        "version": 2,
        "contract_summary": {
            "time_window": contract.time_window,
            "topic_mix": contract.topic_mix,
            "depth": contract.depth,
            "format": contract.format,
            "audience": contract.audience,
            "mode": contract.mode,
            "cognitive_features": contract.cognitive_features,
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

    def add_queue_item(**item: Any) -> None:
        nonlocal ordinal
        argv = item.pop("command_argv", [])
        item["order"] = ordinal
        item["command_argv"] = argv
        item["command"] = shlex.join(argv) if argv else item.get("command", "")
        queue.append(item)
        ordinal += 1

    for step in handoff_package.get("steps", []):
        execution_mode = step.get("execution_mode", "")
        if execution_mode == "anysearch_batch_search":
            for batch in step.get("artifacts", []):
                add_queue_item(
                    phase=step["step"],
                    executor=step.get("adapter"),
                    action="run_batch_search",
                    target=batch.get("batch_name", ""),
                    command_argv=batch.get("command_argv", []),
                    payload=batch.get("payload", []),
                    requires_network=True,
                    consumes_artifact="query_pack",
                    produces_artifact="candidate_pool",
                    success_signal="batch_search returns result set for every query object",
                )
        elif execution_mode == "native_web_search":
            add_queue_item(
                phase=step["step"],
                executor=step.get("adapter"),
                action="run_native_web_queries",
                target=step["step"],
                payload=step.get("primary_inputs", {}).get("queries", {}),
                requires_network=True,
                consumes_artifact="query_pack",
                produces_artifact="candidate_pool",
                success_signal="top queries return enough candidate headlines to move into normalization",
            )
        elif execution_mode == "normalize_deduplicate":
            add_queue_item(
                phase="normalize",
                executor="built_in",
                action="normalize_and_deduplicate",
                target="candidate_pool",
                payload=step.get("primary_inputs", {}),
                requires_network=False,
                consumes_artifact="candidate_pool",
                produces_artifact="normalized_candidates",
                success_signal="candidate records have stable item_id values and duplicate stories are merged",
            )
        elif execution_mode == "rank_retain":
            add_queue_item(
                phase="rank",
                executor="built_in",
                action="rank_and_retain",
                target=artifact_paths.get("items_file", "") or "retained-items.json",
                payload=step.get("primary_inputs", {}),
                requires_network=False,
                consumes_artifact="normalized_candidates",
                produces_artifact="retained_items",
                success_signal="items are ranked and weak evidence is moved to follow-up",
            )
        elif execution_mode == "deep_research_fact_check_tasks":
            for task in step.get("artifacts", []):
                result_stub_file = make_result_stub_path(
                    step.get("primary_inputs", {}).get("verification_results_file", ""),
                    task.get("title", ""),
                    task.get("item_id", ""),
                )
                merge_argv = []
                if artifact_paths.get("items_file") and result_stub_file:
                    merge_argv = [
                        sys.executable,
                        str(runner_path),
                        "verify-results",
                        "--items-file",
                        artifact_paths["items_file"],
                        "--results-file",
                        result_stub_file,
                        "--output-file",
                        step.get("primary_inputs", {}).get("verification_results_file", ""),
                        "--merge",
                    ]
                add_queue_item(
                    phase=step["step"],
                    executor=step.get("adapter"),
                    action="run_fact_check_task",
                    target=task.get("item_id") or task.get("title", ""),
                    command=task.get("command_prompt", ""),
                    payload=task,
                    requires_network=True,
                    consumes_artifact="retained_items",
                    produces_artifact="verification_results",
                    output_file=step.get("primary_inputs", {}).get("verification_results_file", ""),
                    result_stub_file=result_stub_file,
                    success_signal="task returns keep/downgrade/watch judgment with stronger evidence",
                    next_action_summary="append normalized verification result into the shared verification-results file",
                    merge_command_argv=merge_argv,
                    merge_command_hint=shlex.join(merge_argv) if merge_argv else "",
                )
        elif execution_mode == "built_in_verification":
            tasks = step.get("artifacts", []) or [{}]
            for task in tasks:
                result_stub_file = make_result_stub_path(
                    step.get("primary_inputs", {}).get("verification_results_file", ""),
                    task.get("title", "verification-result"),
                    task.get("item_id", ""),
                )
                merge_argv: list[str] = []
                if artifact_paths.get("items_file") and result_stub_file:
                    merge_argv = [
                        sys.executable,
                        str(runner_path),
                        "verify-results",
                        "--items-file",
                        artifact_paths["items_file"],
                        "--results-file",
                        result_stub_file,
                        "--output-file",
                        step.get("primary_inputs", {}).get("verification_results_file", ""),
                        "--merge",
                    ]
                add_queue_item(
                    phase=step["step"],
                    executor=step.get("adapter"),
                    action="run_builtin_checks",
                    target=task.get("item_id") or task.get("title") or step["step"],
                    payload=task,
                    requires_network=False,
                    consumes_artifact="retained_items",
                    produces_artifact="verification_results",
                    output_file=step.get("primary_inputs", {}).get("verification_results_file", ""),
                    result_stub_file=result_stub_file,
                    success_signal="candidate is normalized into keep/downgrade/watch verification result",
                    next_action_summary="write the built-in verification judgment into the shared verification-results file",
                    merge_command_hint=shlex.join(merge_argv) if merge_argv else "",
                    merge_command_argv=merge_argv,
                )
        elif execution_mode == "render_digest":
            inputs = step.get("primary_inputs", {})
            render_argv: list[str] = []
            if inputs.get("items_file"):
                render_argv = [
                    sys.executable,
                    str(runner_path),
                    "digest",
                    "--items-file",
                    inputs["items_file"],
                ]
                if inputs.get("verification_results_file"):
                    render_argv.extend(
                        ["--verification-results-file", inputs["verification_results_file"]]
                    )
                render_argv.extend(
                    ["--cognitive-features", ",".join(inputs.get("cognitive_features", [])) or "off"]
                )
            add_queue_item(
                phase="render",
                executor="built_in",
                action="render_digest",
                target=inputs.get("digest_output_file", "") or "draft-briefing.md",
                command_argv=render_argv,
                payload=inputs,
                requires_network=False,
                consumes_artifact="retained_items",
                produces_artifact="draft_briefing",
                success_signal="digest is rendered with source and evidence fields",
            )
        elif execution_mode == "cognitive_layer" and step.get("status") != "disabled":
            inputs = step.get("primary_inputs", {})
            add_queue_item(
                phase="cognition",
                executor="built_in",
                action="run_cognitive_layer",
                target=inputs.get("digest_output_file", "") or "draft-briefing.md",
                payload=inputs,
                requires_network=False,
                consumes_artifact="draft_briefing",
                produces_artifact="cognitive_draft",
                success_signal="enabled cognitive features stay separated from verified news fields",
            )
        elif execution_mode == "acceptance_gate":
            acceptance_inputs = step.get("primary_inputs", {})
            add_queue_item(
                phase="acceptance",
                executor="built_in",
                action="run_acceptance_gate",
                target=acceptance_inputs.get("digest_output_file", ""),
                payload=acceptance_inputs,
                requires_network=False,
                consumes_artifact=(
                    "cognitive_draft" if acceptance_inputs.get("cognitive_features") else "draft_briefing"
                ),
                produces_artifact="acceptance_report",
                success_signal="no blocking evidence or structure issues remain",
            )
        elif execution_mode == "humanizer_zh_edit_task":
            artifact = step.get("artifacts", [{}])[0]
            add_queue_item(
                phase=step["step"],
                executor=step.get("adapter"),
                action="run_humanizer_edit",
                target=step.get("primary_inputs", {}).get("draft_file", ""),
                command=artifact.get("command_prompt", ""),
                payload=artifact,
                requires_network=False,
                consumes_artifact="acceptance_report",
                produces_artifact="final_briefing",
                success_signal="draft reads more naturally without changing facts or evidence labels",
            )
        elif execution_mode == "built_in_polish":
            add_queue_item(
                phase=step["step"],
                executor=step.get("adapter"),
                action="run_builtin_polish_checks",
                target=step.get("primary_inputs", {}).get("draft_file", "") or step["step"],
                payload=step.get("artifacts", []),
                requires_network=False,
                consumes_artifact="acceptance_report",
                produces_artifact="final_briefing",
                success_signal="draft passes structure and wording checks",
            )
    next_action_summary = queue[0] if queue else {}
    return {
        "version": 2,
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
        "source_targets": build_source_targets(contract),
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
    verification_init_argv: list[str] = []
    digest_argv: list[str] = []
    if artifact_paths["items_file"] and artifact_paths["verification_results_file"]:
        verification_init_argv = [
            sys.executable,
            str(Path(__file__).resolve()),
            "verify-results",
            "--items-file",
            artifact_paths["items_file"],
            "--output-file",
            artifact_paths["verification_results_file"],
        ]
        digest_argv = [
            sys.executable,
            str(Path(__file__).resolve()),
            "digest",
            "--items-file",
            artifact_paths["items_file"],
            "--verification-results-file",
            artifact_paths["verification_results_file"],
            "--cognitive-features",
            ",".join(contract.cognitive_features) or "off",
        ]
    payload = {
        "contract_summary": {
            "topic_mix": contract.topic_mix,
            "depth": contract.depth,
            "format": contract.format,
            "audience": contract.audience,
            "cognitive_features": contract.cognitive_features,
        },
        "artifact_paths": artifact_paths,
        "handoff_package": handoff,
        "execute_queue": build_execute_queue(handoff),
        "verification_results_init_command_argv": verification_init_argv,
        "verification_results_init_command_hint": shlex.join(verification_init_argv) if verification_init_argv else "",
        "digest_command_argv": digest_argv,
        "digest_command_hint": shlex.join(digest_argv) if digest_argv else "",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def load_items(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("items file must contain a JSON array")
    if any(not isinstance(item, dict) for item in data):
        raise ValueError("every item must be a JSON object")
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
    if not isinstance(result, dict):
        raise ValueError("verification result must be a JSON object")
    verdict = str(result.get("verdict", "")).strip().lower()
    if verdict not in VERIFICATION_VERDICTS:
        raise ValueError(f"unknown verification verdict: {verdict or '<empty>'}")
    normalized = {
        "title": str(result.get("title", "")).strip(),
        "verdict": verdict,
    }
    for field in VERIFICATION_RESULT_OPTIONAL_FIELDS:
        value = result.get(field)
        if value not in (None, "", []):
            normalized[field] = value
    if not normalized["title"] and not normalized.get("item_id") and not normalized.get("canonical_url"):
        raise ValueError("verification result requires item_id, canonical_url, or title")
    return normalized


def verification_identity(result: dict[str, Any]) -> str:
    if result.get("item_id"):
        return "id:" + str(result["item_id"])
    if result.get("canonical_url"):
        return "url:" + str(result["canonical_url"]).strip().lower()
    return "title:" + normalize_identity_text(str(result.get("title", "")))


def merge_verification_results(
    existing_results: list[dict[str, Any]],
    incoming_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged_by_identity: dict[str, dict[str, Any]] = {}
    for result in existing_results:
        normalized = normalize_verification_result(result)
        merged_by_identity[verification_identity(normalized)] = normalized
    for result in incoming_results:
        normalized = normalize_verification_result(result)
        merged_by_identity[verification_identity(normalized)] = normalized
    return list(merged_by_identity.values())


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
        allowed_ids = {item["item_id"] for item in verify_items}
        allowed_urls = {
            item.get("canonical_url", "") for item in verify_items if item.get("canonical_url")
        }
        title_counts: dict[str, int] = {}
        for item in verify_items:
            key = normalize_identity_text(item["title"])
            title_counts[key] = title_counts.get(key, 0) + 1
        for raw in raw_results:
            normalized = normalize_verification_result(raw)
            matched = normalized.get("item_id") in allowed_ids
            matched = matched or normalized.get("canonical_url") in allowed_urls
            title_key = normalize_identity_text(normalized.get("title", ""))
            matched = matched or bool(title_key and title_counts.get(title_key) == 1)
            if not matched:
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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_sources(sources: Any) -> str:
    if isinstance(sources, list):
        rendered: list[str] = []
        for item in sources:
            if isinstance(item, dict):
                name = str(item.get("name") or item.get("source_name") or "").strip()
                url = str(item.get("url") or item.get("canonical_url") or "").strip()
                rendered.append(f"{name} ({url})" if name and url else name or url)
            else:
                rendered.append(str(item))
        return "、".join(value for value in rendered if value)
    return str(sources or "")


def normalize_identity_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def make_item_id(item: dict[str, Any]) -> str:
    explicit = str(item.get("item_id", "")).strip()
    if explicit:
        return explicit
    canonical_url = str(item.get("canonical_url", "")).strip().lower()
    identity = canonical_url or normalize_identity_text(str(item.get("title", "")))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return f"news-{digest}"


def normalize_sources(sources: Any) -> list[Any]:
    if sources in (None, ""):
        return []
    if isinstance(sources, list):
        return [source for source in sources if source not in (None, "", {})]
    return [sources]


def item_validation_errors(item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field_name in ("title", "what", "why", "bucket"):
        value = str(item.get(field_name, "")).strip()
        if not value or value in {"未命名条目", "待补充", "未分类"}:
            errors.append(f"missing_or_placeholder:{field_name}")
    if not normalize_sources(item.get("sources")):
        errors.append("missing:sources")
    if item.get("source_level") not in SOURCE_LEVELS:
        errors.append("invalid:source_level")
    if item.get("evidence_status") not in EVIDENCE_STATUSES:
        errors.append("invalid:evidence_status")
    return errors


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("each item must be a JSON object")
    normalized = dict(item)
    normalized.setdefault("title", "未命名条目")
    normalized.setdefault("what", "待补充")
    normalized.setdefault("why", "待补充")
    normalized.setdefault("bucket", "未分类")
    normalized.setdefault("source_level", "次选证据")
    normalized.setdefault("evidence_status", "交叉验证中")
    normalized["sources"] = normalize_sources(normalized.get("sources", []))
    normalized["item_id"] = make_item_id(normalized)
    normalized["canonical_url"] = str(normalized.get("canonical_url", "")).strip()
    validation_errors = item_validation_errors(normalized)
    if validation_errors:
        normalized["_validation_errors"] = validation_errors
        normalized["source_level"] = "线索待证"
        normalized["evidence_status"] = "待确认"
    return normalized


def item_dedup_key(item: dict[str, Any]) -> str:
    if item.get("canonical_url"):
        return "url:" + item["canonical_url"].lower()
    return "title:" + normalize_identity_text(item["title"])


def merge_item_sources(left: list[Any], right: list[Any]) -> list[Any]:
    merged: list[Any] = []
    seen: set[str] = set()
    for source in [*left, *right]:
        key = json.dumps(source, ensure_ascii=False, sort_keys=True) if isinstance(source, dict) else str(source)
        if key not in seen:
            seen.add(key)
            merged.append(source)
    return merged


def normalize_and_deduplicate_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduplicated: dict[str, dict[str, Any]] = {}
    for raw_item in items:
        item = normalize_item(raw_item)
        key = item_dedup_key(item)
        if key not in deduplicated:
            deduplicated[key] = item
            continue
        existing = deduplicated[key]
        existing["sources"] = merge_item_sources(existing["sources"], item["sources"])
        if existing.get("source_level") != "首选证据" and item.get("source_level") == "首选证据":
            for field_name in ("what", "why", "source_level", "evidence_status", "canonical_url"):
                if item.get(field_name):
                    existing[field_name] = item[field_name]
        if item.get("follow_up") and not existing.get("follow_up"):
            existing["follow_up"] = item["follow_up"]
        existing_errors = item_validation_errors(existing)
        if existing_errors:
            existing["_validation_errors"] = existing_errors
        else:
            existing.pop("_validation_errors", None)
    return list(deduplicated.values())


def item_rank_score(item: dict[str, Any], contract: Contract) -> float:
    score = 0.0
    score += 3.0 if item.get("source_level") == "首选证据" else 1.0
    score += 2.0 if item.get("evidence_status") == "已确认" else 0.5
    if item.get("bucket") in {"政治与政策", "商业与市场", "专项关注"}:
        score += 1.0
    if item.get("bucket") == "专项关注" and contract.specialty:
        score += 2.0
    for field_name in ("consequence", "recency", "attention", "relevance", "novelty"):
        value = item.get(field_name, 0)
        if isinstance(value, (int, float)):
            score += float(value)
    explicit = item.get("priority_score")
    if isinstance(explicit, (int, float)):
        score += float(explicit)
    return score


def prepare_items(contract: Contract, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = normalize_and_deduplicate_items(items)
    return sorted(normalized, key=lambda item: item_rank_score(item, contract), reverse=True)


def build_cognitive_review(contract: Contract, items: list[dict[str, Any]]) -> dict[str, Any]:
    if "interrogate" not in contract.cognitive_features:
        return {"enabled": False, "issues": []}

    issues: list[str] = []
    main_items, _ = split_items(items)
    for item in main_items:
        if item["bucket"] in {"政治与政策", "商业与市场", "专项关注"} and len(item["sources"]) < 2:
            issues.append(f"single_source_high_impact:{item['item_id']}")
        if item.get("causal_claim") and not item.get("causal_basis"):
            issues.append(f"causal_claim_missing_basis:{item['item_id']}")
        if item.get("counterevidence_checked") is False:
            issues.append(f"counterevidence_not_checked:{item['item_id']}")
    return {"enabled": True, "issues": list(dict.fromkeys(issues))}


def build_acceptance_report(
    contract: Contract,
    items: list[dict[str, Any]],
    rendered: str = "",
) -> dict[str, Any]:
    normalized = [normalize_item(item) for item in items]
    main_items, follow_ups = split_items(normalized)
    blocking_issues: list[str] = []
    warnings: list[str] = []
    for item in normalized:
        for issue in item.get("_validation_errors", []):
            blocking_issues.append(f"{item['item_id']}:{issue}")
    for item in main_items:
        if item["bucket"] in {"政治与政策", "商业与市场", "专项关注"} and (
            item["source_level"] != "首选证据" or item["evidence_status"] != "已确认"
        ):
            warnings.append(f"high_impact_needs_stronger_evidence:{item['item_id']}")
    target = DEFAULT_COUNT_TARGETS.get(contract.depth, DEFAULT_COUNT_TARGETS["standard"])
    if main_items and len(main_items) < min(5, target):
        warnings.append(f"retained_item_count_below_target:{len(main_items)}/{target}")
    if rendered and "来源：" not in rendered and main_items:
        blocking_issues.append("rendered_digest_missing_source_lines")
    cognitive_review = build_cognitive_review(contract, normalized)
    warnings.extend(cognitive_review["issues"])
    if "sprout" in contract.cognitive_features and rendered and "认知延伸" in rendered:
        rendered_lines = rendered.splitlines()
        section_start = rendered_lines.index("认知延伸") + 1
        extension_lines: list[str] = []
        for line in rendered_lines[section_start:]:
            if not line.strip():
                break
            if not line.startswith("- "):
                break
            extension_lines.append(line)
        if not extension_lines or any(
            "依据：" not in line or "性质：推断" not in line for line in extension_lines
        ):
            blocking_issues.append("cognitive_extension_missing_inference_label")
    return {
        "version": 1,
        "passed": not blocking_issues,
        "blocking_issues": list(dict.fromkeys(blocking_issues)),
        "warnings": list(dict.fromkeys(warnings)),
        "retained_count": len(main_items),
        "follow_up_count": len(follow_ups),
        "cognitive_review": cognitive_review,
    }


def apply_verification_results(
    items: list[dict[str, Any]],
    verification_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized_results = [normalize_verification_result(result) for result in verification_results]
    by_id = {
        str(result["item_id"]): result for result in normalized_results if result.get("item_id")
    }
    by_url = {
        str(result["canonical_url"]).strip().lower(): result
        for result in normalized_results
        if result.get("canonical_url")
    }
    title_results = {
        normalize_identity_text(result["title"]): result
        for result in normalized_results
        if result.get("title")
    }
    title_counts: dict[str, int] = {}
    normalized_items = [normalize_item(item) for item in items]
    for item in normalized_items:
        key = normalize_identity_text(item["title"])
        title_counts[key] = title_counts.get(key, 0) + 1
    updated_items: list[dict[str, Any]] = []
    for normalized in normalized_items:
        result = by_id.get(normalized["item_id"])
        if not result and normalized.get("canonical_url"):
            result = by_url.get(normalized["canonical_url"].lower())
        title_key = normalize_identity_text(normalized["title"])
        if not result and title_counts.get(title_key) == 1:
            result = title_results.get(title_key)
        if not result:
            updated_items.append(normalized)
            continue

        merged = dict(normalized)
        verdict = result["verdict"]
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
        remaining_errors = item_validation_errors(merged)
        if remaining_errors:
            merged["_validation_errors"] = remaining_errors
            merged["source_level"] = "线索待证"
            merged["evidence_status"] = "待确认"
        else:
            merged.pop("_validation_errors", None)
        updated_items.append(merged)
    return updated_items


def split_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    main_items: list[dict[str, Any]] = []
    follow_ups: list[str] = []
    for item in items:
        normalized = normalize_item(item)
        if (
            normalized.get("_validation_errors")
            or normalized["source_level"] == "线索待证"
            or normalized["evidence_status"] == "待确认"
        ):
            follow_ups.append(normalized["title"])
            if normalized.get("follow_up"):
                follow_ups.append(str(normalized["follow_up"]))
            continue
        main_items.append(normalized)
        if normalized.get("follow_up"):
            follow_ups.append(str(normalized["follow_up"]))
    return main_items, list(dict.fromkeys(follow_ups))


def choose_item_limit(contract: Contract, explicit_limit: int | None) -> int:
    if explicit_limit is not None:
        if explicit_limit <= 0:
            raise ValueError("item limit must be positive")
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


def render_cognitive_sections(contract: Contract, items: list[dict[str, Any]]) -> str:
    sections: list[str] = []

    if "commentary" in contract.cognitive_features:
        commentary = [
            f"- {item['title']}：{str(item.get('signal_commentary', '')).strip()}"
            for item in items
            if item.get("signal_commentary") and str(item["signal_commentary"]).strip()
        ]
        if commentary:
            sections.extend(["本期信号点评", *commentary[:3]])

    if "sprout" in contract.cognitive_features:
        extensions: list[str] = []
        for item in items:
            raw_extensions = item.get("insight_extensions", [])
            if not isinstance(raw_extensions, list):
                continue
            for extension in raw_extensions:
                if not isinstance(extension, dict):
                    continue
                insight = str(extension.get("insight", "")).strip()
                basis = str(extension.get("basis", "")).strip()
                if insight and basis:
                    extensions.append(
                        f"- {item['title']}：{insight}（依据：{basis}；性质：推断）"
                    )
        if extensions:
            if sections:
                sections.append("")
            sections.extend(["认知延伸", *extensions[:3]])

    if "continuity" in contract.cognitive_features:
        continuity = [
            f"- {item['title']}：{str(item.get('continuity', '')).strip()}"
            for item in items
            if item.get("continuity") and str(item["continuity"]).strip()
        ]
        if continuity:
            if sections:
                sections.append("")
            sections.extend(["下期追踪", *continuity[:5]])

    return "\n".join(sections).strip()


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
    cognitive_sections = render_cognitive_sections(contract, limited_items)
    if cognitive_sections:
        output = output.rstrip() + "\n\n" + cognitive_sections + "\n"
    if contract.inferred_assumptions:
        output = output.rstrip() + "\n\n推断假设\n"
        for assumption in contract.inferred_assumptions:
            output += f"- {assumption}\n"
    return output


def cmd_digest(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items = prepare_items(contract, load_items(Path(args.items_file)))
    if args.verification_results_file:
        verification_results = load_verification_results(Path(args.verification_results_file))
        items = apply_verification_results(items, verification_results)
    print(render_digest(contract, items, args.item_limit))
    return 0


def cmd_prepare(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items = prepare_items(contract, load_items(Path(args.items_file)))
    payload = {
        "version": 1,
        "contract": contract.to_dict(),
        "items": items,
        "acceptance_report": build_acceptance_report(contract, items),
    }
    if args.output_file:
        write_json(Path(args.output_file), items)
        payload["written_to"] = args.output_file
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    contract = build_contract(args)
    items_file = Path(args.items_file)
    items = prepare_items(contract, load_items(items_file))
    artifact_paths = build_artifact_paths(items_file, Path(args.output_file) if args.output_file else None)
    verification_results_file = args.verification_results_file or artifact_paths["verification_results_file"]
    if verification_results_file and Path(verification_results_file).exists():
        verification_results = load_verification_results(Path(verification_results_file))
        items = apply_verification_results(items, verification_results)
    output = render_digest(contract, items, args.item_limit)
    acceptance_report = build_acceptance_report(contract, items, output)
    if not acceptance_report["passed"]:
        raise ValueError(
            "final digest failed acceptance: " + ", ".join(acceptance_report["blocking_issues"])
        )
    output_file = args.output_file or artifact_paths["digest_output_file"]
    payload = {
        "artifact_paths": artifact_paths,
        "verification_results_file_used": verification_results_file if verification_results_file else "",
        "output_file": output_file,
        "rendered": output,
        "acceptance_report": acceptance_report,
    }
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
        payload["written_to"] = output_file
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_verify_results(args: argparse.Namespace) -> int:
    items = normalize_and_deduplicate_items(load_items(Path(args.items_file)))
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
        subparser.add_argument("--cadence", choices=sorted(CADENCES))
        subparser.add_argument("--topic-mix", default="default")
        subparser.add_argument("--depth", choices=["quick", "standard", "analyst"])
        subparser.add_argument("--format", choices=sorted(FORMAT_ALIASES))
        subparser.add_argument("--audience", choices=["personal", "executive", "research", "public"])
        subparser.add_argument("--mode", choices=["full", "standard", "minimal"])
        subparser.add_argument(
            "--cognitive-features",
            help="Comma-separated: interrogate,sprout,commentary,continuity; use off to disable",
        )
        subparser.add_argument("--specialty", default="")
        subparser.add_argument("--specialty-scope", default="")
        subparser.add_argument("--specialty-keywords", default="")
        subparser.add_argument("--specialty-exclusions", default="")
        subparser.add_argument("--specialty-geography", default="")
        subparser.add_argument("--specialty-priority", choices=sorted(SPECIALTY_PRIORITIES), default="")
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

    prepare_parser = subparsers.add_parser(
        "prepare",
        help="Normalize, deduplicate, rank, and retain candidate items",
    )
    add_common(prepare_parser)
    prepare_parser.add_argument("--items-file", required=True)
    prepare_parser.add_argument("--output-file")
    prepare_parser.set_defaults(func=cmd_prepare)

    digest_parser = subparsers.add_parser("digest", help="Render a digest from JSON items")
    add_common(digest_parser)
    digest_parser.add_argument("--items-file", required=True)
    digest_parser.add_argument("--verification-results-file")
    digest_parser.add_argument("--item-limit", type=int)
    digest_parser.set_defaults(func=cmd_digest)

    finalize_parser = subparsers.add_parser("finalize", help="Render and write the final Markdown digest artifact")
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
