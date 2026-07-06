# Watchlist Template

Use this reference after the user has chosen a specialty subtopic and wants recurring monitoring.

The goal is not to invent a final watchlist automatically. The goal is to offer a strong starting skeleton for:

1. `company_watchlist`
2. `institution_watchlist`
3. `community_watchlist`

Only keep names the user confirms or clearly accepts as a starting set.

## How to use this template

When the user wants a repeatable specialty briefing:

1. pick the matching subtopic section
2. offer the suggested watchlist skeleton
3. let the user keep, trim, or replace names
4. store only the accepted names in the resolved contract

## AI and robotics

### `大模型技术`

`company_watchlist`

1. OpenAI
2. Anthropic
3. Google DeepMind
4. Meta AI
5. xAI
6. Mistral
7. 阿里通义
8. DeepSeek

`institution_watchlist`

1. OpenAI blog / model release pages
2. major benchmark or safety organizations
3. official policy or standards bodies when regulation matters

`community_watchlist`

1. Hacker News
2. GitHub release pages for major model tooling
3. Reddit communities such as LocalLLaMA

### `AI Agent / 工具链`

`company_watchlist`

1. OpenAI
2. Anthropic
3. LangChain
4. LlamaIndex
5. relevant workflow or agent-tool vendors

`institution_watchlist`

1. official product blogs
2. repo release pages
3. benchmark or evaluation projects

`community_watchlist`

1. Hacker News
2. GitHub trending / releases
3. developer forums and practitioner communities

## Simulation and digital twin

### `多物理场仿真`

`company_watchlist`

1. Ansys
2. COMSOL
3. Siemens
4. Dassault Systemes

`institution_watchlist`

1. major conference or journal release pages
2. standards or engineering societies
3. university or lab release pages

`community_watchlist`

1. simulation user communities
2. relevant GitHub projects
3. engineering discussion forums

### `数字孪生平台`

`company_watchlist`

1. Siemens
2. Dassault Systemes
3. PTC
4. Hexagon
5. Autodesk

`institution_watchlist`

1. industrial standards bodies
2. smart manufacturing initiatives
3. government or city digital-twin programs when relevant

`community_watchlist`

1. practitioner communities
2. platform ecosystem blogs
3. GitHub projects tied to twin or industrial data stacks

### `实时仿真 / HIL`

`company_watchlist`

1. dSPACE
2. OPAL-RT
3. NI
4. Typhoon HIL

`institution_watchlist`

1. testing or certification bodies
2. university labs
3. conference pages for HIL and systems validation

`community_watchlist`

1. engineering forums
2. GitHub projects for control, co-simulation, or HIL tooling

## Thermal management

### `散热与热管理`

`company_watchlist`

1. Boyd
2. Vertiv
3. Schneider Electric
4. relevant liquid-cooling or thermal-material vendors

`institution_watchlist`

1. ASME or similar engineering societies
2. battery-safety or thermal-standard bodies when relevant
3. major conference or lab pages

`community_watchlist`

1. thermal-design engineering forums
2. packaging and electronics cooling communities
3. relevant GitHub or open-hardware projects when applicable

### `功率器件散热`

`company_watchlist`

1. Infineon
2. Wolfspeed
3. onsemi
4. STMicroelectronics
5. relevant module or cooling suppliers

`institution_watchlist`

1. IEC or similar standards bodies
2. conference pages on packaging, power modules, and cooling
3. lab and university release pages

`community_watchlist`

1. power-electronics engineering communities
2. conference-side technical discussion
3. GitHub or open design communities when relevant

## Test methods and validation

### `试验方法`

`company_watchlist`

1. key lab-equipment vendors only if the user cares about instruments
2. core suppliers or OEMs if the method is product-specific

`institution_watchlist`

1. standards bodies
2. testing and certification agencies
3. university or national labs

`community_watchlist`

1. engineering forums
2. conference method discussions
3. niche practitioner communities

### `安全测试`

`company_watchlist`

1. key OEMs or suppliers tied to the risk area
2. project owners for major incidents

`institution_watchlist`

1. regulators
2. certification bodies
3. safety-notice and recall pages

`community_watchlist`

1. incident-tracking communities
2. engineering discussion forums
3. practitioner groups focused on safety and compliance

## Energy and power

### `储能`

`company_watchlist`

1. CATL
2. BYD
3. Sungrow
4. Tesla Energy
5. Fluence

`institution_watchlist`

1. NEA
2. NDRC
3. MIIT
4. standards or fire-safety bodies

`community_watchlist`

1. storage engineering communities
2. project and tender trackers
3. GitHub or protocol communities when software layers matter

### `充电 / 快充`

`company_watchlist`

1. Tesla Supercharger
2. Ionity
3. BP Pulse
4. major charging operators in the user’s region

`institution_watchlist`

1. CharIN
2. SAE
3. NEA / MIIT / local regulators when relevant

`community_watchlist`

1. OCPP communities
2. ISO 15118 repositories or forums
3. operator or EV-infrastructure communities

### `EMS / 能源管理`

`company_watchlist`

1. Schneider Electric
2. ABB
3. Siemens
4. Huawei Digital Power

`institution_watchlist`

1. grid and dispatch institutions
2. standards bodies
3. regulator or market-operation agencies

`community_watchlist`

1. EMS software communities
2. GitHub projects
3. operator and integrator discussion groups

## Prompting shortcut

Use a short prompt like this when proposing a starter watchlist:

```text
如果你愿意，我可以先按这个默认观察名单起步，你只需要告诉我“保留哪些、删掉哪些”：

- 公司名单：{company_watchlist_candidates}
- 机构名单：{institution_watchlist_candidates}
- 社区名单：{community_watchlist_candidates}
```
