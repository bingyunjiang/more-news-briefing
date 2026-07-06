# README Promo Illustration Pack

这个目录保存 `more-news-briefing` 的 README 宣传配图方案。

由于当前执行环境禁止把仓库语义和 API key 发送到第三方生图端点，这一版先交付：

- 3 张宣传配图的 shot list
- 每张图的母版锁定记录
- 可直接用于生图的 prompt
- 建议插入 README 的位置

如果后续在你自己的可信环境中生图，建议输出到本目录：

- `01-briefing-funnel.png`
- `02-standalone-first.png`
- `03-evidence-filter.png`

## 图 1：信息收拢成简报

用途：
放在 README 中文说明开头，用来表达“多源热点很散，但这个 skill 会把它们收成一份可直接发的 briefing”。

建议插入位置：
`README.md` 中文 `3 分钟上手` 之前。

母版：
`assets/examples/02-message-overload.png`

抽取的不变量：

- 大面积纯白留白
- 一个主物件承担“信息出口/入口”的作用
- 小黑承担收拢或阻挡动作
- 标签少而准
- 真实物件摄影感统一

当前内容的变异点：

- 主物件改为透明亚克力收件盒或白色 briefing 文件夹，不再使用黑色手机
- 纸条从左右上方汇入，而不是从左侧单向涌出
- 小黑改为跪地整理和推进 retained slips，而不是举盾抵挡
- 去掉沙漏，只保留一个轻量 binder clip
- 标签围绕“收拢成一份”展开，而不是消息催促语境

画面 3 秒读懂句：
很多热点本来四散飞来，但现在被收进一份可直接发送的简报。

短标签：

- `热点太散`
- `收成一份`
- `可直接发`

文件名：
`01-briefing-funnel.png`

## 图 2：主流程留在技能内部

用途：
放在 `独立运行边界` 或 `为什么它更像可交付产品` 附近，表达“外部增强器可以有，但主流程不能外包”。

建议插入位置：
`README.md` 中文 `独立运行边界` 后。

母版：
`assets/examples/05-ai-automation-badge.png`

抽取的不变量：

- 横向铺开的身份/标签物件
- 小黑与“被重新命名/被改标签”的动作拉扯
- 留白充足
- 配件极少
- 标签位置开放，不要像信息图

当前内容的变异点：

- 工牌语义改为 `standalone-first` 产品卡片
- 右侧改成更高一点的 label-maker/tagging gun，而不是复刻同款胶带器关系
- 小黑改成撑住卡框下角，不是从远处拉挂绳
- 挂绳斜穿到卡片背后，形成新的力学关系
- 标签改成 “主流程在这 / 可选增强 / 别外包”

画面 3 秒读懂句：
外部工具可以增强，但主流程必须留在这个 skill 自己手里。

短标签：

- `主流程在这`
- `可选增强`
- `别外包`

文件名：
`02-standalone-first.png`

## 图 3：先验真，再进正文

用途：
放在 `为什么它更像“可交付产品”` 或 `工作流` 后，表达“弱证据先过滤，正式保留条目才进入 digest 正文”。

建议插入位置：
`README.md` 中文 `为什么它更像“可交付产品”而不是“摘要提示词”` 后。

母版：
`assets/examples/06-ai-resume-filter.png`

抽取的不变量：

- 一个过滤工具承担主要冲突
- 小黑必须接触被筛的卡片
- 白色背景空气感强
- 中文短标签稀疏
- 真实物件像同一摄影棚里的小现场

当前内容的变异点：

- 筛选对象从简历改为 news items / retained items
- 滤器斜向导向右侧的小托盘或 verified stack，不再是中置筛子压在纸堆上
- 小黑改为右侧接住保留条目，而不是下方往上推
- 底部只保留一张 faint low-confidence slip 暗示 follow-up
- 标签改成“先验真 / 正式保留 / 继续跟踪”

画面 3 秒读懂句：
不是每条热点都进简报，只有验证过、值得保留的项目才留在正文。

短标签：

- `先验真`
- `正式保留`
- `继续跟踪`

文件名：
`03-evidence-filter.png`

## 可执行 Prompt

完整批量 prompt 已保存到：

- [`tmp/imagegen/readme-promo-prompts.jsonl`](/Users/Bing/.codex/skills/more-news-briefing/tmp/imagegen/readme-promo-prompts.jsonl:1)

如果你在自己的可信环境中执行，可以直接复用该文件。
