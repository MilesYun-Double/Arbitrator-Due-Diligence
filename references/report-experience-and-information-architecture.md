# Report Experience and Information Architecture

## 目的

本文件是 Arbitrator Due Diligence 报告呈现层的信息架构与可见性规则。

它回答两个问题：

1. 系统必须完整保留什么；
2. 最终用户在 Markdown / HTML / PDF 报告中应该看到什么。

本文件不修改 Evidence Schema，不降低证据留存要求，也不直接规定当前 PDF 的视觉样式。未来单独进入报告 UX/UI 阶段时，再基于真实报告样本创建 `REPORT_DESIGN.md`，定义视觉层级、组件、版式和验收。

## Vibe Loop 设计原则

本报告 UX/UI 遵循 Vibe Loop 的 **MACHINE PRECISION, HUMAN CLARITY**：

- 对内保持机器可审计、可追溯、可复算；
- 对外先给用户能理解和能行动的信息；
- 技术证据和机器字段与用户正文分离；
- 不用“界面简洁”作为删除 Evidence、限制、来源或未知状态的理由；
- 变化本身是知识：未来重要 UX/UI 变更要记录 Before / After / Why / Source-Evidence / Affected Scope；
- 当前环境、能力或覆盖只在实际验证范围内表达，不把内部 PASS 外推成用户不需要的技术宣传。

## 文件职责

### PRD.md

负责用户侧产品要求：

- 报告的目标用户；
- 用户必须看到的内容；
- 用户不应被机器细节淹没；
- 信息层级、可读性、可复核性和交付体验的验收标准。

### references/report-experience-and-information-architecture.md

本文件负责：

- 信息分层；
- 可见性规则；
- internal-only 与 user-facing 的映射；
- 哪些内部事实在何种条件下必须提升为用户可见限制。

### ARCHITECTURE.md

负责：

- Evidence / Canonical Model / Presentation 之间的边界；
- 内部记录不能被 Renderer 删除；
- user-facing view 不能反向改写 Evidence；
- 未来 presentation policy / view model 的实现位置。

### REPORT_DESIGN.md

**现在不创建。**

只有在主控正式启动 PDF / HTML UX/UI 项目后创建，用于：

- 页面结构；
- 视觉层级；
- typography；
- spacing；
- table / timeline / source index / evidence reference 的组件规范；
- warning / limitation / unknown 状态的视觉语义；
- PDF 分页、页眉页脚、长链接、跨页表格；
- accessibility；
- Before / After 对比和 UX 验收。

视觉规则不得写入 Evidence Schema。

### PROJECT_BRIEF.md

只记录：

- 当前阶段；
- UX/UI 项目是否已经获准；
- 当前设计 Gate；
- 下一授权动作。

不在 PROJECT_BRIEF 中维护详细设计规则。

## 信息分层

### Layer 1 — 用户核心正文

默认进入交付报告主体。

包括：

- 本次任务范围；
- 启用 / 未启用的功能；
- 身份核对结果；
- 专业背景；
- 当前及重要历史任职；
- 可核验公开著作 / 专业材料；
- 一般公开专业关系事实；
- 与事实判断直接相关的重要时间线；
- 重要 coverage gap / unknown；
- 用户需要关注的人工复核事项；
- 来源索引。

目标：

> 用户先理解“我们查到了什么、哪些可靠、哪些还不知道、下一步要人工确认什么”。

不得把内部运行状态当成用户正文。

### Layer 2 — 用户证据与复核层

默认可在报告后半部、脚注、来源索引或证据附录中展示。

包括：

- Evidence ID；
- 来源标题；
- 发布主体；
- 来源类型；
- 原始 URL；
- 发布 / 事件日期；
- 必要原文摘录；
- 页码 / 段落 / locator；
- 与该事实直接相关的 limitation；
- human review 状态（当它影响用户判断时）。

目标：

> 用户能从报告结论回到来源，但不要求阅读系统完整 Evidence JSON。

### Layer 3 — 条件性用户警示层

只有在影响用户理解、信赖程度或后续动作时进入用户报告。

例如：

- 身份未完全消歧；
- 同名风险；
- 关键来源互相冲突；
- 关键原文不可取得；
- 只有摘要；
- 页面失效；
- 核心 PDF / 页面无法稳定提取；
- 重要模块未执行；
- 证据尚未人工复核；
- coverage gap 足以影响主要结论。

表达方式遵循 Human Clarity：

- 先说对用户的影响；
- 再说已知事实；
- 最后说需要什么复核；
- 不把 stack trace、exit code、内部路径直接扔给用户。

未来 UX/UI 可以把这些设计为高辨识度但不过度惊扰的语义卡片；颜色不能是唯一语义载体。

### Layer 4 — 系统内部审计记录

**系统必须保留，但默认不进入用户 PDF 正文。**

包括：

- research-run contract / marker；
- staging provenance；
- 本地绝对路径；
- source / snapshot SHA-256；
- Git commit / worktree 状态；
- dependency / artifact hash；
- validator / renderer 技术版本；
- 命令、参数、exit code；
- raw stack trace / raw error；
- retry 明细；
- DNS / SSRF / robots 技术检查；
- package closure；
- token usage；
- actual / estimated cost；
- performance.json；
- search/retrieval step timing；
- benchmark profile；
- internal Gate / Reviewer 状态；
- synthetic / regression test receipts；
- 机器环境细节。

这些信息的价值是：

- 审计；
- 复现；
- 排障；
- 性能优化；
- 开发验收；
- 独立审查。

不是普通报告用户阅读任务。

### Layer 5 — Internal-to-User Promotion

Layer 4 的内部事实如果**实质影响报告可靠性或用户下一步动作**，必须提升为 Layer 3 的用户可见限制，但要翻译成人话。

示例：

| 系统内部记录 | 用户报告中的表达 |
|---|---|
| `ModuleNotFoundError` / collector exit 2 | “该来源未能进入稳定提取流程，因此相关事实未据此确认。” |
| PDF page extraction error | “该页内容未能可靠提取；不据此判断该信息不存在。” |
| source hash mismatch | “本地材料完整性与预期版本不一致，本次未使用该材料作为证据。” |
| identity_resolution = unresolved_same_name | “存在同名/身份对应风险，相关履历尚不能安全合并。” |
| human_review = not_started | “该项尚待人工复核。” |
| viewpoints disabled | “本次未执行专项观点检索。” |
| conflicts disabled | “本次未进行针对具体案件主体的关系比对。” |
| token / timing / Git / runtime 信息 | 默认不展示；除非用户明确询问性能或技术验证 |

原则：

> 展示“影响”，不展示无关的机器噪音。

## 用户正文中默认不展示的提示

以下内容即使系统已记录，也默认不进入最终尽调 PDF 主体：

- “Validator PASS”；
- “101 tests PASS”；
- Git commit SHA；
- package SHA；
- Pillow 是否加载；
- pypdf / ReportLab 版本；
- Windows / Python 版本；
- synthetic / real-run marker；
- staging 路径；
- 本地 `reports/` 路径；
- token 消耗；
- benchmark 分数；
- 搜索工具名称；
- 内部 retry 次数；
- 原始 traceback；
- Reviewer / Gate 流程。

例外：

- 用户明确要求技术审计报告；
- 某项机器事实直接影响当前尽调可靠性，此时按 Layer 5 翻译后展示。

## 用户报告中的“不确定性”不能隐藏

以下虽然可能影响视觉简洁度，但不得因为 UX/UI 而删除：

- unknown；
- unresolved lead；
- identity conflict；
- coverage gap；
- source conflict；
- unavailable source；
- not reviewed；
- 未执行模块；
- 支撑范围限制。

UX/UI 的任务是让这些信息更容易理解，而不是让报告看起来更“确定”。

## 未来 PDF / HTML UX/UI 项目启动 Gate

只有主控正式授权后才进入 UX/UI 项目。

启动时至少需要：

1. 一份真实完整报告样本；
2. 用户侧阅读目标与主要使用场景；
3. 当前报告长度、Evidence 数、Source Index 规模；
4. 已发现的阅读问题；
5. 需要保留的 internal / user-visible 边界；
6. 明确的视觉/信息架构验收标准。

UX/UI 任务开始后：

```text
PRD user requirements
+ 本文件 information layers
+ current real report sample
↓
REPORT_DESIGN.md
↓
design / implementation
↓
before-after evidence
↓
PDF / HTML acceptance
```

不得先凭审美重做 Renderer，再反向修改产品规则。

## UX/UI 变更记录

每项 materially visible 变化至少记录：

- Before；
- After；
- Why；
- Source / Evidence；
- Affected Scope；
- Acceptance / observed result。

例如：

> Before：Evidence 原始字段全部平铺在正文。  
> After：用户正文只显示结论必要信息，完整 Evidence 保留在系统记录与来源附录。  
> Why：降低认知负担，但不牺牲审计可追溯性。  
> Source/Evidence：真实用户报告阅读结果 / 明确用户反馈。  
> Affected Scope：PDF + HTML presentation only；Evidence JSON unchanged。

## 当前状态

本文件只记录未来报告 UX/UI 的设计约束。

当前没有授权：

- 重做 PDF 视觉；
- 修改 Canonical Report Model；
- 删除或隐藏 Evidence 记录；
- 创建前端/UI；
- 变更 Renderer 内容合同。

当前优先级仍是完成第一名真实完整链路并取得真实报告样本。
