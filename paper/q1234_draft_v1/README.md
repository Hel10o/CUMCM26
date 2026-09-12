# 四问 LaTeX 论文初稿 v1

本版把四问现行结果、机制分析、独立数值证据和整体批判性复审整理为一篇可编辑论文。实际读取的基线提交：`ad9c6766d6db2f21ee61d6d5a1a7a9c54c28f377`。本轮未修改正式答案或重新冷启动全部历史求解。

当前摘要依据用户提供的参考图片，以加粗“针对问题一／二／三／四”分别起段，按“任务与建模、求解方法、关键结果、结果解释”展开，突出真实方法与主要数值。本次修订基于提交 `573348fd60e1ea26ff9874c570f8fe2f1c0f690f`，见[摘要仿写稿](evidence/abstract_sample_20260912/摘要仿写稿.md)与[修订说明及验收](evidence/abstract_sample_20260912/摘要仿写说明.md)。早期[摘要文字修订记录](evidence/abstract_revision_20260912/摘要修订说明.md)作为历史保留，段首写法以本次用户要求为准。

摘要中的核心方法、比较前提与主要执行时长选择性加粗；当前用词见上述仿写稿，历次[重点排版说明](evidence/abstract_emphasis_20260912/摘要重点排版说明.md)保留。摘要采用 11.5 pt 字号、18 pt 行距、5 pt 段间距，见[摘要间距调整与规范核验](evidence/abstract_spacing_20260912/摘要间距调整说明.md)。

正文段落、标题、公式、表格及图表间距已统一放宽，并调整三处图表浮动位置；正文保留小四字号，使用 1.30 行距系数与 5 pt 段间距，见[正文排版修订说明](evidence/body_spacing_20260912/正文排版修订说明.md)。现版 10 个正文一级标题为“一、”至“十、”编号，每个标题独占一行；二级编号保持 2.1、3.1 等，见[一级标题调整说明](evidence/section_titles_20260912/一级标题调整说明.md)。正文含 AI 声明和参考文献共 22 页；摘要 1 页、附录 127 页，总计 150 页。本次仅摘要文字和强调位置改变，正文与附录页面保持一致；见[本轮页面对比](evidence/abstract_sample_20260912/revision_check.json)及[最新 PDF 检查](evidence/abstract_sample_20260912/pdf_validation.json)。以下历次验收记录保留，当前 PDF 状态以上述最新检查为准。

- [论文 PDF](四问论文初稿_v1.pdf)
- [LaTeX 主文件](main.tex)与[可编辑源稿 ZIP](四问论文LaTeX源稿_v1.zip)
- [AI工具使用详情 PDF](AI工具使用详情.pdf)与[对应 LaTeX](ai_details.tex)
- [完整代码与复现说明](support/README.md)
- [实际验收记录](evidence/论文初稿验收.md)、[PDF机器检查](evidence/pdf_validation.json)、[主张与证据索引](evidence/主张与证据索引.md)

## 内容与当前结论

摘要、题意与统一假设、分问物性、传热传质方程和数值方法、四问结果、六张题设表、五幅图、二维与环境检验、物理适用范围、结论、AI声明、参考文献和完整代码附录均已合入。

Q2使用 `q4_complete_delivery/v1/q123_closeout/result2.xlsx` 的新全程版本；Q3与Q4分别采用 **57.4741 h**、**51.0921 h** 的一维条件执行时长。Q4精细二维正式时刻仍缺直接补证，正文保留粗网格未通过及配对校正的证据边界。气固映射、经验密度、潜热、4 h后环境及收缩归因均有明确讨论，不借更复杂历史模型替换主线。

## 格式依据

2026-09-12实际读取[当届论文格式规范](https://www.mcm.edu.cn/html_cn/node/4cd596519c9eb9fbd866398f6df0caa3.html)及[AI使用规定](https://www.mcm.edu.cn/html_cn/node/fef94648f2836ab6cc81586f4c38512b.html)，网页和官方PDF快照见[来源记录](evidence/official_sources.json)。本稿采用 A4、四边3 cm、摘要首页、无目录、匿名正文与附录、连续居中页码、正文不超过30页；完整代码附录在参考文献之后另起页。ctexart是排版实现，不冠以“官方LaTeX模板”。字体字号属于本稿选择，不宣称为官方固定要求。

AI声明放在参考文献前，另附规定名称的使用详情。队员人工核验、历史模型精确版本与全部代表性交互尚需据真实使用记录补齐，本稿没有把代理复核冒充人工审核。

## 编译与检查

在装有完整 TeX Live、XeLaTeX、latexmk 和 Windows 宋体/黑体/Consolas 的环境中：

```powershell
cd paper/q1234_draft_v1
./build.ps1
```

Linux/macOS可将两份TeX的 `fontset=windows` 改为当地可用的中文字体配置，将Consolas替换为覆盖希腊字母、比较符号的等宽字体，再用同样的XeLaTeX命令编译；跨平台字体替换后的分页需重新验收。本轮实际使用 Windows TeX Live 2026。

```text
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build ai_details.tex
python validate_paper.py
python support/launch.py smoke
```

PDF检查脚本需要 PyMuPDF。只看正文可运行 `./build.ps1 -BodyOnly`；这只是编辑预览，正式初稿始终由 `main.tex` 编译并包含附录。`build/`是未入库的编译中间目录；最终两份PDF位于本目录。

图表已随源稿提供，编译不需要重新求解。`build_assets.py`会从完整仓库的冻结结果重新生成图表，需要科学Python依赖及清单所列原始数组，不能在只有论文源稿的独立目录中凭空重算。实际依赖版本、输入哈希与图表合同见[资产清单](evidence/assets_manifest.json)。

## 源稿包与提交边界

源稿ZIP用于编辑和编译，包含TeX、图表、代码快照、输入小工作簿和构建说明；不是已经验收的国赛最终支撑材料压缩包。大体积正式Excel和未舍入数组仍在仓库原目录，未重复放入源稿包，复现入口说明了依赖和重建顺序。正式提交时须按题设及当届规则另核对结果文件取舍、支撑材料清单、20 MB限制和人工记录，不能把源稿ZIP改名就称为完成提交。

本版保留历史输入和审核证据字节。附录采用的少量源码副本只做匿名化或路径参数化，数值内核未改；原/副本哈希和差异见 `evidence/code_manifest.json`，匿名支撑清单见 `support/snapshot_manifest.json`。针对旧证据的严格SHA门槛仍须在相应原字节版本核验，不用删除断言掩盖来源差异。
