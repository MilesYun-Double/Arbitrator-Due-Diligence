# Issue #9 实际合成 PDF 产物

report.json、report.md、report.html、report.pdf、timing.json 来自最终实现的一次真实CLI，未手工改写。baseline.json 是同次冷/已加载路径实测，packaging.json 是23文件独立目录ZIP解包烟测；verification.json 记录76项回归及11页视觉检查，均为主开发证据。

PDF：11页A4、88039字节、文字可提取。嵌入字体：LXGW WenKai Regular 1.522，不使用系统后备。6条合成Evidence含罕见字、长段落和长URL，非真实人物资料。PDF SHA-256：52e8631168c1a3c154f9de857de3861954d5395024d0ec7c45168ca4cb3c19d0。

最终新CLI完整等待2180.880ms；dependency1197.245ms，PDF内存生成132.236ms（含字体加载），PDF写盘36.468ms，readback485.021ms，MD+HTML+PDF生成与写盘172.095ms，内部total1885.726ms。已加载同进程第二次total495.109ms。不要把这些阶段直接重复相加；完整边界见references/pdf-renderer.md。

候选ZIP22414484字节；未压缩包35409078字节；首次runtime额外19638564字节。字体本身25575676字节，3个renderer wheel共9244495字节；readback pypdf另395480字节。ZIP及中间PNG只保留在任务临时目录，未重复放入仓库；可用tests/package_pdf_smoke.py重建（ZIP时间戳可能导致hash不同）。

只在Windows x64 / CPython3.12验证；不是最终Skill ZIP或发布。当前PDF排版约0.07–0.15秒，依赖/读回占更多等待时间；不值得为未经证明的小幅视觉收益另增重依赖。搜索/研究耗时本轮未测，故只能说其量级比较仍待完整真实链路，不能宣称端到端达标。无SLA。
