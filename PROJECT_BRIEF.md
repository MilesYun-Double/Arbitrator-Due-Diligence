# 商事仲裁员尽调与冲突审查 Skill：项目简报

> 更新日期：2026-09-25
> 正式名称：Arbitrator Due Diligence
> 当前阶段：V1 最小能力实现
> 当前获准子阶段：第一名真实完整链路

本项目面向中国大陆商事仲裁案件中的律师、企业法务和争议解决团队，围绕指定仲裁机构及有限候选范围，整理仲裁员身份、专业背景、公开著作与观点、公开专业关系事实、冲突线索、来源限制和人工复核事项。

核心价值是帮助律师完成仲裁员选任尽调、专业匹配和利益冲突线索核查，不预测仲裁员偏向，不自动选择人选，也不替代律师作最终判断。

## 当前范围

- 首轮机构：贸仲（CIETAC）。
- V0.2 Evidence Foundation：PASS（已通过独立复审）。
- Capability Requirements / Source Evaluation：PASS。
- Static Source → Snapshot → Evidence：PASS。
- Digital PDF → Snapshot → Evidence：PASS。
- Canonical Report Model → Markdown / HTML：PASS。
- Canonical Report Model → PDF：PASS。
- Bundled Capability Baseline：PASS（Issue #13 主控 Gate；Issue #14 独立审查 PASS）。
- CIETAC 5 人样本抽样与锁样：PASS（Issue #15 主控 Gate；Issue #16 独立审查 PASS）。
- 当前阶段：V1 最小能力实现；当前获准子阶段：**第一名完整真实链路**。
- 当前主要能力：Evidence Schema、Snapshot Policy、Validator、静态来源/PDF提取、Canonical Report Model、Markdown/HTML/PDF Renderer、Bundled capability smoke、端到端合成链。
- 当前工作区：`D:\Arbitrator Due Diligence`。
- 真实人物研究报告和证据继续保留在本地 `reports/`，不纳入公开仓库。
- 当前没有数据库、后台服务、UI、外部 API 或多 Agent 调度平台。

## 当前锁定样本

候选池依据：CIETAC 官网当前“仲裁员名册”正式入口所提供的固定 PDF。

- PDF SHA-256：`978da4776f3263488260a0fa72ab0db8195ab265d7ab93c0509be19603067fe8`
- Candidate pool：2301 条人物记录
- Public pool JSONL SHA-256：`73fe6b0f2c30703a8327e95797d2845bb95c6bc92bb5d2c4f2f23d041666c4e1`

锁定样本按抽样 hash 升序为：

1. `WONG, King/黄劲`（pool_index 1683）
2. `邹明春/Zou Mingchun`（pool_index 1605）
3. `BOGASON, Þórður`（pool_index 1804）
4. `周广俊/Zhou Guangjun`（pool_index 1558）
5. `GRAFSTEIN, Joan`（pool_index 1928）

该顺序仅为确定性抽样顺序，不代表推荐、能力、适合度或优先级。锁样后不因资料少、难检索、同名、国籍、职业或知名度换人。

官方人数 `2308 / 2301 / 2300` 的差异继续作为 known consistency note 保留，不对差异原因作未经证实的推断。

## 当前下一步

只对锁样顺序第 1 名：

`WONG, King/黄劲`

执行一次**完整真实基础尽调链路**：

```text
真实公开检索
→ 身份消歧
→ Source / Snapshot
→ Evidence Objects
→ evidence.json
→ Validator
→ Canonical Report Model
→ Markdown / HTML / PDF
→ readback / consistency check
```

本轮没有用户指定观点或法律问题，因此：

- 指定观点检索：**未启用**；
- 案件相关冲突线索核查：**未启用**；
- 不得把“未执行”写成“没有观点问题”或“无冲突”。

第一名完整真实链路完成后先停止并 Gate，不自动继续第 2–5 名。

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

## 当前路线

```text
V1 最小能力实现
→ Bundled Capability Baseline：PASS
→ CIETAC 5 人确定性抽样与锁样：PASS
→ 第一名完整真实链路：CURRENT
→ 主控验收 / 独立审查
→ 再决定是否继续第 2–5 名或修复暴露问题
```

不在第一名真实链路之前继续增加 PDF/Pillow、OCR、跨平台、UI、数据库或其他非阻塞技术准备。

## Evidence 基础

关键事实、观点和关系线索必须先形成结构化 Evidence Object，再进入报告链：

```text
Research → Evidence Objects → evidence.json → Validator → Canonical Report Model → Markdown / HTML / PDF
```

Evidence 字段和 Snapshot 规则分别以 `schemas/evidence.schema.json` 和 `references/snapshot-policy.md` 为准。Snapshot 记录检索时看到了什么，不提高原始来源权威性。

“未检索到”不等于“不存在”；无法访问、只有摘要、来源受限或同名无法排除时，必须保留 coverage gap / unknown。

## 治理

用户是最终决策人；主对话是项目主控；主开发负责获准范围内的实现和证据；独立 Codex 对话负责独立审查。

主开发不得自行进入下一阶段。第一名真实链路执行完成后先回主控；如出现产品或代码阻塞，不得借机自行修改架构、依赖或扩大范围。