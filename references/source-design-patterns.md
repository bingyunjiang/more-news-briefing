# Source Design Patterns

Use this reference when you need to design a stronger source pool before retrieval. It distills reusable patterns from four neighboring projects:

1. `newsnow` — large public hotlist directory with per-source refresh cadence and column metadata
2. `Horizon` — multi-source intelligence pipeline with community feeds, deduplication, scoring, and enrichment
3. `AIMedia` — domestic mainstream-media source matrix with deep channel coverage and publishing automation
4. `ai-xiaohongshu-daily` — narrow editorial pipelines with fallback fetch routes,正文抽取, and chat-first delivery

Do not copy their workflows whole. Borrow only the source and retrieval patterns that strengthen `more-news-briefing`.

## Core lesson

Do not think of “news source” as one thing. Split the pool into source roles:

1. `headline sources` — tell you what is breaking
2. `verification sources` — prove what actually happened
3. `discussion sources` — show why practitioners or communities care
4. `specialty watch sources` — keep a domain radar warm between big headlines

The strongest digest usually uses at least two of these roles for each top item.

## Pattern 1: Source-role layering

Borrowed mostly from `Horizon` and `ai-xiaohongshu-daily`.

Use this four-layer source stack:

1. `discovery layer`
   Use hotlists, realtime feeds, and broad news queries to surface candidates quickly.
   Examples: HN top stories, GitHub Trending, hot-search boards, fast finance wires.
2. `confirmation layer`
   Re-check retained items with official releases, filings, company blogs, standards bodies, or direct reporting.
3. `context layer`
   Add one surrounding source when the item is technical or niche.
   Examples: top comments, subreddit discussion, repo release notes, blog post body.
4. `watch layer`
   Keep a stable set of specialty feeds or watchlists for recurring user interests.
   Examples: charging policy RSS, GitHub release watchlist, OpenBB equity watchlist, sector newsletters.

Rule:

1. `discovery` can nominate a story
2. `confirmation` should support the claim
3. `context` improves relevance and readability
4. `watch` improves continuity across runs

## Pattern 2: Public hotlist directory

Borrowed mostly from `newsnow`.

Maintain a mental directory of source families instead of improvising every run:

1. `china-hotlists`: 微博, 抖音, 今日头条, 百度贴吧, 知乎, 澎湃热榜
2. `finance-fast`: 华尔街见闻快讯, Jin10-style wires, market flash streams
3. `global-headlines`: Reuters/AP/Bloomberg-style direct reporting, Google News topic pages
4. `developer-attention`: Hacker News, GitHub Trending, Product Hunt, V2EX, Juejin
5. `sports-realtime`: league or event result pages plus broadcaster headlines

Borrow the directory idea, not the exact site list. For the current user base, a good directory should explicitly include:

1. Chinese mainstream portals
2. International direct-reporting outlets
3. Technology and developer communities
4. Energy and industrial trade sources
5. Official regulator or standards channels

## Pattern 3: Deep channel coverage inside one outlet

Borrowed mostly from `AIMedia`.

Do not treat a big media brand as one undifferentiated source. Some outlets expose internal channels that map well to digest buckets.

Good uses:

1. policy subchannels for politics and regulation
2. finance subchannels for macro and capital markets
3. tech subchannels for AI, semiconductors, robotics, and telecom
4. local or project channels for deployments and incidents

This is especially useful for:

1. China policy and state-affairs coverage
2. industrial sectors such as storage, charging, automotive, and power systems
3. when the user wants repeatability more than maximal breadth

## Pattern 4: Community-signal enrichment

Borrowed mostly from `Horizon`.

Use community platforms as side signals, not as sole proof:

1. Hacker News for builder attention and open-source momentum
2. Reddit for practitioner sentiment and long-form technical discussion
3. GitHub releases and maintainer activity for product or tooling movement
4. Telegram or X only when relevant accounts are high signal and can be cross-checked

Good outputs to borrow:

1. point score or engagement score
2. top comments or representative discussion snippets
3. release/change-log text
4. whether the item is getting repeat attention across multiple communities

Use these signals to answer:

1. Why does this matter to practitioners?
2. Is this just a press release, or is it being actively discussed?
3. Which technical angle deserves the summary space?

## Pattern 5: Fallback retrieval routes

Borrowed mostly from `ai-xiaohongshu-daily`.

Design at least one fallback route for fragile sources:

1. `RSS -> HTML page`
2. `official page -> cached mirror or newsroom page`
3. `API -> webpage scrape`
4. `article page -> summary extraction from body text`

Use when:

1. the primary feed is unstable
2. an article feed is partial
3. a topic needs body extraction, not only title links

Do not fail the whole digest just because one source family is down.

If the best available route is account-gated, it is acceptable to use it. In that case:

1. tell the user which source needs login
2. explain what value it adds over public alternatives
3. ask the user to complete login
4. continue with public-source work where possible while waiting

## Pattern 6: Watchlists over ad-hoc searching

Borrowed mostly from `Horizon`.

For recurring specialty briefings, keep explicit watchlists instead of rebuilding the source pool every time.

Useful watchlist shapes:

1. `company watchlist`
   Example: CATL, BYD, Tesla Energy, ABB, Schneider, Sungrow
2. `project watchlist`
   Example: storage tenders, charging corridor projects, grid pilot projects
3. `repo watchlist`
   Example: open-source AI tools, EMS software, charging-protocol libraries
4. `ticker or market watchlist`
   Example: energy storage names, charging operators, power semiconductor firms
5. `institution watchlist`
   Example: NDRC, NEA, MIIT, SAE, IEC, state grids, EU Commission

When the user has a stable specialty topic, convert part of the topic definition into one or more watchlists.

## Pattern 7: Balanced bucket caps

Borrowed mostly from `Horizon`.

Avoid letting one loud category crowd out the digest. Use soft caps:

1. set a total target item count
2. reserve at least one slot for each high-priority user bucket
3. cap noisy categories unless the user explicitly prioritizes them
4. allow overflow only when the signal is clearly stronger than the weaker buckets

This is especially important when AI, markets, or politics are dominating the week.

## Pattern 8: Chat-first delivery formats

Borrowed mostly from `ai-xiaohongshu-daily` and `AIMedia`.

When the channel is Feishu, WeChat, or other chat surfaces, source design should consider delivery:

1. keep one source line per top item
2. prefer items with a clean canonical URL
3. prefer items whose body text can be extracted for better summarization
4. for recurring briefings, preserve one stable label per source family

If the digest may later be turned into cards, issues, or long-message pushes, stable source metadata becomes more valuable.

## Recommended source matrix for this skill

Use this matrix as the default design target.

### Broad daily briefing

1. `headline`: mainstream broad news + one hotlist family
2. `verification`: official release or direct reporting for the top block
3. `context`: one community or trade source for technical items
4. `watch`: one specialty feed if the user has a stable domain interest

### AI and developer watch

1. `headline`: AI press + company blogs + Google News
2. `discussion`: Hacker News + GitHub releases + selected Reddit
3. `verification`: model cards, official blog posts, repo release notes

### Energy storage / charging / power electronics watch

1. `headline`: sector trade press + regulator updates + tender or deployment notices
2. `verification`: standards bodies, ministries, company project notices, safety notices
3. `discussion`: engineering communities, GitHub repos, conference or lab releases when relevant

### Markets / business watch

1. `headline`: market wires + business press
2. `verification`: filings, exchange disclosures, earnings materials
3. `context`: sector trade press or analyst commentary clearly labeled as analysis

## What to adopt into `more-news-briefing`

These are the highest-value borrow points:

1. source-role layering instead of one flat “news sources” list
2. explicit community-signal sources for AI and open-source buckets
3. fallback routes such as RSS-to-HTML and article-body extraction
4. specialty watchlists for recurring domains
5. balanced bucket caps when one category is noisy
6. stable source metadata for future Feishu / WeChat / issue-style delivery
