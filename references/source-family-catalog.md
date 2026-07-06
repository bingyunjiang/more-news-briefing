# Source Family Catalog

Use this reference when you need a more concrete source menu than the generic source-design patterns.

This catalog is derived from four neighboring projects:

1. `newsnow` — broad hotlist and realtime source directory
2. `Horizon` — multi-source technical and community intelligence
3. `AIMedia` — domestic mainstream-media and channelized news collection
4. `ai-xiaohongshu-daily` — narrow, repeatable editorial pipelines with article-body extraction

The goal is not to mirror their exact source lists. The goal is to reuse their source-family logic inside `more-news-briefing`.

## How to use this catalog

For each briefing bucket, try to assign:

1. one `discovery family`
2. one `verification family`
3. one optional `context family`
4. one optional `watch family`

This prevents the digest from becoming either:

1. a hotlist dump with no proof, or
2. a slow official-document summary that misses what people are actually watching

## Onboarding shortcuts

Use these shortcuts during first-use onboarding when the user prefers to choose a source style instead of describing it:

1. `A. 偏热点`
   Maps to: China hotlists, portal rankings, realtime market streams
   Best for: broad awareness, fast discovery, chatty daily scans
2. `B. 偏官方`
   Maps to: official and institutional sources, mainstream direct-reporting outlets
   Best for: policy, regulation, safety, markets, factual confidence
3. `C. 偏社区`
   Maps to: developer-attention communities, community discussion sources
   Best for: AI tools, open source, practitioner sentiment, technical nuance
4. `D. 偏产业`
   Maps to: specialty industrial trade sources, channelized media subfeeds
   Best for: storage, charging, grid, power electronics, deployment tracking
5. `E. 平衡默认`
   Maps to: one discovery family plus one verification family, then add context only when clearly useful

If the user picks multiple shortcuts, combine them in this order:

1. verification
2. discovery
3. context
4. watch

## Family 1: China hotlists and portal rankings

Borrowed mostly from `newsnow`.

Typical role:

1. discovery
2. attention ranking
3. China-topic situational awareness

Good members:

1. 微博热搜
2. 知乎热榜
3. 今日头条热榜
4. 抖音热点
5. 澎湃热榜
6. 百度贴吧热议

Best use:

1. broad daily digest
2. social and culture awareness
3. early headline discovery before formal reporting fills in

Do not use as:

1. sole evidence for policy or safety claims
2. sole proof for market-moving stories

## Family 2: Mainstream direct-reporting outlets

Borrowed from `AIMedia` and reinforced by the source ladder.

Typical role:

1. confirmation
2. primary narrative source
3. broad coverage fallback

Good members:

1. 澎湃新闻
2. 中国日报
3. 腾讯新闻
4. 网易新闻
5. 搜狐新闻
6. 新浪国际

Best use:

1. politics and policy
2. general business developments
3. broad current-affairs confirmation

Upgrade:

1. prefer subchannels over homepage-level browsing when the topic is recurring

## Family 3: Channelized media subfeeds

Borrowed strongly from `AIMedia`.

Typical role:

1. focused discovery
2. repeatable specialty monitoring

Good members:

1. policy subchannels
2. finance subchannels
3. tech or AI subchannels
4. project / local deployment subchannels
5. automotive / energy / industrial subchannels

Best use:

1. when a user wants one domain watched every run
2. when the main challenge is “too broad” rather than “too narrow”

Practical rule:

1. if an outlet has a relevant internal channel, search or browse that channel before widening to generic web search

## Family 4: Realtime market and fast-news streams

Borrowed mainly from `newsnow`.

Typical role:

1. discovery
2. recency prioritization
3. markets and macro awareness

Good members:

1. 华尔街见闻快讯类源
2. 财经快讯流
3. exchange or disclosure update pages

Best use:

1. business and markets
2. rate decisions, earnings, guidance, or surprise announcements

Verification pair:

1. exchange filing
2. earnings release
3. official company statement

## Family 5: Developer-attention and builder communities

Borrowed from `Horizon` and `ai-xiaohongshu-daily`.

Typical role:

1. context
2. early discovery
3. practitioner relevance

Good members:

1. Hacker News
2. GitHub Trending
3. GitHub releases
4. V2EX
5. Juejin
6. Product Hunt

Best use:

1. AI tools
2. open source
3. developer infrastructure
4. robotics software stacks
5. protocol or standards implementation activity

Do not use as:

1. factual proof for policy, safety, or finance
2. broad-news replacement

## Family 6: Community discussion and sentiment sources

Borrowed mainly from `Horizon`.

Typical role:

1. context
2. controversy detection
3. technical nuance

Good members:

1. Reddit
2. practitioner forums
3. top comment threads under HN or similar communities
4. selected Telegram or X accounts when clearly high signal

Best use:

1. explaining why an AI or developer story matters
2. identifying objections, limitations, and edge cases
3. surfacing open questions for `继续跟踪`

Rule:

1. quote or summarize these only after the underlying event itself is verified elsewhere

## Family 7: Official and institutional sources

Borrowed across all four projects and aligned with the source ladder.

Typical role:

1. verification
2. regulatory or technical authority
3. stable recurring watchlist

Good members:

1. ministries and regulators
2. standards bodies
3. exchanges
4. company investor-relations or newsroom pages
5. project tender and bid pages
6. university, lab, or conference pages

Best use:

1. policy
2. safety
3. technical standards
4. markets
5. research validation

Access rule:

1. if a source is public, use it directly
2. if a source is account-gated but high value, it is still acceptable to use
3. when login is required, remind the user to log in and say what stronger coverage or evidence that source provides

## Family 8: Specialty industrial trade sources

This is the most important family to strengthen for this user profile.

Typical role:

1. discovery
2. domain context
3. specialty watch

Good members:

1. energy storage trade press
2. charging and EV infrastructure trade press
3. grid and power-market trade press
4. power semiconductor and inverter coverage
5. industry association updates

Best use:

1. storage deployments
2. charging policy and rollout
3. fire safety or incident tracking
4. standards progress
5. supplier and project movement

Verification pair:

1. regulator notice
2. tender file
3. company project release
4. standard body document

## Family 9: Narrow editorial pipelines

Borrowed mostly from `ai-xiaohongshu-daily`.

Typical role:

1. recurring fixed-topic run
2. repeatable source budget
3. delivery-friendly structure

Good pattern:

1. define 2 to 4 fixed source families
2. define a hard cap per family
3. extract article body when titles are not enough
4. keep a fixed output shape

Best use:

1. “AI daily”
2. “HN + selected feed digest”
3. “charging and storage watch”
4. “weekly regulation brief”

## Subtopic routing

Use this section after the user has already chosen a broad specialty topic and then narrowed to a second-layer subtopic.

For each subtopic, prefer one source-family stack instead of a random mix.

### Energy and power

#### `储能`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: mainstream direct-reporting outlets when large deployments or incidents break wider
4. `watch`: company and project watchlists

#### `充电 / 快充`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: developer-attention communities when protocols or software stacks matter
4. `watch`: operator, standard, and project watchlists

#### `V2G / 车网互动`

1. `discovery`: official and institutional sources + specialty industrial trade sources
2. `verification`: official and institutional sources
3. `context`: developer-attention communities and community discussion when protocol, EMS, or aggregator tooling matters
4. `watch`: institution and standards watchlists

#### `EMS / 能源管理`

1. `discovery`: specialty industrial trade sources + developer-attention communities
2. `verification`: official and institutional sources
3. `context`: community discussion and narrow editorial pipelines
4. `watch`: company, repo, and standards watchlists

#### `电力市场`

1. `discovery`: realtime market and fast-news streams + official and institutional sources
2. `verification`: official and institutional sources
3. `context`: mainstream direct-reporting outlets
4. `watch`: regulator, exchange, and market-platform watchlists

#### `电力电子 / 逆变器`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: developer-attention communities when open hardware, control software, or standards implementation matters
4. `watch`: company and conference watchlists

#### `SiC / GaN`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: community discussion and conference-heavy coverage
4. `watch`: company, fab, and research-lab watchlists

### AI and robotics

#### `大模型技术`

1. `discovery`: developer-attention and builder communities + mainstream direct-reporting outlets
2. `verification`: official and institutional sources
3. `context`: community discussion and narrow editorial pipelines
4. `watch`: lab, company, repo, and benchmark watchlists

#### `AI Agent / 工具链`

1. `discovery`: developer-attention and builder communities
2. `verification`: official repo-release, product, or company sources
3. `context`: community discussion sources
4. `watch`: repo and maintainer watchlists

#### `机器人 / 具身智能`

1. `discovery`: mainstream direct-reporting outlets + specialty industrial trade sources
2. `verification`: official and institutional sources
3. `context`: developer-attention communities and community discussion
4. `watch`: company, lab, and repo watchlists

#### `开源模型与社区`

1. `discovery`: developer-attention and builder communities
2. `verification`: official model, repo-release, or lab sources
3. `context`: community discussion sources
4. `watch`: repo and forum watchlists

### Simulation and digital twin

#### `多物理场仿真`

1. `discovery`: specialty industrial trade sources + official and institutional sources
2. `verification`: official and institutional sources
3. `context`: community discussion and narrow editorial pipelines
4. `watch`: vendor, lab, and conference watchlists

#### `电磁 / 热 / 结构仿真`

1. `discovery`: specialty industrial trade sources
2. `verification`: official and institutional sources
3. `context`: community discussion sources
4. `watch`: vendor, lab, and conference watchlists

#### `系统级仿真`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: developer-attention communities when model-based tooling is relevant
4. `watch`: platform and research watchlists

#### `数字孪生平台`

1. `discovery`: specialty industrial trade sources + mainstream direct-reporting outlets
2. `verification`: official and institutional sources
3. `context`: community discussion and narrow editorial pipelines
4. `watch`: platform, project, and standards watchlists

#### `实时仿真 / HIL`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: community discussion sources
4. `watch`: vendor, lab, and test-platform watchlists

### Thermal management

#### `液冷`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: mainstream direct-reporting outlets for large deployments
4. `watch`: company and project watchlists

#### `风冷`

1. `discovery`: specialty industrial trade sources
2. `verification`: official and institutional sources
3. `context`: community discussion sources
4. `watch`: company and product watchlists

#### `热界面材料`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: research and conference coverage
4. `watch`: supplier and lab watchlists

#### `热设计与热仿真`

1. `discovery`: specialty industrial trade sources + simulation-related watch sources
2. `verification`: official and institutional sources
3. `context`: community discussion and narrow editorial pipelines
4. `watch`: vendor, lab, and platform watchlists

#### `电池热管理`

1. `discovery`: specialty industrial trade sources + automotive subfeeds
2. `verification`: official and institutional sources
3. `context`: mainstream direct-reporting outlets for incidents and recalls
4. `watch`: OEM, supplier, and project watchlists

#### `功率器件散热`

1. `discovery`: specialty industrial trade sources + semiconductor/electronics subfeeds
2. `verification`: official and institutional sources
3. `context`: conference and engineering-community discussion
4. `watch`: supplier, lab, and product watchlists

### Test methods and validation

#### `测试标准`

1. `discovery`: official and institutional sources
2. `verification`: official and institutional sources
3. `context`: specialty industrial trade sources
4. `watch`: standards-body and association watchlists

#### `试验方法`

1. `discovery`: official and institutional sources + specialty industrial trade sources
2. `verification`: official and institutional sources
3. `context`: community discussion and narrow editorial pipelines
4. `watch`: lab, method, and conference watchlists

#### `可靠性验证`

1. `discovery`: specialty industrial trade sources + channelized media subfeeds
2. `verification`: official and institutional sources
3. `context`: research and conference coverage
4. `watch`: lab, supplier, and standard watchlists

#### `安全测试`

1. `discovery`: official and institutional sources + mainstream direct-reporting outlets
2. `verification`: official and institutional sources
3. `context`: specialty industrial trade sources
4. `watch`: regulator, lab, and incident-tracking watchlists

#### `台架 / HIL / 实验平台`

1. `discovery`: specialty industrial trade sources + developer-attention communities
2. `verification`: official and institutional sources
3. `context`: community discussion sources
4. `watch`: platform, lab, and vendor watchlists

#### `标定与测量方法`

1. `discovery`: specialty industrial trade sources + official and institutional sources
2. `verification`: official and institutional sources
3. `context`: research and engineering-community discussion
4. `watch`: lab, instrument, and standard watchlists

## Recommended defaults for `more-news-briefing`

### Broad digest

1. `discovery`: China hotlist family + mainstream direct-reporting family
2. `verification`: official and institutional family for top items
3. `context`: developer-attention or community-discussion family for technical items
4. `watch`: specialty industrial trade family if the user has a domain preference

### AI and robotics digest

1. `discovery`: developer-attention family + mainstream tech reporting
2. `verification`: official lab, company, or repo-release sources
3. `context`: community-discussion family
4. `watch`: named company and repo watchlists

### Energy storage / charging / EMS / power electronics digest

1. `discovery`: specialty industrial trade family + channelized media subfeeds
2. `verification`: official and institutional family
3. `context`: developer-attention family only when software, protocol, or tooling is relevant
4. `watch`: company, institution, and project watchlists

### Markets and policy digest

1. `discovery`: realtime market family + mainstream direct-reporting family
2. `verification`: official and institutional family
3. `context`: community-discussion family only as a side signal

## Selection rule

If a source family helps you discover stories but not prove them, keep it near the top of the pipeline and away from final evidence.

If a source family proves claims but discovers little, use it as a verifier or watchlist, not as the only collector.
