# Research Performance Benchmark

## 目的

ADD 从第一名真人研究开始，持续记录每次仲裁员信息检索/研究 run 的时间、token、成本与产出质量，用于比较不同模型、Search/Browser 能力、研究方法和工作流版本，逐步找到更快、更低成本且不降低证据质量的执行方案。

本 benchmark 是性能/成本观测，不替代 Evidence、质量判断或法律复核。

## 记录层级

### 1. Run Summary

每次真人仲裁员研究 run 完成或停止时都必须记录，包括 PASS、PARTIAL、BLOCKED。

至少记录：

- run_id
- issue
- subject_key / pool_index
- started_at / ended_at
- git_commit
- workflow_version
- host / model（运行时可知时）
- capabilities_used
- status
- identity_resolution
- sources_attempted
- sources_opened
- sources_accepted
- evidence_count
- coverage_gap_count
- human_review_count
- report_pages / report_bytes
- research_wall_ms
- processing_wall_ms
- total_wall_ms
- token measurement
- cost measurement

### 2. Search / Retrieval Step

每次实际用于寻找、打开或核验仲裁员信息的检索步骤都记录：

- step_id
- purpose
- capability/tool category（search / browser / static fetch / PDF / other）
- query_or_target（不得写入非公开案件信息）
- started_at / ended_at
- wall_ms
- result_count（可得时）
- accepted_source_count
- token usage（可得时）
- error / retry
- outcome

可以把紧密关联的同一工具批次作为一个 step，但不得把整个研究过程只记成一个模糊步骤。

## Token 口径

### 优先级 1：运行时真实 usage

如果执行环境/API/宿主暴露 usage metadata，记录其真实值：

- input_tokens
- cached_input_tokens
- output_tokens
- reasoning_tokens（若暴露）
- total_tokens
- provider/model
- usage_source

此时 `token_measurement_mode = "runtime_exact"`。

### 优先级 2：匹配模型 tokenizer 的可复算计数

只有在无法取得 runtime usage、且存在与实际模型明确匹配的 tokenizer 时，才允许单独记录估算/重算值，并标记：

`token_measurement_mode = "tokenizer_estimate"`

估算值不得与 runtime exact 混在同一比较列中。

### 不可得

如果既无 runtime usage，也无可靠匹配 tokenizer：

`token_measurement_mode = "unavailable"`

token 数写 null。

**禁止使用“字符数/4”等粗略算法冒充真实 token 消耗。**

工具内部、隐藏系统提示、宿主额外上下文等如果不在 usage 中单独暴露，不自行推测。

## Cost 口径

优先记录 provider/runtime 实际返回的费用。

若没有实际费用：

- cost_amount = null；
- 保留 provider/model/token 数据；
- 不用当前公开价反推后冒充实际账单。

如未来需要估算成本，必须另存 pricing_snapshot（模型、币种、时间、单价）并标记为 estimated。

## 时间口径

统一使用单调时钟记录 wall time；跨进程总时间另记录 ISO 起止时间。

至少分：

- research_wall_ms：搜索、打开来源、身份消歧、阅读、筛选、Evidence 构造；
- processing_wall_ms：collector / Snapshot / Validator / Canonical / rendering / readback；
- total_wall_ms：本次 run 从正式开始到最终状态的墙钟时间。

等待网络、retry 必须计入实际 wall time，不得从“性能”数字中隐藏。

## 能力与方法标签

为了长期 A/B 比较，每个 run 记录 capability_profile，例如：

- model / model version（可知时）
- host
- search capability
- browser capability
- workflow / prompt version
- parallelism
- source strategy
- collector mode
- OCR enabled/disabled
- renderer
- git commit

更换能力或方法时必须形成新的 profile，不覆盖旧记录。

## 质量护栏

性能优化不能只看 token 或时间。

长期比较至少同时看：

- identity 是否可靠解决
- accepted source 数及来源等级
- Evidence 数
- coverage gaps
- Validator 结果
- human review 数
- REAL_CHAIN_PASS / PARTIAL / BLOCKED
- 报告可追溯性

如果更快/更省 token 但证据覆盖或可靠性下降，不得直接标记为“更优”。

## 派生指标

主控后续可计算：

- tokens / accepted source
- tokens / Evidence
- seconds / accepted source
- seconds / Evidence
- coverage gaps / run
- human review items / run
- cost / accepted source（仅 cost 可用时）
- cost / Evidence（仅 cost 可用时）

不同 token_measurement_mode 不直接混合比较。

## 保存位置

执行端：

- 每个真人 run 在本地 run root 保存 `performance.json`，包含 summary + steps。
- 真人来源正文、Snapshot、Evidence、报告继续留在本地，不因 benchmark 上传。

主控：

- 每次收到执行回执后，核对 performance 数据；
- 将不含真人资料正文的性能摘要追加到 `benchmarks/research-performance.jsonl`；
- GitHub Issue 回写本次 summary；
- 长期对比时以 JSONL 为主，不依赖聊天记忆。

## 当前要求

从恢复后的 Issue #17 开始执行。第一次 #17 的入口 BLOCKED 发生在正式真人检索前，不计入“仲裁员研究性能样本”；可保留为工程故障时间，不进入研究效率排名。
