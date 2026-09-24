# Handoff

## 标准交接字段

- **Task**：任务名称和目标
- **From**：交出角色
- **To**：接收角色
- **Fixed Version**：固定版本、commit 或产物标识
- **Goal**：本次要完成的结果
- **Artifacts**：文件和报告位置
- **Evidence / Verification**：测试、检查和运行证据
- **Decisions Already Made**：已冻结的范围和判断
- **Open Issues**：未解决问题
- **Out of Scope**：明确未执行事项
- **Next Authorized Action**：下一项已获准动作

## 主开发 → 主控

提交实际修改、文件、测试结果、Git 状态和已知限制。不得用计划替代运行证据。

## 主控 → 独立审查

提交固定 commit、审查范围、验收标准、已知风险，并明确禁止修改实现。

## 独立审查 → 主控

返回 `PASS`、`FAIL` 或 `NEEDS_FIX`，并附独立检查证据、问题、严重程度和是否阻断 Gate。

## 主控 → 主开发

只下发已经获准的下一任务或修复项；主开发不得自行进入下一阶段。
