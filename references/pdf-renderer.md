# Canonical Model → PDF（Issue #9）

只读取已保存的合成 Canonical Model，不重新读取Evidence来源或Snapshot、不联网、不做研究。输入根为 `tests/fixtures/pdf_reports/`。入口校验Evidence结构与ID，并与Issue #8已有构造器重建结果比较，拒绝模型篡改；验证不带base_dir，因此不读取来源文件。本轮未修改Evidence Schema、Validator、原抓取/提取能力或MD/HTML Renderer。

```powershell
python -B -E -S scripts/pdf_report.py tests/fixtures/pdf_reports/model.json --output .tmp-pdf-result --runtime .tmp-pdf-runtime
python -B -E -S tests/measure_pdf_report.py --output .tmp-pdf-measure-new
python -B -E -S tests/package_pdf_smoke.py --output .tmp-pdf-package-new
```

输出目录必须新建。runtime须是项目内显式 `.tmp-*` 目录；首次解包，复用时核验所有原文件，差异/未知文件失败而不覆盖。仅Windows x64 / CPython3.12的完整闭包已提供；其他环境明确失败，不自动安装。依赖/字体及商业再分发条件见 `vendor/pdf/README.md`。

同一内存模型同时进入已有MD/HTML Renderer与PDF Renderer，使用相同blocks内容。PDF采用嵌入的LXGW WenKai字体、A4、可拆分的单列键值段落、物理页码；不采用系统字体后备。先检查所有实际展示字符的glyph映射，缺字明确失败。Paragraph的输入全部转义，不执行来源中的HTML/XML；不接受图片、远程资源或用户指定字体。本轮URL为可读纯文本，不生成链接动作。

生成report.json、report.md、report.html、report.pdf、timing.json。PDF元数据使用ReportLab invariant固定日期，仅为确定性输出标记，不是检索时间；真实retrieved_at保持在报告正文。PDF中的字体子集可回溯到完整字体hash。

## 验证与计时

PDF写盘后用原有pypdf做readback；单独记录导入+回读时间，不建立新提取能力。验证全部按序展示文字（忽略排版空白）、页码、嵌入字体与无URI动作。MD/HTML沿用Issue #8的一致性测试并在本轮从同model生成，重复运行四种产物字节一致。纯文本回读不能代替布局验证，本轮另用已存在的Poppler逐页渲染、查看11页图片确认版面未见裁切；这些QA工具不进入产品运行依赖。

计时均为perf_counter毫秒：dependency_load_ms含wheel hash、首次解包或复用核验、ReportLab/Pillow/charset导入；pdf_render_ms含字体hash、首次字体解析或已注册字体复用、glyph检查、排版与内存PDF；font_load_ms是其中的字体注册/字符检查子项，不重复加总。pdf_write_ms仅PDF写盘。formats_total_ms含MD+HTML+PDF生成与四种产物写盘，不含依赖加载及readback。readback_ms含已有pypdf首次导入（如发生）及读回检查。total_ms含模型读取/结构核对、上述各项和环境元数据，不含解释器/顶层import及timing.json写盘；基线另记录完整CLI启动至退出。没有隐藏预热或清空OS缓存。

## 已知限制

6条合成Evidence、含长段落和长URL，仅是报告路径验证。字体并不覆盖全部Unicode或所有姓名字；缺字失败不等于该字符没有来源。其他字形组合仍须验证。单列字段报告可读、可打印，但没有设计品牌排版、复杂表格、PDF/A、PDF/UA、签名或全平台支持。任何Renderer的结构/回读检查不能替代律师判断。

已有模型内absolute source/snapshot路径仅展示，不解引用。输入必须已处于获准合成根；没有针对不受信任大文件的资源沙箱。生成或readback失败可能留下新目录中的部分产物，必须以CLI退出码及timing完成结果为准，不自动删除。依赖运行目录由任务明确归属，保持可核验，不读个人配置。

本机未提供pdftotext，未安装；因此未完成其bbox自动边界检查，不将逐页视觉检查冒充坐标级证明。

## Issue #9 M1 分发修复

ReportLab 改为经固定 upstream wheel 派生的 ADD runtime ZIP，完整排除未使用的 DarkGarden 组件；不改 renderer、中文字体或 PDF 内容。来源和裁剪记录见 `vendor/pdf/derivation.json`。最终 package smoke 递归检查 ZIP / wheel 成员，并与既有 PDF 比较原字节。`wheel_bytes` 保留既有计时字段名，当前含一个 runtime ZIP 和两个 wheel；新数据见 `darkgarden-fix-baseline.json` / `darkgarden-fix-packaging.json`，不沿用原闭包数值。
