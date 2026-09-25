# Static Source → Snapshot → Evidence（Issue #6）

运行环境：宿主已有 Python 3.9+；只用标准库，不安装依赖。
本轮仅处理非敏感静态公开来源和合成文件，不进行人物研究、PDF或报告渲染。

在项目根运行（输出目录必须尚不存在）：

```powershell
python scripts/static_source.py tests/fixtures/static_sources/page.html --output .tmp-local-source --evidence-id E-LOCAL-001 --title 合成来源 --publisher 合成发布者 --claim 来源记载合成机构成立于2020年。 --excerpt 合成机构成立于2020年。 --evidence-type source_supported_fact
python scripts/validate_evidence.py .tmp-local-source/evidence.json
python scripts/static_source.py https://example.com --output .tmp-public-source --evidence-id E-URL-001 --title Example --publisher 待核验发布者 --claim 待核验公开页面 --evidence-type unresolved_lead
```

入口不会扫描目录。本地来源根固定为 `tests/fixtures/static_sources/`，只接受明确路径的 `.txt/.html/.htm`；不允许读取报告或真实人物材料。路径逃逸、链接、Windows reparse point、硬链接、隐藏文件、ADS及敏感目录组件会被拒绝。输出限项目内新目录，禁止覆盖；测试或试运行宜使用已被 Git 忽略的 `.tmp-*`。这些检查不是对恶意并发文件替换的操作系统级沙箱。

URL 仅支持无用户名/密码的 HTTP(S)，无Cookie、登录或浏览器脚本；不继承代理。检查解析地址和每次重定向的公共IP，拒绝私网/回环。先核对robots：404视为没有规则；其他获取失败保守降级；重定向目标重新核对。DNS检查与连接不是绑定的，不能作为面向不可信调用者的SSRF服务边界；本工具是本地显式授权CLI。调用者负责URL不含凭据、案件信息以及内容保存授权。不得用重试或更换入口绕过访问限制。

每个响应最多1MiB，单次网络操作timeout=15秒（不是整个操作的绝对截止时间）；接受text/plain、text/html，拒绝压缩响应和不支持的类型。不处理PDF、动态页面、验证码或登录。UTF-8为无charset时默认值；响应明确charset时严格解码，失败不生成替换字符。HTML只作保守文本提取，剔除script/style/template，不模拟浏览器可见性，不保证复杂表格/正文识别。

调用者提供title、publisher、claim和可选excerpt；不自动提取作者、日期或认定事实。只支持既有三种类型：source_supported_fact、unresolved_lead、unknown_insufficient_coverage。source_supported_fact要求L1/L2和实际出现的excerpt；这只验证摘录存在，不判断claim在语义上得到支持。人物字段固定为非人物流程来源，identity_resolution=not_applicable；quality=unknown，human_review=not_started。未擅自标记已复核。

默认L2输出：

- `source.raw`：本次取得的原始字节，Evidence.snapshot.path/sha256指向它。
- `readable.txt`：独立派生UTF-8文本；路径/hash存于现有snapshot.notes，locator指向该hash和零基Unicode字符区间（不含右端）。
- `evidence.json`：单个既有Evidence Object；请求URL、最终URL、content-type、HTTP状态、原始/派生hash保存在现有retrieval_notes中的JSON字符串；retrieved_at为本次尝试开始的UTC时间。

L1只在Evidence中保留匹配摘录/locator，不保存正文；L0只保留元数据，无摘录。L0不允许source_supported_fact。L1未保存派生文本时locator是检索时定位，复核依赖原来源可访问，限制不同于L2。Snapshot政策正文仍仅在 `snapshot-policy.md`。

获取、解码、类型或摘录匹配失败：保存可追溯URL/本地路径和错误，降级unknown_insufficient_coverage、L0/unavailable，excerpt/path/hash为null，不保存伪正文。原待核验claim仅留context，失败claim明确不表示事实不存在。输入/路径违规则拒绝命令，不读取文件、不创建Evidence。

输出使用绝对快照路径，以兼容现有Validator实际解析方式；移动整个产物目录后必须更新路径并重新验证，不能宣称天然可迁移。现有Validator验证原始文件hash；派生文本hash/定位由新增功能测试核对。代码调用原有validate_evidence与validate_file，没有复制规则或改Schema。结构VALID不等于研究结论通过。

退出码：0=取得来源并生成VALID Evidence；3=生成VALID缺口Evidence但获取未完成；2=输入/路径/写入/验证错误。写入失败可能留下部分新目录，应人工检查，不自动删未知文件。不会把结构VALID当作抓取成功。

测试：`python -m unittest discover -s tests -p test_static_source.py -v`。URL测试使用本机合成HTTP服务，仅在测试内mock公共IP检查；另测真实IP/重定向拒绝逻辑，生产入口没有放行开关。三宿主兼容、公开站点全面覆盖、真实仲裁员资料、PDF与后续报告链均未验证。
