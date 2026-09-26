# Architecture

## Current logical flow

```text
User Task
    ↓
Core Skill
    ↓
Research / Capability Layer
    ↓
Evidence Objects
    ↓
evidence.json
    ↓
Validator
    ↓
Canonical Report Model
    ↓
Presentation Layer / View Mapping
    ↓
Read-only Interactive HTML + Fixed PDF
```

Markdown 保留为内部/兼容 representation。

## Current layers

### Core

负责工作流、证据规则、判断边界、Schema、Validator 和 Evals。

### Capability Layer

承载 Search、Fetch、Snapshot、Document Extraction、Entity Resolution、Viewpoint Analysis、Relationship Analysis、Validation 和 Rendering。当前已实现静态来源、数字原生 PDF 提取、authorized real research run 与结构化报告输出。

Capability 原则为 **Bundled First, Host Enhanced**。

### Project Layer

当前只有 CIETAC。

### Evidence / Audit Layer

系统完整保存 Evidence、Snapshot、provenance、hashes、retrieval / extraction metadata、performance、execution / governance receipts。

### Canonical Report Model

作为事实与报告语义共享基础，保留 task scope、identity、facts、Evidence references、limitations、unknowns、human-review state 和 source index。

### Presentation Layer

未来明确新增：

```text
Canonical Report Model
        ↓
Visibility / information hierarchy policy
        ↓
User-facing View Model
        ├── Read-only Interactive HTML
        └── Fixed PDF
```

Presentation Layer 可以：

- 重排信息；
- 改变默认展开状态；
- 隐藏 machine-only 字段；
- 生成摘要视图；
- 生成 PDF 固定阅读结构。

不得：

- 补造研究事实；
- 删除 material limitation；
- 提高来源等级；
- 把 unknown 改为 known；
- 把 not_started 改为 reviewed；
- 修改底层 Evidence；
- 写入用户备注；
- 发起补查；
- 建立复核/审批状态机。

## Three-layer visibility model

### Layer 1 — Default user view

回答：Who is this arbitrator? What key facts were verified? What is practically relevant? What important matters remain unconfirmed?

### Layer 2 — On-demand evidence view

显示 sources、key excerpts、relevant limitations、Evidence mapping、必要的 uncertainty / human-review status。

### Layer 3 — Internal system record

保存但默认隐藏 SHA-256、local paths、retrieval timestamps、snapshot paths/levels、parser/extraction metadata、receipts、token/cost/performance、internal governance evidence、重复 validation fields。

## Read-only Interactive HTML

允许：

- expand/collapse Evidence；
- module navigation；
- filter unknowns；
- show sources；
- focus on unresolved items；
- internal page navigation。

不允许：

- review complete；
- lawyer note；
- supplementary research request；
- accepted risk；
- annotation writeback；
- 修改 Evidence / report state。

当前 HTML 交互是**只读 presentation state**，不是 collaboration/workflow system。

## Fixed PDF

未来作为正式固定交付版，与 HTML 共享 Canonical facts，固定 version / cutoff date，保留 material unknowns 和 traceable source index，不默认打印 Layer 3 machine fields。

PDF 可以有不同布局，但不能使用不同事实。

## Current implementation status

当前 Renderer 仍接近 Canonical/Evidence 审计视图，尚未实现独立 Presentation Layer。

第一名真人样本：

- 9 final Evidence；
- 17-page PDF；
- 大量 local_path / retrieval / snapshot / hash machine fields 被直接呈现。

未来技术工作重点：

1. 建立 Presentation View Model；
2. 实现 Layer 1/2/3 visibility；
3. 只读 HTML 交互；
4. PDF 固定版；
5. 证明 HTML/PDF 事实一致性。

当前未授权实现。

## Future design artifacts

正式启动 UX/UI 后：

- `PRD.md`：用户目标与验收；
- `references/report-experience-and-information-architecture.md`：信息层与 visibility policy；
- `ARCHITECTURE.md`：Presentation Layer 技术边界；
- `REPORT_DESIGN.md`：只读 HTML interaction + PDF visual/component spec；
- `PROJECT_BRIEF.md`：阶段和 Gate。

Material changes 记录 Before / After / Why / Source-Evidence / Affected Scope。
