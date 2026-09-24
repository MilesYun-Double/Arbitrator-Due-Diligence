# 商事仲裁员尽调与冲突审查 Skill：项目简报

> 更新日期：2026-09-25
> 正式名称：Arbitrator Due Diligence
> 当前阶段：V0.2 Evidence Foundation → 主控验收 → 独立审查

本项目面向中国大陆商事仲裁案件中的律师、企业法务和争议解决团队，围绕指定仲裁机构及有限候选范围，整理仲裁员身份、专业背景、公开著作与观点、公开专业关系事实、冲突线索、来源限制和人工复核事项。

核心价值是帮助律师完成仲裁员选任尽调、专业匹配和利益冲突线索核查，不预测仲裁员偏向，不自动选择人选，也不替代律师作最终判断。

## 当前范围

- 首轮机构：贸仲（CIETAC）。
- 当前阶段：V0.2 Evidence Foundation → 主控验收 → 独立审查。
- 当前主要产物：Evidence Schema、Snapshot Policy、Validator、测试和合成示例。
- 当前工作区：`D:\Arbitrator Due Diligence`。
- 真实人物试用报告保留在本地 `reports/`，不纳入公开仓库。
- 当前没有数据库、后台服务、UI、外部 API 或多 Agent 调度平台。

## 产品边界

可以做：

- 指定机构和候选范围内的基础尽调；
- 依据用户明确给出的观点或法律问题进行公开观点检索；
- 在提供比对主体和必要授权后整理案件相关公开冲突线索；
- 以 Evidence Object、Markdown、HTML 和 PDF 形成可人工复核的报告链。

不做：

- 不分析完整案卷、提炼全案争议焦点或制定代理策略；
- 不预测偏向、胜诉率、胜诉概率或“容易支持某一方”；
- 不自动决定人选、认定回避或提出回避申请；
- 不采集私人通信、私人社交关系、泄露数据、非公开仲裁材料或未经核实传闻。

## 当前阶段之后的已确认路线

```text
独立审查通过
→ Capability Requirements / Source Evaluation
→ Bundled Capability Baseline
→ 从实际 CIETAC 官方候选范围按预先固定规则随机抽取 5 名普通仲裁员
→ 锁定样本
→ 第一名完整真实链路
```

该路线只记录已确认阶段，不在本简报中设计 Capability 实现或新增第三方项目。

## Evidence 基础

关键事实、观点和关系线索必须先形成结构化 Evidence Object，再进入报告链：

```text
Research → Evidence Objects → evidence.json → Validator → Canonical Report Model → Markdown / HTML / PDF
```

Evidence 字段和 Snapshot 规则分别以 `schemas/evidence.schema.json` 和 `references/snapshot-policy.md` 为准。Snapshot 记录检索时看到了什么，不提高原始来源权威性。

## 治理

用户是最终决策人；主对话是项目主控；主开发负责获准范围内的实现和证据；独立 Codex 对话负责独立审查。当前下一 Gate 是独立审查，不由主开发自行进入下一阶段。
