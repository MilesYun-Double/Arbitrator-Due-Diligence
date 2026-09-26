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
Interactive HTML + Fixed PDF
```

Markdown may continue as an internal/compatibility representation, but it is not the primary future user surface.

## Current layers

### Core

负责工作流、证据规则、判断边界、Schema、Validator 和 Evals。当前实现包括 `schemas/evidence.schema.json`、`scripts/validate_evidence.py`、测试和合成示例。

### Capability Layer

承载 Search、Fetch、Snapshot、Document Extraction、Entity Resolution、Viewpoint Analysis、Relationship Analysis、Validation 和 Rendering。当前已实现静态来源、数字原生 PDF 提取、authorized real research run 与结构化报告输出。

Capability 原则为 **Bundled First, Host Enhanced**：基础能力尽可能随 Skill 提供，宿主已有能力可以增强，但不要求普通用户另行安装项目或购买服务。

### Project Layer

当前只有 CIETAC，用于承载机构规则、机构特定来源及规则差异。

### Evidence / Audit Layer

系统完整保存：

- Evidence；
- Snapshot；
- provenance；
- hashes；
- retrieval / extraction metadata；
- performance；
- execution / governance receipts。

这一层面向机器、开发、审计和复核，不等于最终用户报告。

### Canonical Report Model

作为事实与报告语义的共享基础，必须保留：

- task scope；
- identity；
- facts；
- Evidence references；
- limitations；
- unknowns；
- human-review state；
- source index。

### Presentation Layer

未来新增的明确边界：

```text
Canonical Report Model
        ↓
Visibility / information hierarchy policy
        ↓
User-facing View Model
        ├── Interactive HTML
        └── Fixed PDF
```

Presentation Layer 可以：

- 重排信息；
- 改变默认展开状态；
- 隐藏 machine-only 字段；
- 生成摘要视图；
- 生成 PDF 固定阅读结构。

Presentation Layer 不得：

- 补造研究事实；
- 删除 material limitation；
- 提高来源等级；
- 把 unknown 改为 known；
- 把 not_started human review 改为 reviewed；
- 修改底层 Evidence。

详细三层 visibility policy 见 `references/report-experience-and-information-architecture.md`。

## Three-layer visibility model

### Layer 1 — Default user view

回答：

- Who is this arbitrator?
- What key facts were verified?
- What is practically relevant?
- What important matters remain unconfirmed?
- Does the user need to decide anything next?

### Layer 2 — On-demand evidence view

显示：

- sources；
- key excerpts；
- relevant limitations；
- Evidence mapping；
- uncertainty / human-review status where useful。

### Layer 3 — Internal system record

保存但默认隐藏：

- SHA-256；
- local paths；
- retrieval timestamps；
- snapshot paths/levels；
- parser/extraction metadata；
- receipts；
- token/cost/performance；
- internal governance evidence；
- repetitive validation fields。

Internal data that materially affects report reliability must be translated to a user-facing limitation before promotion to Layer 1/2.

## Interactive HTML

未来定位为主要工作版。

交互只影响 presentation state，例如：

- expand/collapse Evidence；
- module navigation；
- filter unknowns；
- show sources；
- focus on unresolved items。

如未来允许用户做：

- review complete；
- lawyer note；
- accepted risk；
- follow-up requested；

应新增独立 annotation/review-state model，而不是修改原始 Evidence。

## Fixed PDF

未来定位为正式固定交付版。

必须：

- 与 HTML 共享 Canonical facts；
- 固定 version / cutoff date；
- 保留 material unknowns；
- 保留 traceable source index；
- 支持归档与离线阅读；
- 不默认打印 Layer 3 machine audit fields。

PDF 不是 HTML DOM 的简单 print-to-PDF；它可以使用不同布局，但不能使用不同事实。

## Current implementation status

当前 Renderer 仍接近“Canonical/Evidence 审计视图”，尚未实现独立 Presentation Layer。

第一名真人样本已经显示这一限制：

- 9 final Evidence；
- 17-page PDF；
- 大量 local_path / retrieval / snapshot / hash 等 machine fields 被直接呈现。

因此未来 UX/UI 的技术工作重点应是：

1. 建立 Presentation View Model；
2. 保证 Layer 1/2/3 visibility；
3. HTML 交互；
4. PDF 固定版；
5. 证明 HTML/PDF 的事实一致性。

当前未授权实现该层，不修改现有 Renderer、Schema 或 Evidence contract。

## Future design artifacts

正式启动 UX/UI 后：

- `PRD.md`：用户目标与验收；
- `references/report-experience-and-information-architecture.md`：信息层与 visibility policy；
- `ARCHITECTURE.md`：Presentation Layer 技术边界；
- `REPORT_DESIGN.md`：HTML interaction + PDF visual/component spec；
- `PROJECT_BRIEF.md`：阶段和 Gate。

Material changes 记录 Before / After / Why / Source-Evidence / Affected Scope。