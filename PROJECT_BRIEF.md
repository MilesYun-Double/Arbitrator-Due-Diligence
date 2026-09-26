# 商事仲裁员尽调与冲突审查 Skill：项目简报

> 更新日期：2026-09-26
> 正式名称：Arbitrator Due Diligence
> 当前阶段：V1 最小能力实现
> 当前状态：第一名真实完整链路 Gate 完成，等待下一阶段决策

本项目面向中国大陆商事仲裁案件中的律师、企业法务和争议解决团队，围绕指定仲裁机构及有限候选范围，整理仲裁员身份、专业背景、公开著作与观点、公开专业关系事实、冲突线索、来源限制和人工复核事项。

核心价值是帮助律师完成仲裁员选任尽调、专业匹配和利益冲突线索核查，不预测仲裁员偏向，不自动选择人选，也不替代律师作最终判断。

## 已完成 Gate

- V0.2 Evidence Foundation：PASS。
- Capability Requirements / Source Evaluation：PASS。
- Static Source → Snapshot → Evidence：PASS。
- Digital PDF → Snapshot → Evidence：PASS。
- Canonical Report Model → Markdown / HTML / PDF：PASS。
- Bundled Capability Baseline：PASS（Issue #13 / #14）。
- CIETAC 5 人样本抽样与锁样：PASS（Issue #15 / #16）。
- Authorized real research run repair：PASS（Issue #18 / #19）。
- 第一名真人完整链路：**Gate PASS on REAL_CHAIN_PARTIAL**（Issue #17 / #20）。

注意：

> Issue #20 的 PASS 验收的是 #17 的 PARTIAL 结果真实、可追溯、分类合理；**不把执行状态升级为 REAL_CHAIN_PASS**。

## 第一名真人样本结果

对象：

`WONG, King/黄劲`（pool_index 1683）

结果：

- Status：`REAL_CHAIN_PARTIAL`
- 正式独立来源：6
- final Evidence：9
- human_review：9/9 `not_started`
- PDF：17 页 / 178,807 bytes
- first timing record → report complete：788.458 s
- token：UNAVAILABLE
- actual cost：UNAVAILABLE

主要 coverage gaps：

1. 历史教学任期公开表述口径未解决；
2. 部分资历和历史岗位尚未逐项独立核实；
3. 完整署名著作目录尚未核验。

这些 gap 影响履历完整性和精确任期，但没有推翻核心公开身份对应。

## 已知非阻断 Findings

### MINOR — E-POLYU-001 locator

当前保存 excerpt locator 命中导航栏中的 “Adjunct Professor”，而同一 Snapshot 人物正文中另有直接支持的姓名+职称文本。

- claim 本身仍有同页直接支持；
- Snapshot / Evidence / report 可追溯；
- Reviewer 评为 MINOR，不阻断第一名 PARTIAL Gate；
- 当前不追溯修改第一份真人报告；
- 后续如继续真人样本或修 collector，应考虑更具体的主体+职称定位，而不是单纯首次字符串命中。

### NOTE — performance.json

本次 performance 记录要求在真人 run 中途追加，因此 run root 没有统一 `performance.json`。

- 现有 timing / step / execution log 可审计；
- 主控已将 summary 写入 `benchmarks/research-performance.jsonl`；
- token 保持 unavailable；
- 下一次真人 run 从开始即要求统一 performance.json，不反向估造本次缺失数据。

## 当前锁定样本

1. `WONG, King/黄劲` — 已完成第一名 PARTIAL Gate
2. `邹明春/Zou Mingchun`
3. `BOGASON, Þórður`
4. `周广俊/Zhou Guangjun`
5. `GRAFSTEIN, Joan`

该顺序仅为确定性抽样顺序，不代表推荐、能力、适合度或优先级。

未获主控/用户授权前，不自动进入第 2 名。

## 报告产品方向

未来最终交付方向：

- **Interactive HTML：只读工作版**
- **PDF：固定正式交付版**
- Markdown：内部/兼容输出

### 三层信息架构

1. **用户默认看到**：仲裁员是谁、核实到哪些关键事实、实际相关性、重要未确认事项。
2. **需要时展开**：来源、关键引用、必要限制、Evidence 对应关系。
3. **系统保存、不默认展示**：hash、local path、retrieval/snapshot/parser metadata、execution receipts、token/cost/performance、内部安全治理与重复 machine validation 字段。

内部事实如实质影响报告可靠性，必须转译成用户可理解的限制后再显示。

### HTML 当前产品边界

HTML 未来只做**只读交互阅读**：

可以：

- 展开/收起 Evidence；
- 模块导航；
- 查看来源；
- 聚焦 unknown / coverage gap；
- 页面内跳转。

明确不做：

- 用户标记复核完成；
- 发起补查；
- 备注/批注；
- 接受风险；
- 审批流；
- 写回 Evidence 或报告状态。

当前尚未授权 UI 实现、Renderer 重构或创建 `REPORT_DESIGN.md`。

## 产品边界

可以做：

- 指定机构和候选范围内的基础尽调；
- 依据用户明确给出的观点或法律问题进行公开观点检索；
- 在提供比对主体和必要授权后整理案件相关公开冲突线索；
- 以 Evidence Object、HTML 和 PDF 形成可人工复核的报告链。

不做：

- 不分析完整案卷、提炼全案争议焦点或制定代理策略；
- 不预测偏向、胜诉率或“更容易支持某一方”；
- 不自动决定人选、认定回避或提出回避申请；
- 不采集私人通信、私人社交关系、泄露数据、非公开仲裁材料或未经核实传闻。

## 当前路线

```text
V1 最小能力实现
→ Bundled Capability Baseline：PASS
→ CIETAC 5 人锁样：PASS
→ real research run repair：PASS
→ 第一名真人链：REAL_CHAIN_PARTIAL / Gate PASS
→ CURRENT: 等待用户决定下一阶段
```

下一阶段尚未自动选择：

- 第 2 名真人样本；
- 修复 locator / performance instrumentation 等非阻断问题；
- 启动只读 HTML + PDF Presentation / UX 项目；
- 或其他明确授权任务。

## Evidence 基础

关键事实、观点和关系线索必须先形成结构化 Evidence Object，再进入报告链。

“未检索到”不等于“不存在”；无法访问、只有摘要、来源受限或同名无法排除时，必须保留 coverage gap / unknown。

## 治理

用户是最终决策人；主对话是项目主控；主开发负责获准范围内的实现和证据；独立 Codex 对话负责独立审查。

主开发不得自行进入下一阶段。
