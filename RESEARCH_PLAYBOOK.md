# Research Playbook

本文件记录当前已确认的高层 SOP。第一名仲裁员完整链路尚未完成，因此不把未经验证的细节写成成熟流程。

1. 接收任务。
2. 确认启用功能与候选范围。
3. 进行官方身份核验。
4. 发现公开信息。
5. 打开并核对原始来源。
6. 保存必要 Snapshot。
7. 建立 Evidence Object。
8. 进行身份消歧。
9. 按请求执行观点或关系分析。
10. 记录未知、冲突和资料缺口。
11. 运行 Validator。
12. 生成人工复核清单。
13. 将结构化结果交给后续 Report Renderer。
14. 输出 Markdown、HTML 和 PDF。
15. 输出本次 research performance 记录并交主控入长期 benchmark。

## 停止或降级

遇到同名无法排除、只有搜索摘要、原文不可获得、付费墙/访问控制、页面失效、来源冲突、规则版本无法确认、需要未经授权案件信息，或试图从“未检索到”推导“不存在”时，保留缺口并停止受影响结论，不强行补全。

本 Playbook 在第一名真实仲裁员完整链路完成后再根据实际执行结果修订。

## 已验证的 real research 技术入口

Issue #17 首次在真实材料入口处 BLOCKED；Issue #18 修复 authorized real research run、受控 staging、real metadata 和有界长 PDF，并经 Issue #19 独立审查 PASS。该技术入口已可用于恢复第一名真人链路，但不等于真人尽调本身已经通过。

获准材料须先声明独立 `ADD authorized research run` 合同，通过明确路径与 SHA-256 staging 到该 run；real collector 必须接收调用者 metadata JSON。同一 run 内完成 Evidence、Validator、Canonical Model、MD/HTML/PDF 与 readback。具体入口、范围和限制见 [real research run contract](references/real-research-run.md)。真实 PDF 最多 300 页/10 MiB，仅提取指定页；不得将其视为全文覆盖。出现采集失败时由调用者保留错误及缺口，不能用 synthetic 默认身份替代。

## Research Performance 记录

从恢复后的第一名真人研究开始，每个真人 research run 都必须记录性能数据；PASS、PARTIAL、BLOCKED 均记录。

执行端必须在本地 run root 生成 `performance.json`，至少包含：

- run summary：开始/结束时间、research / processing / total wall time、来源数量、Evidence 数、coverage gap、人工复核项、最终状态；
- capability profile：实际模型/宿主/检索或浏览能力/工作流版本/并行方式/当前 Git commit（运行时可知项）；
- search/retrieval steps：每次实际搜索、打开、抓取或核验的目的、能力类别、wall time、结果与错误/retry；
- token usage：优先记录运行时真实 input/output/cached/reasoning/total tokens；无法取得时明确记录 unavailable，不得用粗略字符换算冒充真实 usage；
- cost：只有 provider/runtime 有实际费用时记录；否则保持 null，不猜实际账单。

每次 run 结束时，GitHub Issue 回写 performance summary。主控收到回执后，将不含真人来源正文的性能摘要追加到 `benchmarks/research-performance.jsonl`，用于长期比较不同模型、Search/Browser 能力和研究方法。

详细定义见 [Research Performance Benchmark](references/research-performance-benchmark.md)。

性能优化必须同时看证据覆盖和结果质量；更快或更省 token 但 identity、来源等级、Evidence 或 coverage 明显变差，不视为更优。
