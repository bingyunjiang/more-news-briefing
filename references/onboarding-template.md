# Onboarding Template

Use this reference when the user is using `more-news-briefing` for the first time, or when they introduce a new specialty topic that is still too vague for stable retrieval.

Prefer multiple-choice interaction over free-form writing. Ask the user to choose first, and only request typed details when the specialty topic is still too broad after selection.

## Default first-use prompt

Use this default Chinese prompt for first-use onboarding:

```text
先把这版简报的主题定一下，我再开始检索。你尽量按选项回复就行：

1. 这次要哪种简报？
A. 综合热点
B. 固定几个主题
C. 一个专项主题持续跟踪

2. 你最想看的主题是哪些？
A. AI 与科技
B. 政策与监管
C. 商业与市场
D. 文化与社会
E. 教育与体育
F. 储能与电池
G. 充电 / 快充 / V2G
H. 机器人 / 具身智能
I. 汽车与新能源
J. 其他专项主题

3. 如果你选了专项主题，再选一下关注重点：
A. 技术路线
B. 政策标准
C. 企业动态
D. 项目落地 / 招投标
E. 市场 / 融资
F. 安全 / 事故
G. 学术 / 研究

4. 再选一下地域范围：
A. 中国
B. 美国
C. 欧洲
D. 全球
E. 其他地区

5. 如果有想排除的内容，再补一句就行。

你可以直接回复类似：
“1B，2A+F+G，3B+D+F，4A+C，不看纯乘用车销量。”
```

## Specialty-topic follow-up prompt

If the user gave a specialty label that is still too broad, use this shorter follow-up instead of starting retrieval immediately:

```text
我先帮你把“专项主题”收紧一下，不然后面会混入太多无关信息。

我理解你现在想跟踪的是：
- 主题：{specialty_label}

你直接选就行：
1. 更想看哪一层？
A. 技术
B. 政策
C. 企业动态
D. 项目落地 / 招投标
E. 市场 / 融资
F. 安全
G. 研究

2. 主要看哪些地区？
A. 中国
B. 美国
C. 欧洲
D. 全球
E. 其他

3. 下面哪种收口方式更适合？
A. 限定几个核心关键词
B. 限定几家公司 / 机构
C. 限定技术路线
D. 限定应用场景
E. 没问题，按当前范围就行

如果你方便，我也可以按这个版本先定：
“{candidate_specialty_formulation}”
你回复“按这个来”我就直接开始；如果有排除项，再补一句就够了。
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
```

Do not show this normalized block unless it helps the user confirm assumptions quickly.
