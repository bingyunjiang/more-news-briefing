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


def load_items(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("items file must contain a JSON array")
    return data


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
    print(render_digest(contract, items, args.item_limit))
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

    digest_parser = subparsers.add_parser("digest", help="Render a digest from JSON items")
    add_common(digest_parser)
    digest_parser.add_argument("--items-file", required=True)
    digest_parser.add_argument("--item-limit", type=int)
    digest_parser.set_defaults(func=cmd_digest)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
