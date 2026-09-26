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

## 停止或降级

遇到同名无法排除、只有搜索摘要、原文不可获得、付费墙/访问控制、页面失效、来源冲突、规则版本无法确认、需要未经授权案件信息，或试图从“未检索到”推导“不存在”时，保留缺口并停止受影响结论，不强行补全。

本 Playbook 在第一名真实仲裁员完整链路完成后再根据实际执行结果修订。

## Issue #18 已验证的技术入口

Issue #17 在真实材料入口处 BLOCKED，尚未完成第一名真人研究。Issue #18 仅用合成身份验证 real-mode plumbing，并对既有官方 PDF 做本地 staging/hash 验收，不代表真人尽调通过。

获准材料须先声明独立 `ADD authorized research run` 合同，通过明确路径与 SHA-256 staging 到该 run；real collector 必须接收调用者 metadata JSON。同一 run 内完成 Evidence、Validator、Canonical Model、MD/HTML/PDF 与 readback。具体入口、范围和限制见 [real research run contract](references/real-research-run.md)。真实 PDF 最多 300 页/10 MiB，仅提取指定页；不得将其视为全文覆盖。出现采集失败时由调用者保留错误及缺口，不能用 synthetic 默认身份替代。

修复完成后停止等待主控及独立审查；不得据此自动恢复 Issue #17 或开始其他人研究。
