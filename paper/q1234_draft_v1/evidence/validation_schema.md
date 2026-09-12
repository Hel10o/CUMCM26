# 论文 PDF 自动验收口径

`../validate_paper.py` 只读取编译 PDF、AUX 和表格预期清单，写入 JSON 与同名 TXT 报告；不修改论文、表格、模型或正式答案。依赖 PyMuPDF。本机已核实可用解释器为项目根目录下的 `review_q1_20260910/.venv/Scripts/python.exe`，PyMuPDF 版本写入每次运行报告。

## 运行与退出码

在论文目录中运行：

```powershell
& '..\..\review_q1_20260910\.venv\Scripts\python.exe' -X utf8 validate_paper.py
```

默认输入为 `build/main.pdf`、`build/main.aux`、`build/ai_details.pdf`、`evidence/table_expected.json`；默认输出 `evidence/pdf_validation.json` 和 `evidence/pdf_validation.txt`。可用 `--pdf`、`--aux`、`--ai-pdf`、`--expected`、`--output` 指定路径。相对参数路径相对调用时的工作目录，默认路径相对脚本目录。

正文预览必须显式使用：

```powershell
& '..\..\review_q1_20260910\.venv\Scripts\python.exe' -X utf8 validate_paper.py --pdf build/body_preview.pdf --aux build/body_preview.aux --body-only --output evidence/body_preview_validation.json
```

退出码 0 表示所选范围内自动检查均通过，退出码 1 表示至少一项失败。缺少文件、依赖、标签、表格定位失败或脚本异常均生成明确失败项，不以跳过代替通过。正文预览最多得到 `preview_passed`，其 `full_document_validated` 始终为 `false`。完整模式缺附录时必定失败。

## 判定规则

| 检查 | 判定与证据 |
|---|---|
| 摘要一页 | AUX `body:start` 必须为第 2 页；PDF 第 1 页须含“摘要”和“关键词”，无承诺书或编号专用页标题。 |
| 正文页数 | 完整模式从 `body:start` 至 `appendix:start` 前一页，包含参考文献及 AI 声明，范围为 1–30 页。预览计至 PDF 末页并标记附录未验。 |
| 顺序与页码 | `document:end` 必须等于 PDF 总页数；AI 声明在正文计数范围内，且在唯一“参考文献”标题之前。逐页从页面底部中央的空间位置识别阿拉伯页码，必须从 1 连续递增。 |
| A4 与文件大小 | 每页直立 A4，宽高允许 1 pt 浮点误差；PDF 严格小于 20,000,000 字节，采用保守的十进制 MB 门槛。主 PDF 与 AI 详情分别检查。 |
| 目录与引用 | 摘要、正文无独立“目录 / Contents / Table of contents”标题；无 `??`、`[?]` 或 Unicode 替代字符；AUX 中每个引用键必须有唯一参考文献定义。附录代码可能合法包含这些字符串，因此引用缺失扫描不用于附录源码。 |
| 匿名与路径 | 全文含附录及 PDF 元数据扫描已知账号 Hel10o、libai、Windows 绝对路径、UNC 路径及 Unix 用户绝对路径；PDF author 必须为空。未知真实姓名、学校、队号须人工复核。 |
| 文字边界 | 所有非空文本 span 应位于 25 mm 页边距框内；仅正确位置的本页居中页码豁免。允许 2 pt 字体包围盒外伸误差，超限逐项列出页码、文本、坐标和超出量；不豁免整个页脚区域。此项依据 PDF 文字包围盒，不能代替视觉检查。 |
| 空白页与字号 | 无文字、图像及绘图的空页失败；正文中文字符按字号计数，报告主字号。公式上下标、表格或图注的小字号不自动判为不合规。 |
| AI 详情 | 另一个可读取 PDF 必须存在，并含“AI工具使用详情”、工具/版本、目的或环节、输入与交互、采纳与核验等主题词。仅验证主题是否出现，不冒充对真实性、记录完整性或人工审核的认证。 |

## 六张数字表的定位与逐格比较

1. `table_expected.json` 必须正好包含六张现行题设结果表。使用 AUX 标签 `tab:q1-temperature`、`tab:q1-moisture`、`tab:q2-temperature`、`tab:q2-moisture`、`tab:q3-moisture`、`tab:q4-moisture` 取得页码及表号，要求表号为 1–6。
2. 在指定页按文字空间位置聚合行，唯一定位对应的表题。表题须同时具有正确表号与时间/物理量等关键词，不能用正文中的“见表 1”代替。
3. 识别表题下方 booktabs 上横线、同宽表头分隔线、下横线，排除较短的 `cmidrule`；只从三条线限定的表格本体矩形中抽取数据，按行的纵坐标和格内横坐标排列。不使用全局数字集合、全文搜索或预期数值反向定位。
4. 若表格到达页面底部但行数未满，允许最多 3 页连续段；续页须在页面顶部找到同横向范围的三条表格线和重复表头结构。小型表格缺行直接失败。无法自动定位其他续表格式时明确失败，须人工检查或扩展定位规则。
5. 行数、列数、所有数值字符串和时间字符串须完全一致，包含四位小数的尾零。PDF 的破折号/长短横线规范化为清单的 `--`，除此之外不四舍五入、不补空格、不填 0。域外格不能充当含水率 0。
6. 每张表报告表题位置、每页抽取矩形、每行包围盒、实际二维单元格、逐格差异。成功也保留实际抽取内容，便于审阅复现。

## JSON 字段与可据此作出的结论

- `schema_version`：当前为 1。
- `validation_scope`：`body_preview` 或 `full_document`。
- `status`：`failed`、`preview_passed` 或 `automated_checks_passed`。
- `passed`：所选范围是否无失败项；`full_document_validated` 仅在完整模式全部自动检查通过时为真。
- `submission_ready`：始终为 `false`。脚本不认证人工核验、最终提交命名/打包、视觉质量或题目模型正确性。
- `inputs`：各输入路径、存在性、字节数、SHA-256；`runtime`：实际 Python 与 PyMuPDF 版本。
- `inputs.stable_during_validation`：运行结束重新核对输入哈希；任何输入在检查中途被重新编译或修改均判失败，避免混用两个编译版本的证据。
- `checks`：每项有 `id`、`status`（`pass/fail/info`）、`message`，必要时有可定位 `evidence`；`failed_check_ids` 汇总失败标识。
- `aux_labels`、`body_page_count`、`documents`、`table_results`：保存结构和数字证据。

官方条款来源与 AI 二选一声明原文另见 `official_format_2026.md` 及其快照。通过本脚本后仍需使用渲染页执行目视检查，并由实际作者审核论文与 AI 记录。

2026-09-12 已用临时输入实际验证三个拒绝路径：完整模式拒绝缺附录的正文预览、缺 PDF 返回未执行及失败项、临时预期清单仅改错一个温度单元格时准确触发该表失败。三项均返回退出码 1；没有修改正式 PDF 或正式预期清单，临时测试文件已逐个删除。
