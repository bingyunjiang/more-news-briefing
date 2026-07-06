# Onboarding Template

Use this reference when the user is using `more-news-briefing` for the first time, or when they introduce a new specialty topic that is still too vague for stable retrieval.

Prefer multiple-choice interaction over free-form writing. Ask the user to choose first, and only request typed details when the specialty topic is still too broad after selection.

Read [topic-enums.md](./topic-enums.md) before presenting topic menus. Treat its `default topic enums` and `specialty topic enums` as the canonical menu source.
Read [source-family-catalog.md](./source-family-catalog.md) when the user wants a repeatable specialty briefing and you need to resolve source-role preference or recurring watchlists.

When writing the onboarding message, do not hand-maintain the topic menu inside this file. Render the menu by copying the current `Rendered menu block` sections from `topic-enums.md`.

## Default first-use prompt

Use this default Chinese prompt skeleton for first-use onboarding. Replace the placeholders with the current rendered menu blocks from [topic-enums.md](./topic-enums.md):

```text
先把这版简报的主题定一下，我再开始检索。你尽量按选项回复就行：

1. 这次要哪种简报？
A. 综合热点
B. 固定几个主题
C. 一个专项主题持续跟踪

2. 你最想看的主题是哪些？
{default topic enums rendered menu block}
{specialty topic enums rendered menu block}

3. 如果你选了专项主题，再补一层更细的子方向。
例如：
- 能源与电力 -> 储能 / 充电 / V2G / EMS / 电力市场 / 电力电子 / SiC / GaN
- AI 与机器人 -> 大模型技术 / Agent / 机器人 / 开源社区
- 仿真与数字孪生 -> 多物理场仿真 / 数字孪生 / HIL
- 散热与热管理 -> 液冷 / 风冷 / 电池热管理 / 功率器件散热
- 试验方法与测试验证 -> 测试标准 / 试验方法 / 可靠性验证 / 安全测试

子方向一旦确定，回到 [source-family-catalog.md](./source-family-catalog.md) 里的 `Subtopic routing` 选择对应的 source family 组合。

4. 再选一下关注重点：
{specialty priority enums rendered menu block}

5. 再选一下地域范围：
{geography enums rendered menu block}

6. 如果你希望后面每次都更贴近你的口味，再选一下信息源风格：
A. 偏热点
B. 偏官方
C. 偏社区
D. 偏产业
E. 平衡默认

7. 如果你想定观察名单，再选一下要不要带：
A. 公司 / 项目名单
B. 机构 / 标准组织名单
C. 社区 / 仓库 / 论坛名单
D. 这次先不定

8. 如果有想排除的内容，再补一句就行。

9. 如果后面需要登录某些高价值信息源，我会提醒你登录，再继续抓取。

你可以直接回复类似：
“1B，2A+F+J，3储能+大模型技术，4B+D+F，5A+C，6B+D，7A+B，不看纯乘用车销量。”
```

Map source-style selections with [source-family-catalog.md](./source-family-catalog.md):

1. `A. 偏热点` -> hotlists, rankings, realtime streams
2. `B. 偏官方` -> official institutions, direct-reporting outlets
3. `C. 偏社区` -> HN, GitHub, Reddit, practitioner communities
4. `D. 偏产业` -> trade media, channelized subfeeds, industrial watch sources
5. `E. 平衡默认` -> one discovery family plus one verification family

## Specialty-topic follow-up prompt

If the user gave a specialty label that is still too broad, use this shorter follow-up instead of starting retrieval immediately. Replace the placeholders with the current rendered blocks from [topic-enums.md](./topic-enums.md):

```text
我先帮你把“专项主题”收紧一下，不然后面会混入太多无关信息。

我理解你现在想跟踪的是：
- 主题：{specialty_label}

你直接选就行：
1. 更细想看哪个子方向？
A. 限定到某个技术子方向
B. 限定到某个政策或市场子方向
C. 限定到某类公司 / 项目
D. 先保持当前大类

2. 更想看哪一层？
{specialty priority enums rendered menu block}

3. 主要看哪些地区？
{geography enums rendered menu block}

4. 下面哪种收口方式更适合？
A. 限定几个核心关键词
B. 限定几家公司 / 机构
C. 限定技术路线
D. 限定应用场景
E. 没问题，按当前范围就行

如果你方便，我也可以按这个版本先定：
“{candidate_specialty_formulation}”
你回复“按这个来”我就直接开始；如果有排除项，再补一句就够了。
```

If a chosen route depends on an account-gated source, use a short prompt like:

```text
这个主题有一个高价值信息源需要登录后才能继续抓，我建议用它，因为它能提供更完整的 {policy / filing / project / research / community} 信息。

你先登录一下，登录好后告诉我，我就继续往下抓；在这之前我会先用公开来源把其他部分跑起来。
```

## Normalized intake note

After the user answers, rewrite the result into this stable internal structure before retrieval:

```text
briefing_shape:
primary_topics:
specialty_label:
specialty_scope:
specialty_keywords:
specialty_geography:
specialty_priority:
specialty_exclusions:
source_roles:
company_watchlist:
institution_watchlist:
community_watchlist:
```

Do not show this normalized block unless it helps the user confirm assumptions quickly.

## Maintenance note

When changing the topic menu, update [topic-enums.md](./topic-enums.md) first. Keep this template synchronized to that file rather than inventing new labels locally.
