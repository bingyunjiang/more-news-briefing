# Topic Enums

Use this reference as the single source of truth for topic-selection menus in `more-news-briefing`.

Keep the topic choices split into two layers:

1. `default topic enums`: broad recurring buckets suitable for general briefings
2. `specialty topic enums`: domain-heavy watch topics that usually need narrower follow-up

When updating topic menus, change this file first, then keep other references aligned to these labels.

## Default topic enums

Use these as the first-layer choices for broad or mixed briefings:

1. `A. AI 与科技`
2. `B. 政策与监管`
3. `C. 商业与市场`
4. `D. 文化与社会`
5. `E. 教育与体育`

These buckets are intended to be stable and broadly understandable. Avoid overloading them with niche industrial terms.

Rendered menu block:

```text
A. AI 与科技
B. 政策与监管
C. 商业与市场
D. 文化与社会
E. 教育与体育
```

## Specialty topic enums

Use these as the second-layer choices when the user wants domain-specific monitoring:

1. `F. 能源与电力`
2. `G. 汽车与出行`
3. `H. 先进制造`
4. `I. 半导体与电子`
5. `J. AI 与机器人`
6. `K. 仿真与数字孪生`
7. `L. 散热与热管理`
8. `M. 试验方法与测试验证`
9. `N. 其他专项主题`

If `N. 其他专项主题` is selected, follow up by narrowing the topic with the onboarding template before retrieval.

Rendered menu block:

```text
F. 能源与电力
G. 汽车与出行
H. 先进制造
I. 半导体与电子
J. AI 与机器人
K. 仿真与数字孪生
L. 散热与热管理
M. 试验方法与测试验证
N. 其他专项主题
```

## Specialty subtopic enums

Use these as the third-layer narrowing menu after the user selects a broad specialty topic.

### `F. 能源与电力`

```text
A. 储能
B. 充电 / 快充
C. V2G / 车网互动
D. EMS / 能源管理
E. 电力市场
F. 电网 / 新型电力系统
G. 电力电子 / 逆变器
H. SiC / GaN
```

### `G. 汽车与出行`

```text
A. 新能源汽车
B. 智能驾驶
C. 车载电子
D. 补能网络
E. 商用车 / 重卡
F. 出海与供应链
```

### `H. 先进制造`

```text
A. 工业自动化
B. 智能制造
C. 产线装备
D. 材料与工艺
E. 质量与可靠性
```

### `I. 半导体与电子`

```text
A. 功率半导体
B. 模拟 / 电源芯片
C. 封装与热设计
D. 器件制造
E. 供应链与产能
```

### `J. AI 与机器人`

```text
A. 大模型技术
B. AI Agent / 工具链
C. 机器人 / 具身智能
D. 视觉与感知
E. 开源模型与社区
```

### `K. 仿真与数字孪生`

```text
A. 多物理场仿真
B. 电磁 / 热 / 结构仿真
C. 系统级仿真
D. 数字孪生平台
E. 实时仿真 / HIL
```

### `L. 散热与热管理`

```text
A. 液冷
B. 风冷
C. 热界面材料
D. 热设计与热仿真
E. 电池热管理
F. 功率器件散热
```

### `M. 试验方法与测试验证`

```text
A. 测试标准
B. 试验方法
C. 可靠性验证
D. 安全测试
E. 台架 / HIL / 实验平台
F. 标定与测量方法
```

## Specialty priority enums

Use these when the user selected a specialty topic and you need to narrow the watch angle:

1. `A. 技术路线`
2. `B. 政策标准`
3. `C. 企业动态`
4. `D. 项目落地 / 招投标`
5. `E. 市场 / 融资`
6. `F. 安全 / 事故`
7. `G. 学术 / 研究`

Rendered menu block:

```text
A. 技术路线
B. 政策标准
C. 企业动态
D. 项目落地 / 招投标
E. 市场 / 融资
F. 安全 / 事故
G. 学术 / 研究
```

## Geography enums

Use these when the topic needs a regional boundary:

1. `A. 中国`
2. `B. 美国`
3. `C. 欧洲`
4. `D. 全球`
5. `E. 其他地区`

Rendered menu block:

```text
A. 中国
B. 美国
C. 欧洲
D. 全球
E. 其他地区
```

## Maintenance rule

If a new topic is likely to be used as a default recurring bucket, place it under `default topic enums`.

If a new topic usually requires follow-up on scope, keywords, companies, or applications, place it under `specialty topic enums`.
