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
Markdown / HTML / PDF
```

## Current layers

### Core

负责工作流、证据规则、判断边界、Schema、Validator 和 Evals。当前实现包括 `schemas/evidence.schema.json`、`scripts/validate_evidence.py`、测试和合成示例。

### Capability Layer

概念上承载 Search、Fetch、Snapshot、Document Extraction、Entity Resolution、Viewpoint Analysis、Relationship Analysis、Validation 和 Rendering。当前已实现静态来源、基于随包 pypdf 的数字原生 PDF 提取、authorized real research run 与结构化报告输出；PDF 使用当前已 Gate PASS 的 ReportLab 路径。

Capability 原则为 **Bundled First, Host Enhanced**：基础能力尽可能随 Skill 提供，宿主已有能力可以增强，但不要求普通用户另行安装项目或购买服务。

### Project Layer

当前只有 CIETAC，用于承载机构规则、机构特定来源及规则差异。当前不建立其他仲裁机构目录。

### Output

Evidence JSON 是研究结果与报告之间的事实基础。Markdown / HTML / PDF Renderer 只消费同一 Canonical Report Model，不承担研究、事实补充、来源评级或不确定性改写职责。

## Evidence / presentation separation

系统记录与用户呈现必须分层。

```text
Evidence / Snapshot / audit / performance
        ↓
Canonical Report Model
        ↓
Presentation policy / view mapping
        ↓
User-facing Markdown / HTML / PDF
```

其中：

- Evidence、Snapshot、运行审计和 performance 数据保持完整；
- 用户可见报告只展示完成任务所需的信息；
- presentation 层可以隐藏机器噪音，但不能删除或改写事实、unknown、coverage gap、来源限制和人工复核状态；
- internal-only 字段在实质影响报告可靠性时，应转译成用户可理解的限制；
- user-facing view 不能反向修改 Evidence 或提高来源等级。

当前实现仍主要由 Renderer 直接呈现 Canonical Report Model；独立 presentation policy / view model 尚未实现。未来 UX/UI 项目如需新增该层，必须另行授权并验证不会改变事实源。

详细信息层级和可见性规则见 `references/report-experience-and-information-architecture.md`。

## Future report UX/UI boundary

正式进入 PDF / HTML UX/UI 项目后：

- `PRD.md` 定义用户需求和验收；
- `references/report-experience-and-information-architecture.md` 定义信息层级和 visibility policy；
- 新建 `REPORT_DESIGN.md` 定义视觉层级、组件、分页、状态语义和 accessibility；
- 本文件只记录数据流、呈现层边界和实现影响；
- `PROJECT_BRIEF.md` 只记录阶段/Gate，不复制设计正文。

视觉改版必须保留同一事实源，不得让 PDF / HTML 各自补造内容。

## Current implementation boundary

当前没有数据库、后台服务、独立 UI、外部 API 或多 Agent 调度平台。authorized real research run 已通过独立审查，当前优先完成第一名真实完整链路。

报告 UX/UI 尚未启动。不会在取得真实报告样本前，为视觉设计提前修改 Canonical Report Model、Evidence Schema 或 Renderer 内容合同。
