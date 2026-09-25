# Digital PDF → Snapshot → Evidence（Issue #7）

此入口仅处理明确授权的非敏感测试PDF；没有OCR、PDF报告生成或人物研究。脚本默认从 `vendor/` 加载固定pypdf wheel，运行不执行pip、不联网；依赖来源/许可/摘要见 `vendor/README.md`。宿主需已有Python≥3.11，未验证其他平台/版本，不自动安装runtime。

```powershell
python -E -S scripts/pdf_source.py tests/fixtures/pdf_sources/digital.pdf --output .tmp-pdf-example --evidence-id E-PDF-001 --title 合成PDF --publisher ADD --claim 第二页包含合成声明 --excerpt 第二页：仅用于流程测试。 --page 2
python scripts/validate_evidence.py .tmp-pdf-example/evidence.json
python -E -S tests/measure_pdf.py --output .tmp-pdf-measurement
```

`-E -S` 忽略Python环境变量并关闭site-packages，不依赖用户pip安装；正常命令也使用固定wheel。output必须是新目录。PDF输入根固定为 `tests/fixtures/pdf_sources/`；共享Issue #6的路径校验，拒绝根外、reports、链接/reparse/hardlink/ADS等。只读取指定文件，不扫描来源根。

产物：

- `source.pdf`：可解析、未加密PDF的原字节，L3 Snapshot和SHA-256。部分空页、目标摘录缺失不改变“原件已保存”的事实。
- `pages.json`：每页提取文字与状态，物理页序号从1起；不是印刷页码标签。空白页/扫描页都只能标no_text_extracted，提取报错标extraction_error，不能推断没有内容。
- `evidence.json`：匹配指定页的原始摘录及页内Unicode字符区间、页文本hash。只验证摘录出现，不自动确认陈述真伪、来源质量或人工复核。匹配失败形成unknown_insufficient_coverage；不伪造text/locator。
- `timing.json`：测量旁记录，不新增Evidence Schema字段。可解析PDF的pages.json路径/hash保存在既有snapshot.notes。

损坏/不支持/加密文件不生成伪正文，形成L0/unavailable缺口Evidence。未读取到的文件没有伪hash；读取但无法解析时可保留输入hash于retrieval_notes，原source.local_path仍供人工复核。原PDF不得被生成的Evidence覆盖。入口退出码0=取得匹配摘录且VALID，3=结构VALID的缺口，2=参数、路径、依赖或输出失败。

## 计时口径

统一使用 `time.perf_counter()`，单位毫秒，未人为缓存或删除首次结果：

- bundle_load_ms：校验wheel字节/hash及导入；pypdf_already_loaded明确区分当前进程是否已导入。
- pdf_open_parse_ms：打开/读取本地文件、PdfReader解析、加密/页数检查及页列表取得。
- page_extraction_ms / extraction_ms：每页真实extract_text调用（包括空页/失败）及整个逐页循环。
- snapshot_evidence_ms：Evidence初始字段构造，加上hash/摘录定位/快照、pages.json和Evidence写盘；不含提取及Validator。
- preflight_validation_ms：对调用者基础元数据的既有Validator校验。
- validation_ms：最终validate_file（包括原始Snapshot文件hash复核）。
- total_ms：collect_pdf入口至最终Validator完成，包括上述时间、路径检查、环境元数据等其余开销；不含解释器启动、模块顶层导入和timing.json自身写盘。
- benchmark的external_wall_ms：父进程从启动CLI前到子进程结束，包含解释器、模块导入、全部产物写盘、CLI反馈及退出，代表本次完整CLI等待时间；不能只用extraction_ms代替它。

`tests/measure_pdf.py` 运行3个全新 `-E -S` CLI子进程，再在同一父进程显式记录首次加载和后续2次已加载调用。无隐藏预热、不清理OS文件缓存；“冷”只指新Python进程/首次import，不声称冷磁盘。`examples/pdf-timing-baseline.json` 是本轮实测原始数值；重跑应输出新目录，不覆盖历史基线。只用固定3页2260字节夹具，不能推断真实PDF/完整仲裁员任务性能，未设SLA或性能断言。

## 限制

- PDF限制10MiB/100页；压缩流解压后资源消耗仍可能很大，没有独立进程CPU/内存硬隔离；只处理受信任的合成测试文件，不是任意上传PDF服务。
- strict解析下不兼容文件会降级；加密直接拒绝。未调用OCR、解密或网络服务；不执行PDF动作/脚本/附件。
- 文字顺序、复杂版式、字体映射和缺字可能错误。replacement/null字符会标提取异常，但不是全面正确性检测；空文本不等于空内容。
- fixture使用文本对象/Unicode映射和标准CJK字体引用，未嵌入字体；不据此宣称PDF视觉渲染在各阅读器通过。它的较宽CMap也影响本次提取成本。
- 绝对快照路径遵循既有Validator，搬迁需更新路径重新验证。Validator核对原PDF hash，不自动验证派生pages.json的hash或语义对应；本轮功能测试检查这些关系。
- 发生输出错误可能留下新目录中的部分文件；不删未知文件。宿主没有兼容runtime或wheel不完整时明确报错，不通过自动安装解阻。
