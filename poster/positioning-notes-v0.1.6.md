# more-news-briefing v0.1.6 推广定位底稿

更新日期：2026-07-26

## 结论

推广时不应把“聚合、摘要、去重、多视角、专题追踪”描述为本 Skill 独有。当前主流产品已分别覆盖这些能力。

`more-news-briefing` 更可信的差异化定位是：把新闻检索之后的编辑判断、证据边界、认知延伸、验收阻断和跨期连续性，做成同一条可重复、可检查、可移植的交付工作流。

## 当前产品范式

| 产品范式 | 官方资料显示的典型能力 | 对本 Skill 定位的影响 |
|---|---|---|
| 聚合与个性化 | Google News 按语言、地域、兴趣、来源与历史活动选择和个性化内容，并提供 briefing、Full Coverage 等入口 | 不宣传“个性化聚合”独占 |
| 多视角比较 | Ground News 把同一事件的不同来源合并，展示政治倾向、事实性、所有权、地域与时间，并生成跨来源摘要 | 不宣传“多来源合并/多视角”独占 |
| AI 摘要与问答 | Particle 提供多种摘要视图、故事问答、观点比较、实体关注、时间线与来源链接 | 不宣传“AI 摘要/解释/追踪”独占 |
| 情报监测与去重 | Feedly AI 支持主题、公司和趋势追踪、优先级排序、AI Feeds、跨来源内容去重，以及面向交付和集成的情报流程 | 不宣传“专题监测/去重/交付”独占 |

## 应强调的组合差异

1. `为什么重要` 是每条重点新闻的固定字段：不仅复述事件，还明确其影响对象、后果与当前相关性。
2. `本期点评` 是跨条目的编辑综合：压缩成少量有区分度的周期信号，而不是逐条泛泛评论。
3. `认知延伸` 只从已保留、证据充分的条目生成；每条延伸必须写明依据并标注 `性质：推断`。
4. `继续跟踪` 不只是收藏或关注：弱证据事件、未决问题、实体、指标和时间范围被转成下一周期的具体检查任务。
5. `证据边界` 显式存在：正文条目带 `来源级别` 与 `证据状态`；待确认内容通常转入继续跟踪。
6. `验收门` 会检查单来源高影响条目、无依据因果、未查反证和字段缺失；阻断项会阻止正式 Markdown 产物写出。
7. `跨期连续性` 可导出为用户可见的 JSON 文件，由调用方、上期简报、watchlist 或自动化显式传递，不依赖隐藏用户记忆。
8. `交付闭环` 固定为：`collect -> normalize/deduplicate -> rank/retain -> verify -> render -> cognition -> acceptance -> polish`。

因此，推广主张应是：

> 差异不在多一个摘要功能，而在把“为什么重要—本期点评—认知延伸—继续跟踪—验收交付”串成有证据边界的同一条工作流。

## 官方对标来源

- Google News Help, “How Google News stories are selected”: <https://support.google.com/googlenews/answer/9005749?hl=en>
- Ground News FAQ: <https://ground.news/frequently-asked-questions>
- Particle, “Introducing Particle: The news, organized”: <https://particle.news/blog/introducing-particle-the-news-organized>
- Feedly AI: <https://feedly.com/ai>
- Feedly Documentation, “How to create AI Feeds”: <https://docs.feedly.com/article/807-how-to-create-ai-feeds>
- Feedly Documentation, “How does Deduplication work?”: <https://docs.feedly.com/article/218-how-does-deduplication-work>

## 仓库实现依据

- `SKILL.md`
- `references/cognitive-enhancements.md`
- `references/output-templates.md`
- `references/acceptance-checklist.md`
- `references/editorial-rubric.md`
- `scripts/standalone_runner.py`
