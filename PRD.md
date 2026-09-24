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
Research → Evidence Objects → evidence.json → Validator → Canonical Report Model → Markdown / HTML / PDF
```

Evidence 字段和 Snapshot 规则以 `schemas/evidence.schema.json` 与 `references/snapshot-policy.md` 为准。三种报告格式应保持事实、Evidence ID、限制和来源一致；Renderer 不得联网补事实、改变来源等级或把不确定改成确定。PDF 是正式交付格式，需支持中文、分页、来源索引和 Evidence 可追溯性。

## User-side dependency principle

基础产品应遵循 Bundled First、Host Enhanced：用户不应被强制购买服务、申请付费 API 或另行安装第三方项目。Skill ZIP 可携带合法可再分发的脚本、Schema、模板和静态资源；宿主已有联网能力可用于搜索。实际打包第三方组件时必须单独核验许可证、NOTICE 和再分发义务。

## Current scope and success standard

V0.2 仅包含 Evidence Foundation。Capability 选型、随机仲裁员研究和完整 Report Renderer 属于后续阶段。当前成功标准是把公开研究结果形成可靠、结构化、可追溯、可验证并能进入统一报告链的证据基础。
