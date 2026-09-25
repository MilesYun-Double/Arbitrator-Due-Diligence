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

概念上承载 Search、Fetch、Snapshot、Document Extraction、Entity Resolution、Viewpoint Analysis、Relationship Analysis、Validation 和 Rendering。当前已实现静态来源、基于随包 pypdf 的数字原生 PDF 提取与结构化报告输出；本轮验证基于随包 ReportLab 的 PDF Renderer 候选。不创建完整 Capability 框架，不接入 OpenCLI、Jev、浏览器项目、搜索框架或数据库。

Capability 原则为 **Bundled First, Host Enhanced**：基础能力尽可能随 Skill 提供，宿主已有能力可以增强，但不要求普通用户另行安装项目或购买服务。

### Project Layer

当前只有 CIETAC，用于承载机构规则、机构特定来源及规则差异。当前不建立其他仲裁机构目录。

### Output

Evidence JSON 是研究结果与报告之间的事实基础。现有 Markdown / HTML Renderer 及本轮 PDF Renderer 候选只渲染同一 Canonical Report Model，不承担研究、事实补充、来源评级或不确定性改写职责。

## Current implementation boundary

当前没有数据库、后台服务、UI、外部 API 或多 Agent 调度平台。V0.2 Evidence Foundation 及 Issue #6 / #7 / #8 已通过正式 Gate；当前只推进 Canonical Report Model → PDF 与计时/打包验证，其他后续能力仍须单独授权。
