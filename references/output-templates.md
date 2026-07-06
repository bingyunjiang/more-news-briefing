# Output Templates

Use these templates to keep briefing output consistent across one-off runs and recurring workflows.

## Evidence tags

Use these two fields by default on retained top items when the digest is source-backed:

1. `来源级别`:
   `首选证据` / `次选证据` / `线索待证`
2. `证据状态`:
   `已确认` / `交叉验证中` / `待确认`

Use `线索待证` instead of `仅作线索` inside the final digest to keep the label short and readable.

If an item is labeled `线索待证` or `待确认`, it should usually move to `继续跟踪` instead of staying in the main ranked block.

## Template 1: Short briefing

Use for fast reading, chat delivery, or a compact daily skim.

```text
简报时间：2026-07-03

今日概览
[2-4句总览，直接说最重要的变化，不要铺垫]

重点新闻
1. [标题]
发生了什么：[一句话]
为什么重要：[一句话]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]

2. [标题]
发生了什么：[一句话]
为什么重要：[一句话]
来源级别：[次选证据]
证据状态：[交叉验证中]
来源：[媒体A]、[媒体B]

3. [标题]
发生了什么：[一句话]
为什么重要：[一句话]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]
```

## Template 2: Standard digest

Use for the default broad news digest.

```text
简报时间：2026-07-03
覆盖范围：AI、政治、商业、文化、体育、专项关注

今日概览
[2-4句总览]

重点新闻
1. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]

2. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[次选证据]
证据状态：[交叉验证中]
来源：[媒体A]、[媒体B]

分主题速览

AI与科技
- [标题]：[一句话]
- [标题]：[一句话]

政治与政策
- [标题]：[一句话]
- [标题]：[一句话]

商业与市场
- [标题]：[一句话]

文化与社会
- [标题]：[一句话]

体育
- [标题]：[一句话]

专项关注
- [标题]：[一句话]

继续跟踪
- [正在发酵但还不稳定的主题]
- [需要下一个周期继续确认的主题]
```

## Template 3: Analyst watch

Use for monitoring-oriented output where the reader cares about signals and open questions.

```text
观察窗口：过去24小时

核心判断
[2-4句，概括最值得注意的变化]

高优先级项目
1. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[首选证据]
证据状态：[已确认]
需要确认：[1句，可选]
来源：[媒体A]、[媒体B]

2. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[次选证据]
证据状态：[交叉验证中]
需要确认：[1句，可选]
来源：[媒体A]、[媒体B]

主题观察
AI与科技
- [信号]

政治与政策
- [信号]

商业与市场
- [信号]

继续跟踪
- [事件]
- [事件]
```

## Template 4: Source-attributed format

Use when the user explicitly asks for links, attribution, or auditability, or when a fuller source line than the default is needed.

```text
重点新闻
1. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]、[官方来源]
```

## Template 5: WeChat / Feishu long message

Use when the digest will be sent as a single Chinese long message in WeChat, Feishu, or similar chat tools.

Default variant: `信息密度高版`

```text
今日热点简报 | 2026-07-03

今日概览
[用2-4句概括今天最重要的变化。先说结论，再说变化方向，不要写空泛开场。]

重点新闻
1. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]、[官方来源]

2. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[次选证据]
证据状态：[交叉验证中]
来源：[媒体A]、[媒体B]、[官方来源]

3. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]、[官方来源]

分主题速览

AI与科技
- [标题]：[一句话]
- [标题]：[一句话]

政治与政策
- [标题]：[一句话]
- [标题]：[一句话]

商业与市场
- [标题]：[一句话]
- [标题]：[一句话]

文化与社会
- [标题]：[一句话]

体育
- [标题]：[一句话]

专项关注
- [标题]：[一句话]

继续跟踪
- [仍在发酵、适合下个周期继续观察的主题]
- [仍需更多信息确认的主题]
```

### Long message editing notes

1. Title line should stay short enough to preview well in chat lists
2. Leave one blank line between major sections
3. Do not use more than two consecutive multi-sentence items
4. Keep `分主题速览` tighter than `重点新闻`
5. End cleanly after `继续跟踪`; do not add polite filler or generic outlook text

## Template 6: WeChat / Feishu long message - 信息密度高版

Use as the default long-message format when the user does not specify a style.

```text
今日热点简报 | 2026-07-03

今日概览
[2-4句。直接说今天最重要的变化与方向。]

重点新闻
1. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]、[官方来源]

2. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[次选证据]
证据状态：[交叉验证中]
来源：[媒体A]、[媒体B]、[官方来源]

3. [标题]
发生了什么：[1-2句]
为什么重要：[1句]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]、[官方来源]

分主题速览

AI与科技
- [标题]：[一句话]
- [标题]：[一句话]

政治与政策
- [标题]：[一句话]
- [标题]：[一句话]

商业与市场
- [标题]：[一句话]
- [标题]：[一句话]

文化与社会
- [标题]：[一句话]

体育
- [标题]：[一句话]

专项关注
- [标题]：[一句话]

继续跟踪
- [仍在发酵、适合下个周期继续观察的主题]
- [仍需更多信息确认的主题]
```

### 信息密度高版规则

1. 默认覆盖尽可能多的主题面
2. `重点新闻` 放结论最强的 3 条
3. `分主题速览` 负责补足广度
4. 每条尽量压缩到 1 到 3 行
5. 适合熟悉资讯阅读节奏的读者
6. 默认保留来源行，满足证据链要求

## Template 7: WeChat / Feishu long message - 领导速览版

Use when the reader wants a faster executive scan with fewer items and stronger prioritization.

```text
今日热点速览 | 2026-07-03

一句话判断
[用1-2句先说今天最值得关注的变化]

最重要的三件事
1. [标题]
发生了什么：[1句]
影响判断：[1句]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]

2. [标题]
发生了什么：[1句]
影响判断：[1句]
来源级别：[次选证据]
证据状态：[交叉验证中]
来源：[媒体A]、[媒体B]

3. [标题]
发生了什么：[1句]
影响判断：[1句]
来源级别：[首选证据]
证据状态：[已确认]
来源：[媒体A]、[媒体B]

其他值得看
- AI与科技：[一句话]
- 政策与政治：[一句话]
- 市场与商业：[一句话]
- 文化/体育：[一句话]

继续跟踪
- [主题]
```

### 领导速览版规则

1. 优先压缩长度，不追求全覆盖
2. 优先给判断，不展开过多背景
3. 主体内容控制在手机一屏到数屏之间
4. 只保留最需要被转述或决策者知道的信息
5. 默认仍保留来源行；只有用户明确要求极简版时才去掉

## Editing rules

1. Keep titles factual, not clickbait
2. Use the same field order throughout the digest
3. Keep "为什么重要" shorter than "发生了什么"
4. Put source lines last
5. Put `来源级别` and `证据状态` before `来源`
6. Remove empty sections instead of leaving placeholders
7. Default to source-included output for evidence traceability
