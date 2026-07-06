# More News Briefing

一次刷尽近期热点，高效工作一整天  
Scan the day in one pass, from headlines to chatter

[![Version](https://img.shields.io/badge/version-v0.1.2-2f6feb)](#release-notes)
[![License](https://img.shields.io/badge/license-MIT-1f883d)](./LICENSE)
[![Type](https://img.shields.io/badge/type-AI%20Agent%20Skill-8250df)](#项目表头)
[![Language](https://img.shields.io/badge/language-ZH%20%7C%20EN-f59e0b)](#中文说明)

中文入口: [跳转到中文说明](#中文说明)  
English entry: [Jump to English Overview](#english-overview)
Promo illustration pack: [View README promo illustration pack](./assets/readme-xiaohei-scenes/README.md)

## 项目表头

| 字段 | 内容 |
|---|---|
| 名称 | `more-news-briefing` |
| 版本 | `v0.1.2` |
| 类型 | AI Agent Skill / 新闻简报技能 |
| 场景 | 新闻简报 / 日报周报 / 研究跟踪 / 长消息汇总 |
| 关键词 | `news briefing`, `digest`, `AI`, `policy`, `business`, `WeChat`, `Feishu`, `新闻简报`, `日报`, `周报`, `研究跟踪` |

## 中文说明

`more-news-briefing` 是一个独立可运行的新闻简报 skill，用于把分散的时事信息整理成结构稳定、可追溯来源、适合直接交付的多主题资讯摘要。它覆盖从需求归一化、候选信息收集、去重、排序，到最终格式化输出的完整链路，适合一次性简报，也适合持续性日报、周报和专题监测。

### 你为什么会愿意持续用它

很多“新闻摘要”工具解决的是“今天有什么”，但实际工作里更难的是下面几件事同时成立：

- 主题很多，但不能写成东拼西凑的链接堆
- 有专项跟踪需求，但又不想每次从零解释检索口径
- 需要能直接发给同事、老板、客户或群聊，而不是二次手工改写
- 希望高价值事件排在前面，弱证据条目自动降级到继续跟踪

`more-news-briefing` 的设计目标就是把这些高频痛点收束成一个稳定产品动作：先定合同，再出查询，再保留条目，最后按模板成稿。

### 适合谁

- 研究员/分析师：需要把 AI、政策、商业、产业专项放到同一份日报或周报里
- 创始人/投资人/管理者：想在几分钟内看完“今天最重要的三到十件事”
- 媒体、内容和运营团队：需要把素材快速整理成微信、飞书或内部播报可直接发送的格式
- 行业跟踪用户：例如充电桩、储能、V2G、快充、无线充电、超级电容等专题监测

### 3 分钟上手

这个仓库自带一个只依赖 Python 标准库的 runner，能把 skill 最核心的三段闭环跑通：

```bash
python3 scripts/standalone_runner.py contract --specialty "charging / V2G / BESS"
python3 scripts/standalone_runner.py queries --topic-mix default --specialty "charging / V2G / BESS"
python3 scripts/standalone_runner.py digest --items-file items.json --audience executive
```

对应关系很直接：

- `contract`：把模糊需求收敛成可重复执行的 briefing contract
- `queries`：按主题桶生成查询包，而不是临时手写搜索词
- `digest`：把保留条目渲染成可直接交付的简报格式


### 功能概览

- 信息来源更广：不是单一新闻源抓取，而是按“综合媒体 + 垂直媒体 + 官方/一手来源”三层混合取材，更适合做跨主题简报
- 更适合多主题合并：同一轮里可以同时覆盖 AI、政策、商业、文化、体育和用户专项主题，并在输出前统一去重、排序、压缩
- 对高价值信息更友好：当政策、公司公告、平台更新、监管变化这类事件出现时，会优先保留高影响条目，而不是被流量型热点挤掉
- 完全独立可用：这个 skill 自己就能走通“收集-筛选-验证-输出”链路，不依赖其它 skill、插件或外部编排
- 主流程完整内聚：检索扩展、候选合并、优先级排序、事实压缩和最终成稿都在同一套工作流里完成
- 更适合交付而不是试验：内置输入契约、输出模板、验收清单和运行 runbook，适合直接产出日报、周报、研究跟踪或微信/飞书长消息版简报

### 独立运行边界

这个 skill 采用 `standalone-first` 设计：

- 核心能力内置：输入合同归一化、默认查询生成、候选去重、证据分级、模板成稿
- 外部 skill 可选：如果环境里有更强的检索或润色 skill，可以借用它们做增强，但不是主路径
- 不整包复制其它 skill：只把这个 skill 真正必需的方法和最小实现保留在本仓库里，避免跨 skill 代码漂移

如果确实需要“开箱即用”，也支持把少量可选 skill 快照随仓附带到 `references/skills/`。推荐只 vendoring 可选增强器，不 vendoring 整个主流程依赖。

仓库内已经提供一个只依赖 Python 标准库的本地 runner：

- `python3 scripts/standalone_runner.py contract`
- `python3 scripts/standalone_runner.py queries --topic-mix default`
- `python3 scripts/standalone_runner.py digest --items-file items.json`

它不负责替代在线检索，而是把合同、查询规划和最终成稿这些核心流程收回到本 skill 内部。

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

- `full mode`：默认模式，执行完整的收集、排序、验证和成稿流程
- `standard mode`：轻量模式，适合明确要求更快、更省步骤的场景
- `minimal mode`：在检索受限时，优先重组用户已提供材料

### 首次使用交互

第一次使用时，skill 会先帮助用户把主题定清楚，再开始检索。尤其当用户提到“专项主题”但定义仍然偏宽泛时，会优先补全这些信息：

1. 专项主题名称
2. 关注范围，例如技术、政策、企业、项目或市场切片
3. 中英文关键词、缩写、别名
4. 地域范围
5. 重点关注维度，例如政策、产品、安全、招投标、融资或研究
6. 希望排除的相邻主题

### 工作流

1. 使用输入契约归一化用户请求
2. 按主题桶收集候选新闻
3. 对重复事件做合并，并按重要性排序
4. 生成包含概览、重点条目和可选跟踪项的简报
5. 输出为可复用、可继续自动化的稳定格式

### 为什么它更像“可交付产品”而不是“摘要提示词”

从仓库当前实现来看，主流程已经被收拢成一个很清晰的闭环：

- 同一个 `Contract` 结构同时驱动合同归一化、查询生成和最终成稿
- `digest` 会自动区分“正式保留条目”和“继续跟踪条目”，避免把弱证据内容硬塞进正文
- 输出样式不是单一模板，而是面向不同投递场景准备了 `Quick Brief`、`Standard Digest`、`Analyst Watch`、`Long Message Briefing` 和执行层速览
- 外部增强器是可选项，不是隐性依赖，所以它既适合个人临时使用，也适合后续接入自动化

这意味着你不是在买一段 prompt，而是在拿到一个已经有边界、有默认值、有输出约束的 briefing workflow。

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

## 版本说明

### v0.1.2

- 强化 `standalone-first` 设计，明确外部 skill 仅为可选增强器
- 新增 `scripts/standalone_runner.py`，内置合同归一化、查询生成和 digest 成稿
- 新增 `references/local-runner.md`，说明本地 runner 的使用方式
- 调整检索说明，默认主路回到 skill 自带流程

### v0.1.1

- 新增 `SKILL.md` 与 `agents/openai.yaml` 版本号
- 新增中英双语 `README.md`
- 新增 GitHub 风格徽章、关键词索引、快速导航与跳转链接
- 新增标准 MIT `LICENSE`

## 备注

- 当前发布版本为 `v0.1.2`
- 该技能定位为独立可运行的完整新闻简报 skill

---

## English Overview

中文链接: [跳转到中文说明](#中文说明)

`more-news-briefing` is a standalone news-briefing skill built to turn scattered current-affairs information into structured, source-backed, delivery-ready digests. It covers the full path from request normalization and candidate collection to deduplication, prioritization, and final formatting, making it suitable for one-off summaries as well as recurring daily, weekly, or topic-watch briefings.

### Why People Keep Coming Back To It

Most news-summary tools answer "what happened today." Real work usually needs more:

- multiple topics without turning the output into a link dump
- stable specialty monitoring without redefining the search scope every time
- delivery-ready output for chat, leadership updates, or internal distribution
- automatic downgrading of weakly sourced items into a watchlist instead of overstating them

`more-news-briefing` is built around that practical loop: resolve the contract, generate topic-bucket queries, retain the right items, then render a digest that can actually be sent.

### Who It Is For

- researchers and analysts merging AI, policy, business, and specialty monitoring into one briefing
- founders, investors, and managers who want the top three to ten meaningful developments fast
- editorial, content, and ops teams preparing WeChat, Feishu, or internal distribution-ready updates
- domain watchers tracking areas like charging, BESS, V2G, fast charging, wireless charging, or supercapacitors

### Three-Minute Quick Start

The repository includes a standard-library-only runner that proves the core workflow end to end:

```bash
python3 scripts/standalone_runner.py contract --specialty "charging / V2G / BESS"
python3 scripts/standalone_runner.py queries --topic-mix default --specialty "charging / V2G / BESS"
python3 scripts/standalone_runner.py digest --items-file items.json --audience executive
```

Each command owns one durable piece of the product workflow:

- `contract`: turns a vague request into a reusable briefing contract
- `queries`: emits grouped query packs instead of ad hoc search wording
- `digest`: renders retained items into a delivery-ready briefing format

If you want to turn this README into a more promotion-ready landing page, the repo also includes a three-image Xiaohei promo illustration pack with master locks and executable prompts at [assets/readme-xiaohei-scenes/README.md](/Users/Bing/.codex/skills/more-news-briefing/assets/readme-xiaohei-scenes/README.md:1).

### What It Does

- Broader source coverage: it uses a blended source model of general outlets, vertical publications, and official or primary sources instead of relying on a single feed
- Stronger multi-topic synthesis: it can merge AI, policy, business, culture, sports, and user-priority specialty topics into one ranked digest
- Better handling of high-impact signals: policy shifts, company announcements, platform updates, and regulatory moves are intended to outrank low-value noise
- Fully self-contained: it completes the collect-filter-verify-format loop on its own, without relying on companion skills, plugins, or external orchestration
- Tighter workflow ownership: search expansion, candidate merging, prioritization, factual compression, and final briefing output all live inside one cohesive workflow
- Built for delivery, not just exploration: it includes an input contract, output templates, acceptance checks, and runbooks so the result is ready for reporting or chat-based delivery

### Standalone-First Boundary

This skill is designed around a `standalone-first` boundary:

- Core workflow stays local to this repository: contract resolution, query planning, deduplication, evidence labels, and final formatting
- Other skills are optional accelerators, not hidden prerequisites
- We do not bulk-copy whole external skills into this one; we only keep the minimum implementation this skill must own directly

If zero-setup distribution matters, this repository can also ship selected optional skill snapshots under `references/skills/` with a manifest. Those snapshots stay optional and should not take ownership of the core workflow.

The repository now includes a standard-library-only local runner:

- `python3 scripts/standalone_runner.py contract`
- `python3 scripts/standalone_runner.py queries --topic-mix default`
- `python3 scripts/standalone_runner.py digest --items-file items.json`

It does not replace live retrieval. It keeps the skill's core orchestration and output logic self-contained.

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

- `full mode`: default mode; runs the complete collect-rank-verify-write workflow
- `standard mode`: lighter mode for explicitly faster or simpler runs
- `minimal mode`: restructures user-provided material when retrieval is constrained

### First-Use Interaction

On the first use, the skill should resolve the user's topic design before retrieval begins. When a specialty topic is still vague, it should help the user refine:

1. topic name
2. scope
3. Chinese and English keywords or aliases
4. geography
5. watch priorities such as policy, product, safety, financing, or bids
6. exclusions

### Workflow

1. Normalize the request with the input contract
2. Collect candidate stories across topic buckets
3. Deduplicate and rank by consequence, recency, attention, relevance, and novelty
4. Write a layered digest with summary, ranked items, and optional watchlist
5. Prepare the result in a stable format for repeated use

### Why This Feels Like A Product, Not A Prompt

The current implementation already concentrates the workflow into a durable core:

- the same `Contract` structure drives normalization, query generation, and digest rendering
- weakly sourced or unresolved items are separated from the main body instead of being overstated
- output is shaped for multiple delivery contexts, from quick skim to analyst watch to chat-ready long message
- external enhancers stay optional, which keeps the workflow portable and easier to automate later

That makes this repository more useful than a one-off summarization prompt. It gives you a bounded, repeatable briefing system.

### Output Styles

- `Quick Brief`: short mobile-friendly summary
- `Standard Digest`: balanced daily or weekly roundup
- `Analyst Watch`: research-heavy monitoring format
- `Long Message Briefing`: chat-friendly format for WeChat or Feishu

## Release Notes

### v0.1.2

- Clarified the `standalone-first` design so companion skills are optional only
- Added `scripts/standalone_runner.py` for contract resolution, query planning, and digest rendering
- Added `references/local-runner.md` for local runner usage
- Repositioned retrieval guidance so the built-in workflow remains the default route

### v0.1.1

- Added version metadata to `SKILL.md` and `agents/openai.yaml`
- Added a bilingual `README.md`
- Added GitHub-style badges, keyword indexing, quick navigation, and anchor links
- Added a standard MIT `LICENSE`

## Notes

- The current repository release is `v0.1.2`
- This skill is designed as a complete standalone news-briefing workflow
