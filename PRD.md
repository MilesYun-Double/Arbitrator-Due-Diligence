# Product Requirements Document

## Product name

Arbitrator Due Diligence

## Product positioning

面向中国大陆商事仲裁案件中的律师、企业法务和争议解决团队，对指定仲裁机构及候选仲裁员进行有来源、可人工复核的基础尽调、用户指定观点检索和案件相关冲突线索核查。首轮机构为 CIETAC（中国国际经济贸易仲裁委员会）。

## Product functions

### 基础尽调（默认）

整理身份、专业背景、任职经历、公开著作和公开专业关系。

### 指定观点检索（可选）

仅根据用户明确给出的观点或法律问题检索，不擅自从案情扩展争议焦点。

### 案件相关冲突线索核查（可选）

仅在用户提供比对主体及必要授权后执行，输出公开关系事实和时间线，不自动作出回避结论。

## Non-goals

本阶段不分析完整案卷、不提炼全案争议焦点、不制定代理策略，不预测仲裁员偏向、胜诉率或“更容易支持某一方”，不自动决定人选、认定回避或提出回避申请。不采集私人通信、私人社交关系、泄露数据或非公开仲裁材料。

## Evidence and reporting requirements

关键事实、观点和关系线索必须先形成 Evidence Object，再进入报告链：

```text
Research → Evidence Objects → evidence.json → Validator → Canonical Report Model → Presentation → HTML / PDF
```

Evidence 字段和 Snapshot 规则以 `schemas/evidence.schema.json` 与 `references/snapshot-policy.md` 为准。最终用户输出必须保持事实、Evidence 对应、限制和来源一致；Renderer / Presentation 不得联网补事实、改变来源等级或把不确定改成确定。

## Final delivery direction

当前确认的产品方向是双交付：

### Interactive HTML

作为未来主要工作版 / 交互版，面向案件团队日常阅读和核验。

应支持：

- 快速查看关键事实；
- 展开/收起 Evidence；
- 查看来源；
- 聚焦未确认事项；
- 模块导航；
- 用户下一步决策提示。

交互默认只改变展示状态。未来如加入律师人工复核、备注或接受风险等状态，应使用独立 review / annotation data，不直接改写历史 Evidence。

### PDF

作为固定版 / 交付版，面向客户发送、邮件附件、卷宗和归档。

必须：

- 与 HTML 使用同一事实源；
- 固定检索截止时间和报告版本；
- 保留 material limitations / unknown；
- 保留来源可追溯性；
- 不默认展示绝大多数机器审计字段。

### Markdown

继续作为内部/兼容输出，用于 diff、调试、审查和 portable text；当前不定位为主要终端用户交付物。

## Report UX and information hierarchy

最终用户体验采用三层信息模型。

### 用户默认看到

- 这个仲裁员是谁；
- 核实到哪些关键事实；
- 与选择/使用他有什么实际相关性；
- 哪些重要事项尚未确认；
- 是否需要用户进一步决定。

### 需要时展开

- 来源；
- 关键引用；
- 必要限制；
- Evidence 对应关系；
- human review / uncertainty 等与判断有关的信息。

### 系统保存、不默认展示

- SHA-256；
- local path；
- retrieval timestamp；
- snapshot path/level；
- parser/extraction metadata；
- execution receipts；
- token / cost / benchmark；
- internal safety / governance evidence；
- 重复 machine validation 字段。

如果系统内部事实实质影响报告可靠性，必须把其**影响**翻译成用户可理解的限制并提升到用户可见层，而不是显示原始机器错误。

详细规则以 `references/report-experience-and-information-architecture.md` 为准。

UX/UI 不能通过删除 Evidence、unknown、coverage gap、人工复核状态或未执行模块来让报告显得更简洁。

未来正式启动 HTML/PDF UX/UI 项目时，应基于真实报告样本创建 `REPORT_DESIGN.md`，记录视觉层级、组件、交互、PDF 版式、状态语义和验收。UX/UI 变更应记录 Before / After / Why / Source-Evidence / Affected Scope。

## User-side dependency principle

基础产品应遵循 Bundled First、Host Enhanced：用户不应被强制购买服务、申请付费 API 或另行安装第三方项目。Skill ZIP 可携带合法可再分发的脚本、Schema、模板和静态资源；宿主已有联网能力可用于搜索。实际打包第三方组件时必须单独核验许可证、NOTICE 和再分发义务。

## User waiting experience and timing

技术上能完成不等于产品可接受。Capability、第三方来源和架构选型必须同时考虑用户等待时间；后续每项关键 Capability 都应保留可复现的实测耗时，并关注冷启动、单来源处理、网络等待/重试以及串并行结构对总耗时的影响。

真人 research run 应按 `references/research-performance-benchmark.md` 记录 token、时间、能力配置、来源/Evidence 产出和可得的实际成本，用于长期比较不同能力与方法；性能优化不得牺牲证据质量。

## Current scope and success standard

V0.2 Evidence Foundation、静态来源、数字原生 PDF、Canonical Report Model → Markdown / HTML / PDF、Bundled Capability Baseline，以及 authorized real research run plumbing 均已通过相应主控 Gate / 独立审查。CIETAC 5 人样本已经锁定。

第一名 `WONG, King/黄劲` 的真实完整基础尽调链路已执行，执行端状态为 `REAL_CHAIN_PARTIAL`，当前进入独立审查 Gate。

第一份真人报告已经证明当前“完整 Evidence 字段式输出”不适合作为最终用户体验：9 条 final Evidence 形成 17 页 PDF，并展示大量 machine fields。因此未来 UX/UI 项目的核心不是单纯美化，而是建立稳定的 Presentation Layer 和三层信息结构。

报告 UX/UI 实现尚未启动；当前仅记录产品方向，不授权 Renderer/UI 改造。