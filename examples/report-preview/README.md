# Issue #8 实际合成产物

report.json、report.md、report.html、timing.json 直接复制自最终代码的真实CLI输出，未手工修饰。baseline.json 保留同次新CLI与两次同进程测量；另两次三种报告产物与首次逐字节一致。

复现：`python -E -S tests/measure_report.py --output .tmp-report-new-run`

6条合成Evidence，Python 3.12.4 / Windows-11-10.0.26200-SP0。UTF-8字节数：{'report.json': 11689, 'report.md': 16603, 'report.html': 20812}。
新CLI整体等待 327.226ms，内部total 125.112ms；validation 0.131ms、model 0.144ms、MD 1.159ms、HTML 0.449ms。
同进程首次total 127.486ms，第二次 4.678ms。无隐藏预热、无OS缓存清理。内部total包含路径、读取、序列化、写盘、环境元数据等额外开销，不是所列阶段简单相加。

仅本小样本中，模型+MD/HTML未显示为明显瓶颈；不能外推真实完整任务或规模上限。Evidence读取/验证各一次，两种Renderer复用同一内存模型；无新研究、网络、PDF生成或SLA。
