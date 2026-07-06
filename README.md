# More News Briefing

[![Version](https://img.shields.io/badge/version-v0.1.1-2f6feb)](#release-notes)
[![License](https://img.shields.io/badge/license-MIT-1f883d)](./LICENSE)
[![Type](https://img.shields.io/badge/type-AI%20Agent%20Skill-8250df)](#项目表头)
[![Language](https://img.shields.io/badge/language-ZH%20%7C%20EN-f59e0b)](#中文说明)
[![Status](https://img.shields.io/badge/status-active-16a34a)](#备注)


中文入口: [跳转到中文说明](#中文说明)  
English entry: [Jump to English Overview](#english-overview)

## 项目表头

| 字段 | 内容 |
|---|---|
| 名称 | `more-news-briefing` |
| 版本 | `v0.1.1` |
| 类型 | AI Agent Skill / 新闻简报技能 |
| 场景 | 新闻简报 / 日报周报 / 研究跟踪 / 长消息汇总 |
| 关键词 | `news briefing`, `digest`, `AI`, `policy`, `business`, `WeChat`, `Feishu`, `新闻简报`, `日报`, `周报`, `研究跟踪` |

## 中文说明

English link: [Jump to English Overview](#english-overview)

`more-news-briefing` 是一个独立可运行的新闻简报 skill，用于把分散的时事信息整理成结构稳定、可追溯来源、适合直接交付的多主题资讯摘要。它覆盖从需求归一化、候选信息收集、去重、排序，到最终格式化输出的完整链路，适合一次性简报，也适合持续性日报、周报和专题监测。

### 功能概览

- 信息来源更广：不是单一新闻源抓取，而是按“综合媒体 + 垂直媒体 + 官方/一手来源”三层混合取材，更适合做跨主题简报
- 更适合多主题合并：同一轮里可以同时覆盖 AI、政策、商业、文化、体育和用户专项主题，并在输出前统一去重、排序、压缩
- 对高价值信息更友好：当政策、公司公告、平台更新、监管变化这类事件出现时，会优先保留高影响条目，而不是被流量型热点挤掉
- 完全独立可用：这个 skill 自己就能走通“收集-筛选-验证-输出”链路，不依赖其它 skill、插件或外部编排
- 主流程完整内聚：检索扩展、候选合并、优先级排序、事实压缩和最终成稿都在同一套工作流里完成
- 更适合交付而不是试验：内置输入契约、输出模板、验收清单和运行 runbook，适合直接产出日报、周报、研究跟踪或微信/飞书长消息版简报

### 为什么是这个 Skill

很多资讯工具擅长“搜链接”，也有很多工具擅长“润色文案”，但真正难的是把多来源、跨主题、彼此重复的时事信息压缩成一个有排序、有判断、能直接发出去的简报。`more-news-briefing` 的价值就在这里。

它不是把搜索结果简单堆起来，也不是把已有材料机械改写，而是把“信息收集、去重、判断优先级、压缩表达、稳定交付”串成一条完整工作流，更适合长期做日报、周报和专题跟踪。

### 设计原则

- 先保证信息覆盖面，再追求措辞润色
- 先做优先级排序，再开始写摘要
- 先去重合并，再组织叙述
- 输出要能直接交付，而不是停留在研究笔记
- 工作流必须独立完整，不能依赖隐性外部能力
- 输出结构要稳定，方便重复执行和后续自动化

### 默认主题

当用户未指定主题时，默认覆盖以下内容：

1. AI 与科技
2. 政治与政策
3. 商业与市场
4. 文化与社会
5. 体育
6. 用户重点关注的专项主题

### 工作模式

- `standard mode`：默认模式，生成平衡型新闻简报
- `full mode`：执行完整的收集、排序、验证和成稿流程
- `minimal mode`：在检索受限时，优先重组用户已提供材料

### 工作流

1. 使用输入契约归一化用户请求
2. 按主题桶收集候选新闻
3. 对重复事件做合并，并按重要性排序
4. 生成包含概览、重点条目和可选跟踪项的简报
5. 输出为可复用、可继续自动化的稳定格式

### 输出形式

- `Quick Brief`：适合手机快速浏览的短简报
- `Standard Digest`：适合日报/周报的标准摘要
- `Analyst Watch`：适合研究型监测的分析视图
- `Long Message Briefing`：适合微信或飞书长消息投递

### 典型用法

- “做个今日新闻简报”
- “按 AI、政策、商业三个主题做周报”
- “帮我整理成适合微信发送的长消息版资讯汇总”
- “把我给你的素材整理成带来源的简报”

## 仓库结构

```text
more-news-briefing/
├── SKILL.md
├── README.md
├── LICENSE
├── agents/
│   └── openai.yaml
└── references/
    ├── acceptance-checklist.md
    ├── anysearch-adapter-runbook.md
    ├── demo-runbook.md
    ├── editorial-rubric.md
    ├── embedded-enhancements.md
    ├── input-contract.md
    ├── output-templates.md
    ├── query-playbook.md
    ├── retrieval-adapters.md
    ├── source-ladder.md
    └── standalone-operation.md
```

## 关键参考文件

- [SKILL.md](./SKILL.md)：主技能定义
- [references/input-contract.md](./references/input-contract.md)：输入归一化契约
- [references/demo-runbook.md](./references/demo-runbook.md)：演示执行路径
- [references/output-templates.md](./references/output-templates.md)：输出模板
- [references/acceptance-checklist.md](./references/acceptance-checklist.md)：交付检查清单

## 版本说明

### v0.1.1

- 新增 `SKILL.md` 与 `agents/openai.yaml` 版本号
- 新增中英双语 `README.md`
- 新增 GitHub 风格徽章、关键词索引、快速导航与跳转链接
- 新增标准 MIT `LICENSE`

## 备注

- 当前发布版本为 `v0.1.1`
- 该技能定位为独立可运行的完整新闻简报 skill

---

## English Overview

中文链接: [跳转到中文说明](#中文说明)

`more-news-briefing` is a standalone news-briefing skill built to turn scattered current-affairs information into structured, source-backed, delivery-ready digests. It covers the full path from request normalization and candidate collection to deduplication, prioritization, and final formatting, making it suitable for one-off summaries as well as recurring daily, weekly, or topic-watch briefings.

### What It Does

- Broader source coverage: it uses a blended source model of general outlets, vertical publications, and official or primary sources instead of relying on a single feed
- Stronger multi-topic synthesis: it can merge AI, policy, business, culture, sports, and user-priority specialty topics into one ranked digest
- Better handling of high-impact signals: policy shifts, company announcements, platform updates, and regulatory moves are intended to outrank low-value noise
- Fully self-contained: it completes the collect-filter-verify-format loop on its own, without relying on companion skills, plugins, or external orchestration
- Tighter workflow ownership: search expansion, candidate merging, prioritization, factual compression, and final briefing output all live inside one cohesive workflow
- Built for delivery, not just exploration: it includes an input contract, output templates, acceptance checks, and runbooks so the result is ready for reporting or chat-based delivery

### Why This Skill

Many news tools are good at collecting links, and many writing tools are good at polishing prose. The harder job is turning overlapping, cross-topic, multi-source current-affairs input into a ranked, readable briefing that can actually be delivered. That is the core value of `more-news-briefing`.

It is not a raw search-result dump, and it is not a mechanical rewrite layer. It is a complete workflow that connects collection, deduplication, prioritization, compression, and stable delivery into one reusable briefing system.

### Design Principles

- Source breadth before summary polish
- Ranking before writing
- Deduplication before narration
- Delivery-ready structure over raw research notes
- Standalone workflow over hidden dependencies
- Stable output shape for repeated use

### Default Topic Mix

If the user does not specify topics, the skill defaults to:

1. AI and technology
2. Politics and policy
3. Business and markets
4. Culture and society
5. Sports
6. User-priority specialty topics

### Operating Modes

- `standard mode`: default mode for a balanced digest
- `full mode`: runs the complete collect-rank-verify-write workflow
- `minimal mode`: restructures user-provided material when retrieval is constrained

### Workflow

1. Normalize the request with the input contract
2. Collect candidate stories across topic buckets
3. Deduplicate and rank by consequence, recency, attention, relevance, and novelty
4. Write a layered digest with summary, ranked items, and optional watchlist
5. Prepare the result in a stable format for repeated use

### Output Styles

- `Quick Brief`: short mobile-friendly summary
- `Standard Digest`: balanced daily or weekly roundup
- `Analyst Watch`: research-heavy monitoring format
- `Long Message Briefing`: chat-friendly format for WeChat or Feishu

## Repository Structure

```text
more-news-briefing/
├── SKILL.md
├── README.md
├── LICENSE
├── agents/
│   └── openai.yaml
└── references/
    ├── acceptance-checklist.md
    ├── anysearch-adapter-runbook.md
    ├── demo-runbook.md
    ├── editorial-rubric.md
    ├── embedded-enhancements.md
    ├── input-contract.md
    ├── output-templates.md
    ├── query-playbook.md
    ├── retrieval-adapters.md
    ├── source-ladder.md
    └── standalone-operation.md
```

## Key References

- [SKILL.md](./SKILL.md): Main skill definition
- [references/input-contract.md](./references/input-contract.md): Request normalization contract
- [references/demo-runbook.md](./references/demo-runbook.md): Concrete execution path
- [references/output-templates.md](./references/output-templates.md): Reusable digest layouts
- [references/acceptance-checklist.md](./references/acceptance-checklist.md): Final quality checklist

## Release Notes

### v0.1.1

- Added version metadata to `SKILL.md` and `agents/openai.yaml`
- Added a bilingual `README.md`
- Added GitHub-style badges, keyword indexing, quick navigation, and anchor links
- Added a standard MIT `LICENSE`

## Notes

- The current repository release is `v0.1.1`
- This skill is designed as a complete standalone news-briefing workflow
