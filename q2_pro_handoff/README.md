# 第二问 Pro 分析交付包

本包包含原题、输入、候选模型推导、数值风险分析和实际试算证据，用于让 Pro 继续独立审查并给出第二问最终答案。**当前包不是最终答案包，尚未生成正式 result2.xlsx。**

## 使用方法

将完整 ZIP 上传给 Pro，并粘贴 `发给Pro的简短提示词.txt`。提示词已明确要求它主动从 [GitHub仓库 Hel10o/libai](https://github.com/Hel10o/libai) 读取所需文件：先读根 `README.md` 和 `readable/README.md`，再按主说明第0节取得原题、附件、代码、结果、审核记录和相关文献。预计算记录应在独立建模之后用于交叉比较。

只传主 Markdown 时，Pro 需要从仓库实际取得原题和附件才能完成计算；完整包同时提供原件副本和尚未推送的本次预分析证据，因此仍推荐上传 ZIP。2026-09-11 核对的远端 main 为 `1942d7506632e94853b32772c7c9bb4ba3a3c0be`；本次主说明、预计算和最新阶段论文尚未推送，不能将本地文件误称为GitHub已发布文件。

## 文件索引

| 路径 | 用途 |
|---|---|
| `第二问分析与Pro交付说明.md` | 主任务、方程推导、题意歧义、假设边界、算法和最终验收清单 |
| `发给Pro的简短提示词.txt` | 可直接粘贴的启动指令 |
| `预计算说明.md` | 已实际运行的内容、量级、精度缺口、重跑命令和数组说明 |
| `inputs/题目原件.pdf` | 项目原题完整字节副本，优先于文字提取和二次解释 |
| `inputs/附件1.xlsx` | 环境输入原件副本，241 个一分钟采样点，覆盖 0—4 h |
| `inputs/result2_template.xlsx` | 第二问空白模板原件副本；不是已求解结果 |
| `evidence/audit_inputs.py`、`data_contract_audit.json` | 标准库 OOXML 输入与输出契约审计 |
| `evidence/preflight_q2.py`、`preflight_results.json`、`preflight_npz.npz` | 三级有限网格试算、真实记录和最细级采样数据 |
| `evidence/parameter_scales.json` | 附录 3 公式的代表状态代入与尺度 |
| `evidence/problem-page-2.png`、`evidence/problem-page-4.png` | 第二问题面及附录 3 公式页面，供目视核对 |
| `evidence/adrover-page-06.png` | 现有文献中被讨论的热方程及配套边界机制 |
| `evidence/package_checks.json` | 打包前的原件哈希、包内独立读取和试算文件一致性检查 |
| `context/` | 第一问冻结模型、表格和报告，以及题面文字提取；历史参考，不作为第二问最终结果 |
| `requirements-preflight.txt` | 重跑预计算时的依赖版本 |
| `MANIFEST.sha256` | 除本清单自身外各交付文件的 SHA256，用于传输完整性检查 |

`context/` 中保留了历史文档和代码，其中部分链接、导入或输出路径属于原项目，不保证脱离原仓库直接运行。第二问的必要输入和两个审计/试算入口均在本包中齐备。文献截图不是完整文献的替代品；只用于核对主文档明确讨论的式子。

## 原件校验

| 文件 | SHA256 |
|---|---|
| `inputs/题目原件.pdf` | `052d8014bff5727c019b72e44fdffaf5c145ce04050dd938baaf3527db331736` |
| `inputs/附件1.xlsx` | `7ef32870abeef420b89560b2530ff60dfe4255917805151d89988d0311af9dd7` |
| `inputs/result2_template.xlsx` | `23b261b295c1b787d000eebbca6521c37075107b6fcf78724f8d395ce1798ff4` |

重新运行会改变生成记录中的路径、环境或用时，因而改变文件哈希；这不表示原始输入发生改变。保留原包，再在副本中计算即可。
