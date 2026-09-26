# Report Experience and Information Architecture

## 目的

本文件定义 Arbitrator Due Diligence 最终报告的信息架构、系统留存边界，以及 HTML / PDF 双交付方向。

核心原则：

> **MACHINE PRECISION, HUMAN CLARITY**
>
> 系统完整记录；用户按需看见。

Evidence、Snapshot、审计和性能记录不得因为界面简化而删除。用户报告只显示完成法律工作所需的信息。

## 最终三层信息模型

### Layer 1 — 用户默认看到

HTML 首屏/主流程和 PDF 主体优先回答：

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
   - 只基于已核验公开事实说明业务相关性；
   - 不预测偏向、胜诉率或哪一方更有利；
   - 不把名册专业栏目直接升级成能力评价。

4. **哪些重要事项尚未确认**
   - material coverage gaps；
   - 来源冲突；
   - 身份或任期不确定；
   - 尚未独立核验的机构自述；
   - human_review 尚未完成；
   - 未执行的模块。

当前不提供“复核、补查、备注、接受风险”等交互动作。Layer 1 只呈现信息与状态，不建立用户写回工作流。

### Layer 2 — 需要时展开

用户主动展开、点击或查看附录时展示：

- 来源标题与发布主体；
- 来源类型；
- 原始 URL；
- Evidence ID；
- 关键原文引用；
- 必要 excerpt locator；
- 与结论直接相关的 limitations；
- uncertainty；
- human_review 状态（仅作为状态展示）；
- 同一事实的支持来源关系。

HTML 可使用折叠、展开、侧栏、drawer、modal 或等价**只读交互**。

PDF 可使用紧凑脚注、来源注、证据附录或来源索引。

目标：

> 用户可以从结论追到证据，但不要求阅读完整机器 Evidence JSON。

### Layer 3 — 系统保存，不默认展示

系统必须完整保存，但默认不进入普通用户 HTML 主流程或 PDF 主体：

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

这些数据用于审计、复现、排障、性能优化、独立审查和产品验证，不是普通律师的默认阅读内容。

## Internal → User Promotion Rule

Layer 3 的内部事实如果实质影响用户对报告可靠性的理解，必须转译后提升到 Layer 1/2，而不是直接显示机器错误。

| 系统内部事实 | 用户看到 |
|---|---|
| collector / parser error | “该来源未能可靠提取，因此相关事实本次未据此确认。” |
| PDF page extraction error | “该页内容未能可靠取得；不能据此判断相关信息不存在。” |
| source hash mismatch | “材料完整性与预期版本不一致，本次未将其用于证据。” |
| unresolved_same_name | “存在同名对应风险，相关履历尚不能安全合并。” |
| human_review = not_started | “该项尚未人工复核。” |
| viewpoints disabled | “本次未执行专项观点检索。” |
| conflicts disabled | “本次未进行针对具体案件主体的关系比对。” |
| token / timing / Git / runtime | 默认不展示，除非用户明确请求技术/性能信息 |

原则：

> **展示影响，不展示机器噪音。**

## 最终交付形态

### 1. Interactive HTML — 只读工作版

未来作为主要阅读与核验界面。

当前允许的交互范围：

- 展开 / 收起 Evidence；
- 模块导航；
- 查看来源；
- 过滤或聚焦 unknown / coverage gaps；
- 在页面内跳转；
- 只读查看同一事实的证据对应关系。

当前明确不做：

- 标记“已复核”；
- 发起“补查”；
- 添加备注 / 批注；
- 接受风险；
- 修改 Evidence；
- 写回任何研究或业务状态；
- 用户账户、协作、审批流。

也就是说：

> **HTML 当前是可交互阅读，不是可编辑工作流。**

### 2. PDF — 固定版 / 交付版

继续作为正式、稳定、可归档交付物：

- 发给客户；
- 内部归档；
- 邮件附件；
- 案件卷宗；
- 固定某一检索截止时间的研究结果；
- 离线阅读。

PDF 应：

- 与 HTML 使用同一 Canonical Report Model；
- 固定检索截止时间和报告版本；
- 保留主要限制和未确认事项；
- 保留可追溯来源索引；
- 不展示绝大多数 Layer 3 机器字段。

PDF 不是 HTML 的“全部展开后打印”，可以使用不同布局，但事实源必须一致。

### 3. Markdown — 内部/兼容输出

用于：

- 调试；
- diff；
- portable text；
- Agent / Reviewer 辅助。

当前不作为主要终端用户交付物。

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
- 来源详情默认是否展开。

不允许：

- 两端出现不同事实；
- 任一端自行补充研究结论；
- 来源等级、不确定性或 material limitation 不一致。

## 当前真人报告提供的设计证据

第一名真实报告：

- 9 个 final Evidence；
- 17 页 PDF；
- 当前 Renderer 将大量 Evidence machine fields 平铺展示。

真实报告中已经出现 local_path、retrieved_at、retrieval_notes、snapshot path、SHA-256、parser/extraction metadata。

这些字段证明当前 Renderer 更接近“审计视图”，尚不是理想的最终用户视图。

未来 UX/UI 的第一目标不是装饰，而是：

> **建立 Presentation Layer，把审计模型转换成用户阅读模型，同时保持底层 Evidence 完整。**

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

## 文件职责

- `PRD.md`：用户目标、HTML/PDF 双交付、只读交互范围与验收。
- 本文件：Layer 1/2/3、visibility policy、internal-to-user promotion。
- `ARCHITECTURE.md`：Evidence → Canonical → Presentation → HTML/PDF 技术边界。
- `REPORT_DESIGN.md`：当前不创建；正式启动 UX/UI 后再定义版式、组件和只读交互细节。
- `PROJECT_BRIEF.md`：只记录方向、阶段和 Gate。

## UX/UI 变更记录

Material UX/UI 变化至少记录：

- Before；
- After；
- Why；
- Source / Evidence；
- Affected Scope；
- Acceptance / observed result。

## 当前状态

当前只确认产品方向：

- **Interactive HTML（只读交互） + PDF** 双交付；
- 信息架构采用三层；
- Markdown 保留为内部/兼容输出；
- 复核/补查/备注/审批等写入型能力明确不做；
- 尚未授权 UI 实现、Renderer 重构或 REPORT_DESIGN.md。
