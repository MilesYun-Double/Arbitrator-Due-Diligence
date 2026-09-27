# Report Content Standard

## 1. Purpose

本文件定义 Arbitrator Due Diligence 用户报告中不同内容类型的语义职责、写作规则、默认可见层以及与 Evidence 的映射关系。

目标：

- 用户先理解研究结果，而不是阅读机器字段；
- 每个重要发现都可以追溯到 Evidence；
- 事实、解释、来源与限制不混写；
- 不因压缩报告而隐藏 material unknown、coverage gap 或重要限制；
- HTML 与 PDF 使用同一事实与内容语义。

本文件不定义颜色、字体、卡片视觉、页面尺寸或具体布局；这些属于后续 `REPORT_DESIGN.md`。

## 2. Governing Principles

### 2.1 Machine Precision, Human Clarity

系统继续完整保存 Evidence、Snapshot、provenance、hash、retrieval / extraction metadata、execution receipts 和 performance records。

用户报告只显示完成阅读、理解和核验所需要的信息。

如果内部机器信息实质影响报告可靠性，必须把其“影响”翻译成用户可理解的限制，而不是直接把机器字段平铺给用户。

### 2.2 Single-page Continuous Reading

Interactive HTML 必须是一份连续的单页长文档。

主要阅读方式：

> 自上而下纵向滚动。

允许：

- 同页目录；
- anchor 页面内跳转；
- Evidence 局部展开 / 收起；
- 查看原始来源；
- 回到顶部；
- 聚焦未确认事项。

禁止：

- tabs；
- 多标签页；
- 把身份、关键事实、unknown、sources 拆成不同内部页面；
- 需要用户在多个页面或标签之间来回切换才能完成主要阅读。

外部来源链接可以打开原始来源；这不属于报告内部的信息架构。

## 3. Standard Reading Order

一份完整报告原则上按以下顺序连续阅读：

1. Document Identity / Report Scope
2. Executive Summary / 主要发现摘要
3. Candidate Identity / 身份核对
4. Key Findings / 关键发现
5. Module Status / 未执行模块说明
6. Sources & Evidence / 来源与证据
7. Important Unknowns & Limitations / 重要未确认事项与限制

Important Unknowns & Limitations 必须位于整份用户报告的最下方。

Executive Summary 可以提示“存在重要未确认事项，详见页末”，但不重复展开完整限制内容。

未执行模块不得生成空白分析章节。

## 4. Content Types

### 4.1 Document Title

**用户目的**

告诉用户这是什么报告，以及研究对象是谁。

**内容**

- Arbitrator Due Diligence；
- 仲裁员姓名；
- 必要的中英文名称。

**默认层级**

Layer 1。

**写作规则**

简短、中性、描述性。

**禁止事项**

不得使用可能误导报告性质的名称，例如：

- 推荐报告；
- 仲裁员评估意见；
- 选任意见；
- 法律意见书。

---

### 4.2 Report Status / Scope Line

**用户目的**

让用户在开始阅读前理解本次到底查了什么、没有查什么，以及资料检索截至何时。

**至少包括**

- 研究类型；
- 已启用模块；
- 未启用模块；
- 检索截止日期 / 时间；
- 必要的整体研究状态。

**不包括**

- 报告版本号；
- “v1 / v2 / 修订版”等进化式版本语义。

每次用户报告均视为一次独立生成结果，不建立“报告版本演进”概念。

内部系统如需保存 run_id、commit、执行标识等，继续留在 Layer 3，不进入普通用户 Scope Line。

**示例**

> 本次执行基础公开尽调；未执行专项观点检索及针对具体案件主体的关系比对。公开资料检索截至 YYYY-MM-DD。

**禁止事项**

不得把：

> 未执行冲突核查

写成：

> 未发现冲突。

---

### 4.3 Executive Summary / 主要发现摘要

**用户目的**

用户只阅读这一部分，也应能够理解：

1. 这个人是谁；
2. 最重要的核实结果是什么；
3. 哪些事实与律师的选择或使用判断具有实际相关性；
4. 是否存在重要未确认事项。

**内容**

原则上只保留：

- 身份结论；
- 3–6 项主要发现；
- 必要的实际相关性说明；
- 如存在 material unknown，仅作简短提示并指向页末完整区块。

**写作规则**

结论先行，不复制整个正文。

正文负责证明和解释摘要中的内容。

**禁止事项**

不得形成：

- 推荐 / 不推荐；
- 适合 / 不适合担任本案仲裁员；
- 偏向某方；
- 胜诉概率；
- 自动选人结论。

---

### 4.4 Section Heading / 章节标题

**用户目的**

告诉用户下面讨论哪一类问题。

**示例**

- 身份核对
- 专业背景与任职
- 公开专业材料
- 公开专业关系

Section Heading 只负责分类，不承担具体事实结论。

---

### 4.5 Finding Heading / 发现标题

**用户目的**

用一句话直接告诉用户：

> 这一项研究实际发现了什么。

Finding Heading 是报告正文的基本阅读单位。

**写作规则**

- 基于已经进入 Evidence 的事实；
- 一般只表达一个核心发现；
- 优先使用具体主体、行为或状态；
- 时间口径不确定时必须反映这种不确定性；
- 应尽量让标题本身能够独立表达 takeaway。

**示例**

不优先使用：

> 任职经历

优先使用：

> 某大学当前公开页面列示其为兼职教授

**禁止事项**

不得把事实升级成无依据评价。

例如 Evidence 只能支持“名册将其专业领域列为工程相关领域”时，不得写：

> 在工程争议领域经验丰富。

---

### 4.6 Fact / 已核实事实

**用户目的**

说明来源实际上支持什么。

**写作规则**

Fact 必须尽可能靠近原始 Evidence 能支持的范围。

优先写：

> 某公开页面列示……

> 某官方名册记载……

> 某机构个人简介记载……

而不是：

> 已完全确认其……

来源只是个人简介时，不得因其位于机构网站而自动升级为机构对全部履历的独立认证。

---

### 4.7 Explanation / Practical Relevance

**用户目的**

告诉律师为什么这个公开事实可能值得注意。

这不是重复 Fact，也不是给出选人建议。

**可以说明**

- 某段专业经历与特定专业领域存在直接关联；
- 某公开任职有助于理解其职业背景；
- 某公开材料涉及用户明确指定的法律问题；
- 某关系事实可能需要在案件主体确定后进一步比对。

**禁止事项**

不得从公开事实进一步推断：

- 仲裁倾向；
- 私人关系；
- 利益输送；
- 对某一方友好；
- 具体案件结果；
- 应当或不应当选择该仲裁员。

---

### 4.8 Source / Citation

**用户目的**

让用户立即知道该信息从哪里来，并可以直接进入原始来源核验。

**默认呈现**

每个 material Finding 的来源信息应与 Finding 紧邻。

以下信息全部使用独立 tag / 标签形式展示：

- 来源标题；
- 发布主体；
- 日期（如可确认）；
- 原始链接；
- 对应 Evidence ID。

**交互要求**

- 原始链接 tag 在 HTML 中必须可以点击并打开原始来源；
- 不得把 URL 仅作为不可点击的长字符串平铺；
- 日期无法确认时，不生成空白日期 tag 或虚假的“未知日期”。

**重复控制**

同一个来源不应在正文中多次重复完整技术信息。

tag 只显示用户核验需要的信息，不显示：

- local path；
- SHA-256；
- retrieval JSON；
- parser metadata；
- execution receipts。

具体 tag 的颜色、形状、字号和视觉优先级属于 `REPORT_DESIGN.md`。

---

### 4.9 Direct Quote / 原文引用

**用户目的**

只有当原始措辞本身对理解事实或限制具有明显价值时使用。

**适用情形**

例如：

- 职位名称；
- 官方身份表述；
- 用户指定观点的原文；
- 有争议的时间表达。

**规则**

- 优先概括事实；
- 只有确有必要时引用原文；
- 引用必须保留足够上下文；
- 不得通过截断改变原义。

---

### 4.10 Evidence Reference

**用户目的**

建立：

> 用户 Finding → Evidence Object

的明确追溯关系。

每个 material Finding 至少对应一个 Evidence ID。

Evidence ID 是追溯工具，不是正文主体。

用户不需要默认看到：

- hash；
- local path；
- retrieval JSON；
- parser metadata；
- execution receipts。

这些信息继续完整保存在系统内部。

如果这些机器信息影响报告可靠性，应把“影响”翻译成人话后进入页末 Limitation / Unknown。

---

### 4.11 Disabled-module Notice

**用户目的**

明确告诉用户哪些功能本次根本没有执行。

**标准表达**

> 本次未执行专项观点检索。

> 本次未进行针对具体案件主体的关系比对。

**禁止事项**

不得生成：

> 未发现相关观点。

> 未发现冲突。

未执行 ≠ 结果为无。

---

### 4.12 Source Index / Evidence Appendix

**用户目的**

提供报告级统一来源与 Evidence 索引。

每个独立来源原则上只完整列示一次。

**至少包括**

- 来源名称；
- 发布主体；
- 来源类型；
- 日期（如可确认）；
- 原始链接；
- 对应 Evidence ID。

正文中的 Source tags 与此处索引必须能够相互对应。

**不进入普通用户索引**

默认不列：

- SHA-256；
- local path；
- staging 信息；
- retrieval JSON；
- parser 信息；
- token；
- execution log；
- benchmark。

这些属于 Layer 3 系统记录。

---

### 4.13 Limitation / Unknown

这是用户报告的一级重要信息，不是技术附注。

**固定位置**

完整 Limitation / Unknown 区块必须位于用户报告最下方，作为整份报告最后一个内容区块。

Source Index / Evidence Appendix 应位于其之前。

**用户目的**

告诉用户：

> 我们现在还不能安全地说什么。

**包括**

- coverage gap；
- 身份尚未解决；
- 任期冲突；
- 来源时间未知；
- 只有机构自述、尚未独立核验；
- 原始材料无法取得；
- human review 尚未完成；
- 搜索覆盖不足；
- 其他会影响用户理解报告可靠性的 material limitation。

**正文处理**

正文中的具体 Finding 可以用非常简短的边界提示避免误读，但完整 limitation 不在正文展开，统一汇总到页末。

Executive Summary 只允许提示存在重要未确认事项并指向页末，不重复完整内容。

**禁止事项**

不得：

- 把“未检索到”写成“不存在”；
- 把“无法访问”写成“没有”；
- 为了报告简洁删除 material limitation。

## 5. Repetition Control

同一事实应只有一个主要完整表述位置。

允许：

- Executive Summary 对重要 Finding 作压缩概括；
- 正文 Finding 使用一句边界提示防止误读；
- 页末 Limitation / Unknown 集中完整列示 material gaps。

不允许：

- 同一 claim 在多个章节完整重复；
- supports_statement 与正文再次机械重复；
- 同一 limitation 在摘要、正文、复核项和来源索引中全文重复；
- 同一 source technical metadata 被多次展开。

原则：

> 摘要负责概括，正文负责解释，来源负责证明，页末限制负责划定边界。

## 6. Language Certainty Rules

报告措辞必须与 Evidence 的实际确定程度一致。

### 可以确认

使用：

- 公开页面列示……
- 官方名册记载……
- 本次核实到……

### 尚存在限制

使用：

- 现有公开资料支持……
- 尚未独立核验……
- 本次无法确认……
- 不足以据此判断……

### 禁止未经支持使用

- 已完全证实；
- 无冲突；
- 没有其他关系；
- 没有其他著作；
- 一贯持有某观点；
- 明显偏向；
- 擅长某类案件。

除非相应结论本身确实具有充分 Evidence 支持且属于 ADD 产品允许范围。

## 7. HTML / PDF Content Consistency

HTML 与 PDF 必须保持一致：

- Candidate identity；
- Scope；
- enabled / disabled modules；
- material findings；
- facts；
- Evidence mapping；
- material limitations；
- unknowns；
- source index；
- cutoff date / time。

用户报告不使用 report version 作为一致性字段。

允许不同：

- 信息默认展开程度；
- Evidence 详情密度；
- 来源详情呈现程度；
- HTML 的同页导航与展开行为；
- PDF 的固定分页。

不得出现：

- HTML 有一个事实而 PDF 没有；
- HTML 表达为 unknown，PDF 变成确定事实；
- 一端遗漏 material limitation；
- 两端使用不同 Evidence 映射。

## 8. Core User-facing Content Logic

用户最终阅读到的基本单位应当接近：

**Finding**

→ 发现了什么

**Fact / Explanation**

→ 依据是什么、为什么值得注意

**Source tags / Evidence**

→ 用户如何核查

最终在报告最下方统一阅读：

**Limitation / Unknown**

→ 哪些事项仍不能安全确认、这些限制如何影响报告理解

而不是直接展示 Evidence Object 的全部字段。
