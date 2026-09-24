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

概念上承载 Search、Fetch、Snapshot、Document Extraction、Entity Resolution、Viewpoint Analysis、Relationship Analysis、Validation 和 Rendering。当前不选择具体第三方项目、不创建完整 Capability 框架；本轮不决定 OpenCLI、Jev、浏览器项目、搜索框架或数据库。

Capability 原则为 **Bundled First, Host Enhanced**：基础能力尽可能随 Skill 提供，宿主已有能力可以增强，但不要求普通用户另行安装项目或购买服务。

### Project Layer

当前只有 CIETAC，用于承载机构规则、机构特定来源及规则差异。当前不建立其他仲裁机构目录。

### Output

Evidence JSON 是研究结果与报告之间的事实基础。未来 Renderer 只渲染结构化结果，不承担研究、事实补充、来源评级或不确定性改写职责。

## Current implementation boundary

当前没有数据库、后台服务、UI、外部 API 或多 Agent 调度平台。V0.2 只固定 Evidence Foundation；后续能力须经过单独范围和来源评估。
