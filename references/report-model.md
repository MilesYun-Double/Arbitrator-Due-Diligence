# Canonical Report Model → Markdown / HTML（Issue #8）

本轮输入限 `tests/fixtures/report_sources/` 中显式指定的合成 JSON；不扫描目录，不读取真实人物、案件或 reports/。不联网、不安装依赖、不生成 PDF。入口只使用标准库，复用现有路径检查与 Evidence Validator；未修改 Evidence Schema / Validator。

```powershell
python -E -S scripts/report.py tests/fixtures/report_sources/evidence.json tests/fixtures/report_sources/task.json --output .tmp-report-example
```

输出目录必须不存在，禁止覆盖。输入为非空 Evidence 数组；逐条调用现有 Validator，跨条目检查 ID 唯一性，验证一次。Snapshot 路径先限制到合成输入根内的绝对路径（拒绝链接/重解析点等），再允许 Validator 读取；不根据 source.url/local_path 获取来源。

## 模型与语义

`report.json` 包含 model_version、task、sections、evidence：

- task：调用者明确提供 title、scope、enabled_modules、assignments。身份、背景、公开著作、公开关系是基础模块；指定观点与冲突比对明确启用/关闭。当前不解析案情或推断模块。
- assignments：每个 Evidence ID 必须恰好分配至一个已启用模块；漏项、多余引用或关闭模块中的分配直接报错，不能静默丢弃 Evidence。
- sections：固定模块顺序、状态、Evidence ID 引用；启用但无证据为“未提供证据 / unknown”，不声称检索完成。关闭模块为“未执行”。未启用冲突比对明确标记“未进行针对具体案件主体的关系比对”。
- evidence：输入 Evidence 的深拷贝，保留全部字段、类型、身份状态、质量、unknown、限制、人工复核状态，不把同名主体合并。调用者元数据不等于独立核验事实。

来源索引、覆盖限制、人工复核列表通过同一模型内的 Evidence 产生，避免维护两份可能漂移的事实。`build_model` 是接收已验证 Evidence 的内部构造函数；对外入口 `generate` 总是先验证。Renderer 只接受构造后的模型，不把任意外部 report.json 当成可信新入口。

## 输出与安全

MD/HTML 使用同一 `blocks(model)` 展示顺序，逐条保留全部 Evidence 字段；嵌套值按字段路径展示，null/空数组明确保留。事实不经过自动摘要或改写。模型、MD、HTML 不包含生成时间，因此同一输入重复生成确定一致；timing 是单独的非确定性旁记录。

HTML 对所有动态文字、属性执行转义；无远程 CSS/JS/字体，无脚本。仅合法、无凭据的 http/https 来源 URL 可点击，其他 scheme 保留为文字。CSP 是附加防护，不代替转义；点击链接属于阅读者主动行为，生成/加载报告不获取来源。MD 也转义来源 HTML 与 Markdown 控制字符，换行显示为 br；未引入第三方 Markdown 解析器。尚未验证任意第三方 Markdown 查看器的行为。

## 计时

time.perf_counter，毫秒：validation_ms、model_ms、markdown_ms、html_ms。total_ms 从 generate 入口到模型/MD/HTML写盘和环境元数据完成，包含读取、路径检查、序列化等额外开销；不含 timing.json 写盘、解释器启动及模块导入。基线另以父进程测量完整 CLI 启动至退出，不隐藏冷启动。

记录 Evidence 条数、report.json/report.md/report.html UTF-8字节数、Python/平台。Renderer 复用同一内存模型，不重复读取或验证 Evidence；共享 blocks 为纯内存展示遍历，非研究层。当前小样本不能推出大规模或完整尽调 SLA，也不能将平台元数据开销误作渲染开销。

## 限制

本实现是合成输入的最小链路；结构校验不证明来源、身份、语义或法律判断正确。报告保留所有条目，不按身份合并或自动组织事实时间线。没有 PDF、复杂排版、后台服务或插件系统。没有针对任意巨大/恶意 JSON 的资源隔离；路径校验不等于操作系统沙箱。写盘失败可能保留新目录中的部分文件。新增机器/平台未实际验证。
