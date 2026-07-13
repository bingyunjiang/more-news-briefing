# Borrowed News Source Catalog

Use this reference when you need concrete news sites, feeds, APIs, communities, or fallback routes rather than only source-family guidance.

This catalog distills the reusable source inventory from `AIMedia` and `Horizon`. It does not depend on either project at runtime and does not copy their crawlers. Treat URLs, channel IDs, undocumented endpoints, and third-party feed mirrors as changeable discovery routes; verify that they still work before relying on them.

## Table of contents

1. Operating rules
2. AIMedia-derived domestic sources
3. Horizon-derived open and community sources
4. Curated specialty feeds and watchlists
5. Default source packs
6. Fallback routes
7. Source metadata

## Operating rules

Use each source for an explicit role:

1. `discovery`: surface candidate stories quickly
2. `verification`: support the retained factual claim
3. `context`: explain technical or community significance
4. `watch`: monitor a stable company, institution, feed, account, repo, or topic

Apply these constraints:

1. Do not treat a portal ranking, community score, social post, or aggregator headline as sole proof.
2. Open the canonical article or primary document before retaining a high-impact item.
3. Prefer public, keyless routes for the default run.
4. Use login-, token-, provider-, or paid routes only when their incremental value is material.
5. Do not bypass access controls. Ask the user to sign in when a permitted high-value source requires their session.
6. Rate-limit repeated requests and keep a fallback route for every fragile source family.
7. Re-check source availability during each run; this catalog is a routing guide, not an uptime guarantee.

## AIMedia-derived domestic sources

The main lesson from AIMedia is deep channel coverage inside large Chinese media brands. Use the public site or channel page first. Treat the project's JSONP and internal API routes as implementation clues only because undocumented endpoints can change without notice.

### NetEase News

- Site: `https://news.163.com/`
- Useful channels: current affairs, military, society, technology, entertainment, finance, education, lifestyle
- Best roles: `discovery`, `context`
- Best buckets: China general news, technology, business, culture
- Retrieval note: AIMedia used channel-specific JSONP feeds; prefer the public channel page or a `site:163.com` search when the feed is stale.
- Verification rule: follow market-, policy-, safety-, and geopolitics-sensitive stories to an official source or stronger direct report.

### The Paper

- Site: `https://www.thepaper.cn/`
- Best roles: `discovery`, `verification`, `context`
- Best buckets: China policy, law, society, international affairs, business, science, culture
- High-value policy and society channels: 中国政库, 人事风向, 法治中国, 直击现场, 澎湃质量观, 绿政公署
- High-value international channels: 全球速报, 澎湃世界观, 澎湃明查, 澎湃防务, 外交学人, 大国外交
- High-value business and industry channels: 10%公司, 能见度, 财经上下游, IPO最前线, 新引擎, 汽车圈
- High-value science and research channels: 科学湃, 生命科学, 未来2%, 科创101, 科学城邦, 澎湃研究所
- Analysis-only channels: 社论, 澎湃评论, 思想市场 and other opinion sections
- Retrieval note: channel IDs are useful for stable monitoring, but verify the current public channel page rather than assuming old IDs remain valid.

### China Daily Chinese sites

- Sites: `https://china.chinadaily.com.cn/`, `https://cn.chinadaily.com.cn/`, `https://caijing.chinadaily.com.cn/`
- Useful channels: politics, Taiwan affairs, international news, finance events, authoritative releases, disclosure interpretation, health, education, sports
- Best roles: `discovery`, `verification`, `context`
- Best buckets: China policy, international communication, business, health, education
- Verification rule: distinguish China Daily reporting from the underlying government, exchange, or company document; link the primary document when available.

### Sohu News

- Site: `https://www.sohu.com/`
- Useful channels: politics, international, finance, technology, communications, mobile, internet, 5G, smart hardware, science, IPO, emerging sectors, education, culture, entertainment, games and esports
- Best roles: `discovery`, `context`
- Best buckets: broad China coverage, consumer technology, culture, entertainment
- Retrieval note: AIMedia used topic/channel identifiers against an internal feed API. Prefer the public topic page or `site:sohu.com` search as the portable route.
- Verification rule: identify the original publisher because Sohu can carry self-media and republished material.

### Tencent News

- Site: `https://news.qq.com/`
- Useful channels: finance, technology, entertainment, world, military, games, automotive and livelihood, property, health, education, culture, lifestyle
- Best roles: `discovery`, `context`
- Best buckets: broad news, technology, business, culture
- Retrieval note: channel feed identifiers are useful for topic routing, but the public article URL should be the retained canonical URL.
- Verification rule: separate Tencent-origin reporting from partner or republished content.

### Tencent Sports

- Site: `https://sports.qq.com/`
- Best roles: `discovery`, `context`
- Best buckets: sports results, league news, athlete and event coverage
- Verification pair: official league, federation, club, event, or results page for records, sanctions, transfers, and schedules.

### Sina International

- Site: `https://news.sina.com.cn/world/`
- Best roles: `discovery`, `context`
- Best buckets: international headlines and China-language situational awareness
- Verification rule: follow through to the named original outlet, government statement, or international organization document.

### IT Home

- Site: `https://www.ithome.com/`
- Best roles: `discovery`, `context`, `watch`
- Best buckets: consumer technology, devices, operating systems, AI products, Chinese technology companies
- Verification pair: vendor newsroom, product page, changelog, filing, repo release, or regulator notice.

## Horizon-derived open and community sources

The main lesson from Horizon is to mix broad news discovery with developer, community, market, and watchlist signals in one normalized candidate pool.

### Google News RSS search

- Endpoint: `https://news.google.com/rss/search`
- Access: public, no API key
- Best roles: `discovery`
- Best buckets: broad multi-language search, topic sweeps, regional variants
- Query controls: search terms, `when:Nh`, `when:Nd`, `after:YYYY-MM-DD`, language, country, `ceid`
- Availability note: reachability can vary by region or network. Fall back to GDELT or direct publisher search when the RSS endpoint times out.
- Limit: Google News is an aggregator. Retain the publisher's canonical article, not the Google redirect, whenever possible.

### GDELT 2.0 DOC API

- Endpoint: `https://api.gdeltproject.org/api/v2/doc/doc`
- Access: public, no API key
- Best roles: `discovery`, cross-country coverage comparison
- Best buckets: geopolitics, international affairs, crisis monitoring, multilingual global sweeps
- Useful controls: query, date window, `sourcelang:`, `sourcecountry:`, newest-first sorting
- Availability note: reachability can vary by region or network. Fall back to Google News RSS, regional outlet search, or direct web retrieval when the API times out.
- Limit: broad recall can be noisy and metadata can be incomplete. Verify retained items at the publisher or primary source.

### Hacker News

- Site: `https://news.ycombinator.com/`
- API: `https://hacker-news.firebaseio.com/v0`
- Access: public, no API key
- Best roles: `discovery`, `context`
- Best buckets: AI tools, developer infrastructure, startups, open source
- Useful signals: points, comment count, top substantive comments
- Limit: use the linked article or official release as evidence; HN ranking and comments measure attention, not factual authority.

### GitHub

- Site: `https://github.com/`
- API: `https://api.github.com/`
- Access: public; `GITHUB_TOKEN` is optional but raises rate limits
- Best roles: `verification`, `watch`, `context`
- Useful routes: repository releases, changelogs, maintainer/user public events, issue or discussion threads when directly relevant
- Best buckets: open-source releases, AI models and tools, developer infrastructure, standards implementations
- Verification rule: prefer release notes, tags, commits, model cards, and project documentation over community reposts.

### RSS and Atom

- Access: usually public; some full-text feeds require a subscription key
- Best roles: `discovery`, `watch`, sometimes `verification`
- Best buckets: specialist publications, company blogs, researchers, regulators, standards bodies
- Retrieval note: read `published`, `updated`, and `created` fields defensively, then open the linked page when the feed is summary-only.
- Fallback: `RSS/Atom -> linked HTML page -> site search`.

### Reddit

- Sites and routes: `https://old.reddit.com/`, public JSON listings, subreddit RSS
- Access: public routes can work without an API key but are intermittently blocked or rate-limited
- Best roles: `discovery`, `context`
- Useful communities from Horizon presets: `r/MachineLearning`, `r/LocalLLaMA`, `r/linux`, `r/netsec`, `r/webdev`, `r/javascript`, `r/ProgrammingLanguages`, `r/rust`, `r/robotics`, `r/embedded`, `r/commandline`, `r/science`
- Useful signals: score, upvote ratio, comment count, flair, top comments
- Limit: verify the underlying event elsewhere. Treat comments as practitioner reaction, not evidence.

### Telegram public channels

- Public preview route: `https://t.me/s/<channel>`
- Access: public channels only, no API key
- Best roles: `discovery`, `watch`
- Best buckets: regional news, niche communities, fast-moving specialist channels
- Retrieval note: use the first external link as the candidate canonical URL when present.
- Limit: channel identity and claims require verification; never elevate an unattributed message into a confirmed story.

### OSS Insight

- Site: `https://ossinsight.io/`
- API: `https://api.ossinsight.io/v1/trends/repos`
- Access: public, no API key
- Best roles: `discovery`, `watch`
- Best buckets: fast-rising open-source projects, language-specific developer trends
- Useful controls: 24-hour or 28-day period, language, keyword filter, minimum stars gained
- Limit: star growth is an attention signal. Verify the project's actual release, documentation, ownership, and security posture on GitHub.

### OpenBB

- Site: `https://www.openbb.co/platform`
- Access: optional SDK plus provider-specific credentials or settings
- Best roles: `discovery`, `watch`, market context
- Best buckets: company news, equity watchlists, filings and macro sources where supported
- Example provider families: yfinance, Benzinga, FMP, Intrinio, Tiingo, SEC, Federal Reserve
- Limit: provider coverage and licensing differ. Verify material company or market claims with filings, exchange disclosures, earnings materials, or regulator releases.

### X / Twitter through a retrieval provider

- Site: `https://x.com/`
- Horizon route: Apify actor plus `APIFY_TOKEN`
- Access: account/token/credit dependent
- Best roles: `discovery`, `watch`, `context`
- Best buckets: named expert, researcher, company, lab, and maintainer accounts
- Limit: keep disabled by default. Use only for named high-signal accounts and verify important claims through an official page, repo, paper, filing, or direct reporting.

## Curated specialty feeds and watchlists

These examples came from Horizon's presets. Use them as starter candidates, not permanent defaults. Check freshness, ownership, and feed availability before use.

### AI and machine learning

- Simon Willison: `https://simonwillison.net/atom/everything/`
- `r/MachineLearning`
- `r/LocalLLaMA`
- GitHub releases for `vllm-project/vllm`
- GitHub activity for selected maintainers such as `karpathy`
- 量子位 and 新智元 through third-party WeChat-to-RSS mirrors only when the mirror is current and permitted; pair with the original article or another source

### Systems and infrastructure

- LWN: `https://lwn.net/headlines/rss`
- Brendan Gregg: `https://www.brendangregg.com/blog/rss.xml`
- `r/linux`
- GitHub activity for `torvalds`

### Security and privacy

- Krebs on Security: `https://krebsonsecurity.com/feed/`
- Schneier on Security: `https://www.schneier.com/feed/atom/`
- `r/netsec`
- Verification pair: vendor advisory, CVE record, CISA or national CERT notice, patch or release notes

### Hardware and robotics

- Hackaday: `https://hackaday.com/feed/`
- `r/robotics`
- `r/embedded`
- Verification pair: company/lab release, paper, repo, standards document, or product documentation

### Open source and developer tools

- OSS Insight trending API
- GitHub repository releases
- GitHub Trending RSS mirror: `https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml`
- `r/commandline`
- Verification pair: repository release notes and project documentation

### Science and research

- Nature: `https://www.nature.com/nature.rss`
- Quanta Magazine: `https://api.quantamagazine.org/feed/`
- `r/science` for attention only
- Verification pair: paper, journal page, preprint, lab or institution release

## Default source packs

Choose one pack per bucket, then add official verification for retained high-impact items.

### Broad China daily

1. Discovery: NetEase current affairs + Tencent News + one Sohu broad channel
2. Depth: The Paper policy, business, science, or international subchannel matching the bucket
3. Confirmation: China Daily or another direct report
4. Verification: government, regulator, exchange, company, court, or institution source as needed

### AI and technology

1. Discovery: Google News RSS + IT Home + Hacker News
2. Momentum: OSS Insight + GitHub releases
3. Specialist watch: Simon Willison, selected AI RSS, `r/MachineLearning`, `r/LocalLLaMA`
4. Verification: official lab/company blog, model card, paper, repo release, product documentation

### Global affairs

1. Discovery: Google News RSS + GDELT
2. Chinese-language context: Sina International + The Paper international channels
3. Verification: government, international organization, primary document, or reputable direct reporting
4. Rule: require cross-source confirmation for conflict, sanctions, diplomacy, and casualty claims

### Business and markets

1. Discovery: Google News RSS + Tencent finance + NetEase finance
2. Watch: OpenBB ticker lists when installed and configured
3. Context: The Paper business channels + China Daily finance channels
4. Verification: filing, exchange notice, earnings material, regulator release, or company investor relations

### Culture and society

1. Discovery: NetEase society/entertainment + Tencent entertainment/culture + selected Sohu channels
2. Depth: The Paper society and culture channels
3. Verification: direct interview, organizer, platform, court, regulator, or original publisher when claims are contested

### Sports

1. Discovery: Tencent Sports + China Daily sports
2. Context: mainstream sports reporting
3. Verification: official league, federation, club, event, athlete, or results page

## Fallback routes

Use these routes when the preferred collector fails:

1. AIMedia-style channel feed -> public channel page -> `site:<domain> <topic>` web search
2. Google News RSS -> GDELT -> direct publisher or general web search
3. GDELT -> Google News RSS -> regional outlet search
4. RSS/Atom -> linked HTML page -> site search
5. Reddit old-web HTML -> public JSON -> subreddit RSS -> skip and continue
6. GitHub API -> repository release page -> tags/changelog page
7. OSS Insight -> GitHub Trending or release watchlist
8. Telegram preview -> named external link -> general web verification
9. OpenBB -> provider website -> filing/exchange/company IR page
10. X retrieval provider -> official website, repo, paper, filing, or direct report

Do not let one failed source block the whole briefing. Record the coverage gap when it affects a priority bucket.

## Source metadata

Normalize retained candidates with these fields when possible:

1. `source_name`
2. `source_family`
3. `source_role`
4. `topic_bucket`
5. `title`
6. `canonical_url`
7. `published_at`
8. `author_or_account`
9. `engagement_signal`
10. `access_mode`: public, login, token, provider, subscription
11. `evidence_level`: 首选证据, 次选证据, 仅作线索
12. `retrieval_route`
13. `fallback_route`

Keep the canonical publisher or primary-source URL in the final digest. Aggregator, community, and social URLs may remain as supporting context links.
