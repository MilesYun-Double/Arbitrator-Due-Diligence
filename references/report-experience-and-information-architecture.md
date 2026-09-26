# Report Experience and Information Architecture

## 目的

本文件定义 Arbitrator Due Diligence 最终报告的用户信息架构、系统留存边界，以及未来 HTML / PDF 双交付形态。

核心原则：

> **MACHINE PRECISION, HUMAN CLARITY**
>
> 系统完整记录；用户按需看见。

Evidence、Snapshot、审计和性能记录不得因为界面简化而删除。用户报告只显示完成法律工作所需的信息。

## 最终三层信息模型

### Layer 1 — 用户默认看到

这是 HTML 首屏/主流程和 PDF 主体默认展示的内容。

必须优先回答：

1. **这个仲裁员是谁**
   - 姓名及必要身份消歧；
   - 当前可核实身份；
   - 与固定候选的对应关系。

2. **核实到哪些关键事实**
   - 专业背景；
   - 重要任职和执业信息；
   - 专业领域；
   - 已核验的公开专业材料；
   - 已核验的一般公开专业关系。

3. **这些事实与选择/使用他有什么实际相关性**
   - 只允许基于已经核验的公开事实说明其业务相关性；
   - 不预测偏向、胜诉率或哪一方更有利；
   - 不把机构名册专业领域直接升级成能力评价。

4. **哪些重要事项尚未确认**
   - material coverage gaps；
   - 来源冲突；
   - 身份或任期不确定；
   - 尚未独立核验的机构自述；
   - 尚未完成的人工复核；
   - 未执行的模块。

5. **是否需要用户进一步决定**
   - 是否补做专项观点检索；
   - 是否提供案件主体做公开冲突线索核查；
   - 是否要求人工律师复核；
   - 是否接受当前有限覆盖。

目标：

> 用户先得到“能不能用这份报告做下一步判断”的答案，而不是先阅读 Evidence 数据结构。

### Layer 2 — 需要时展开

这是用户主动展开、点击或查看附录时看到的证据复核层。

包括：

- 来源标题与发布主体；
- 来源类型；
- 原始 URL；
- Evidence ID；
- 关键原文引用；
- 关键 excerpt locator；
- 与结论直接相关的 limitations；
- uncertainty；
- human review 状态；
- 同一事实的支持来源关系。

HTML 中应以折叠、展开、侧栏、drawer、modal 或等价交互呈现。

PDF 中应以紧凑脚注、来源注、证据附录或来源索引呈现。

目标：

> 用户可以从结论追到证据，但不要求阅读完整机器 Evidence JSON。

### Layer 3 — 系统保存，不默认展示

系统必须完整保存，但默认不进入普通用户 HTML 主流程或 PDF 主体。

包括：

- SHA-256；
- local path；
- retrieval timestamp；
- snapshot path / level；
- parser / extraction metadata；
- pypdf / ReportLab / runtime 版本；
- staging provenance；
- research-run contract / marker；
- Git revision / worktree 状态；
- execution receipts；
- command / exit code；
- raw traceback / raw error；
- retry 明细；
- token usage；
- cost；
- performance benchmark；
- internal Gate / Reviewer records；
- package closure / synthetic regression evidence；
- 重复的 machine validation 字段。

这些数据用于：

- 审计；
- 复现；
- 排障；
- 性能优化；
- 独立审查；
- 产品验证。

普通律师阅读报告不需要理解这些机器字段。

## Internal → User Promotion Rule

Layer 3 的内部事实如果**实质影响用户对报告可靠性的理解或下一步动作**，必须转译后提升到 Layer 1，而不是直接显示机器错误。

示例：

| 系统内部事实 | 用户看到 |
|---|---|
| collector exit 2 / parser error | “该来源未能可靠提取，因此相关事实本次未据此确认。” |
| PDF page extraction error | “该页内容未能可靠取得；不能据此判断相关信息不存在。” |
| source hash mismatch | “材料完整性与预期版本不一致，本次未将其用于证据。” |
| identity_resolution = unresolved_same_name | “存在同名对应风险，相关履历尚不能安全合并。” |
| human_review = not_started | “该项尚待人工复核。” |
| viewpoints disabled | “本次未执行专项观点检索。” |
| conflicts disabled | “本次未进行针对具体案件主体的关系比对。” |
| token / timing / Git / runtime | 默认不展示，除非用户明确请求技术/性能信息 |

原则：

> **展示影响，不展示机器噪音。**

## 最终交付形态

### 1. Interactive HTML — 工作版 / 交互版

未来建议作为主要阅读与工作界面。

适合：

- 案件团队日常阅读；
- 快速扫描关键事实；
- 展开 Evidence；
- 来源跳转；
- 只看未确认事项；
- 只看某一模块；
- 查看用户下一步决策；
- 后续加入人工复核/批注能力（如获单独授权）。

建议交互结构：

- Summary / 关键结论；
- Identity；
- Background & Appointments；
- Professional Materials；
- Public Professional Relationships；
- Important Unknowns / Coverage Gaps；
- User Decisions / Next Actions；
- Sources / Evidence（可展开）。

HTML 的交互只能改变**展示状态**，不能在没有明确产品设计时直接修改原始 Evidence。

如果未来增加“律师已复核”“备注”“接受风险”等交互，应使用独立 user annotation / review state，而不是修改历史 Evidence 内容。

### 2. PDF — 固定版 / 交付版

继续保留为正式、稳定、可归档的交付物。

适合：

- 发给客户；
- 内部归档；
- 邮件附件；
- 案件卷宗；
- 固定某一检索截止时间的研究结果；
- 离线阅读。

PDF 应：

- 与 HTML 使用同一 Canonical Report Model；
- 固定检索截止时间；
- 固定报告版本；
- 保留主要限制和未确认事项；
- 保留可追溯来源索引；
- 不展示绝大多数 Layer 3 内部机器字段。

PDF 不是 HTML 的“打印整个展开状态”，而是独立设计的固定阅读版，但事实源必须一致。

### 3. Markdown — 内部/兼容输出

Markdown 可继续作为：

- 调试；
- diff；
- portable text；
- 开发/审查辅助。

当前不把 Markdown 定义为主要终端用户交付物。

## HTML / PDF 一致性

二者必须共享：

- candidate identity；
- task scope；
- enabled / disabled modules；
- core facts；
- Evidence references；
- limitations；
- unknowns；
- human-review state；
- source index；
- report version / cutoff date。

允许不同：

- 信息密度；
- 折叠/展开；
- 导航；
- 视觉层级；
- 用户操作；
- 来源详情默认是否展开。

不允许：

- HTML 有一个事实而 PDF 没有对应事实且无设计理由；
- PDF 自行补充 HTML 没有的研究结论；
- 两边出现不同的来源等级或不确定性；
- 为了缩短 PDF 隐藏 material limitations。

## 当前真人报告提供的设计证据

第一名真实报告：

- 9 个 final Evidence；
- 17 页 PDF；
- 当前 Renderer 将大量 Evidence machine fields 平铺展示。

真实报告中已经出现：

- local_path；
- retrieved_at；
- retrieval_notes；
- snapshot path；
- SHA-256；
- parser/extraction metadata。

这些字段证明当前 Renderer 是“审计视图”，尚不是理想的最终用户视图。

因此未来 UX/UI 的第一目标不是视觉装饰，而是：

> **建立 presentation layer，把审计模型转换成用户阅读模型，同时保持底层 Evidence 完整。**

## 用户报告中绝不能因 UX 隐藏

即使追求简洁，以下仍必须进入 Layer 1 或 Layer 2：

- material unknown；
- unresolved identity；
- source conflict；
- coverage gap；
- unavailable material；
- not reviewed；
- 未执行模块；
- 与结论直接有关的 limitation；
- 影响用户判断的来源可靠性限制。

UX/UI 的任务是降低认知负担，不是制造确定感。

## 文件职责

### PRD.md

定义：

- 用户目标；
- HTML / PDF 双交付需求；
- 三层信息结构；
- 用户体验验收。

### 本文件

定义：

- Layer 1 / 2 / 3；
- internal-to-user promotion；
- HTML / PDF 信息行为；
- visibility policy。

### ARCHITECTURE.md

定义：

- Evidence → Canonical → Presentation View → HTML/PDF 的技术边界；
- user view 不得反向修改 Evidence。

### REPORT_DESIGN.md

**当前不创建。**

正式启动 UX/UI 后再建立，用于：

- 页面/屏幕结构；
- PDF 页面结构；
- typography；
- spacing；
- cards；
- timeline；
- source/evidence component；
- limitation / unknown semantic treatment；
- HTML interaction；
- responsive behavior；
- accessibility；
- PDF pagination；
- Before / After 验收。

### PROJECT_BRIEF.md

只记录阶段、Gate 和下一授权动作。

## UX/UI 变更记录

Material UX/UI 变化至少记录：

- Before；
- After；
- Why；
- Source / Evidence；
- Affected Scope；
- Acceptance / observed result。

例：

> Before：17 页 PDF 将完整 Evidence 字段平铺给用户。  
> After：用户默认只看到关键事实与重要未知；Evidence 按需展开；machine audit fields 只保留系统记录。  
> Why：真实样本显示 Evidence 仅 9 条即形成 17 页，阅读负担过高。  
> Affected Scope：Presentation / HTML / PDF；Evidence JSON unchanged。

## 当前状态

当前只确认产品方向：

- 最终优先考虑 **Interactive HTML + PDF** 双交付；
- 信息架构采用三层；
- Markdown 保留为内部/兼容输出；
- 尚未授权 UI 实现、Renderer 重构或 REPORT_DESIGN.md；
- 当前继续优先完成并 Gate 第一名真人链。