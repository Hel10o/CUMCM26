# 四问 LaTeX 论文初稿 v1

最新内容修订读取 GitHub main 提交 `9c26eb4b13a236326e6605106934e35325c1a748`，沿用已完成的结构：新增 9.2“模型推广”，原限制与数据需求顺延为 9.3/9.4；新增一张只读冻结配对数组生成的降维图；第一、二问追加潜热诊断引用；摘要与结论各追加一句未加粗的时长量级说明。摘要四段原文及加粗、结论前两段原文、所有已定数值保持。I1 在保留含数字整句与保护性声明的前提下简化重复限定，严格句数目标的受限项见[本轮记录](evidence/content_finalization_20260912/论文内容改进与定稿记录.md)；可选 I6 未执行。

当前 PDF 为 **156 页**：摘要 1 页，正文 **28 页**（物理页 2–29，含 AI 声明和参考文献），附录 127 页（第 30–156 页）。最终 37 项 PDF 检查、17 项独立静态检查和 19 项独立编译产物检查通过；六张题设表 279 个显示单元格一致。九项内容合同检查第 2 项句数上限受限，其余通过，详见本轮记录。

新图及其[脚本](build_dimension_reduction.py)、[来源与哈希](evidence/content_finalization_20260912/figure_sources.json)、[提取绘图数据](evidence/content_finalization_20260912/dimension_reduction_plot_data.json)单独留证，原 `assets_manifest.json` 及历史图表未覆盖。图取半柱坐标的 `z=0` 中截面，使用当前径向距离；三个失水增加标注与表 7 一致。脚本须在含冻结数组的完整仓库运行，独立源稿 ZIP 使用已生成图即可编译，不包含六份大数组。

本版把四问现行结果、机制分析、独立数值证据和整体批判性复审整理为一篇可编辑论文。实际读取的基线提交：`ad9c6766d6db2f21ee61d6d5a1a7a9c54c28f377`。本轮未修改正式答案或重新冷启动全部历史求解。

此前摘要加粗修订基于提交 `50e7b544aff9082c6c4cbfa7f9b226c98feaa1ec`，仅将摘要四问结论句和“针对问题一”段的表面含水率 **1.5102 kg/kg**、轴心含水率 **2.55 kg/kg** 加粗，结论中的限制也一并加粗，其他文字和数值不变；记录与该轮 PDF 哈希见[摘要含水率与结论加粗说明](evidence/abstract_moisture_bold_20260912/摘要含水率与结论加粗说明.md)及[本轮核对](evidence/abstract_moisture_bold_20260912/revision_check.json)。

此前结构修订读取 GitHub main 提交 `b51ca5671e693c01bb04db7d312ce548cf621d89`，只改章节组织与措辞：第八章标题为“模型检验：降维有效性与后段环境灵敏度”，第九章为“模型评价、适用范围与推广”，下设 9.1 模型优点、9.2 适用范围与主要限制、9.3 改进方向与数据需求；第十章保留原前两段，附录加入代码导览。第七章同步去除禁用词并明确百分比为模型临界时间缩短。详见[修订记录和九项检查](evidence/structure_revision_20260912/论文结构与表述修订记录.md)、[静态一致性检查](evidence/structure_revision_20260912/consistency_check.json)和[结构修订 PDF 检查](evidence/structure_revision_20260912/pdf_validation.json)。

摘要加粗轮 PDF 为 155 页：摘要 1 页、正文 27 页（物理页 2–28，含 AI 声明和参考文献）、附录 127 页（从第 29 页起）。此前结构修订的 37 项 PDF 检查和 26 项静态检查通过；六张题设表 279 个显示单元格与冻结清单一致，该轮摘要源文和页面像素保持不变；最新结论句及两项含水率加粗见页首排版记录。所有页面已渲染，改动页作详细目视检查，其他页作缩览和基线像素比对；不代替队员人工审核。结构修订时的产物哈希见[该轮清单](evidence/structure_revision_20260912/final_artifacts.json)，此前各轮证据保持原字节。

此前推导修订基于实际读取的提交 `63d4ca00c75e4e907caeaa2136763a379754a588`，补齐第三节与四问之间的推导链：共用控制体收支、各问参数代入和方程化简、有限体积／配点离散、隐式积分、重构极值与执行时刻、收缩坐标及实际位置输出。推导按现行求解器核对，未更换模型或重算结果；见[四问推导补充与验收](evidence/derivations_20260912/四问公式推导补充说明.md)及[公式与代码对应表](evidence/derivations_20260912/公式与代码对应表.md)。

当前摘要依据用户提供的参考图片，以加粗“针对问题一／二／三／四”分别起段，按“任务与建模、求解方法、关键结果、结果解释”展开，突出真实方法与主要数值。本次修订基于提交 `573348fd60e1ea26ff9874c570f8fe2f1c0f690f`，见[摘要仿写稿](evidence/abstract_sample_20260912/摘要仿写稿.md)与[修订说明及验收](evidence/abstract_sample_20260912/摘要仿写说明.md)。早期[摘要文字修订记录](evidence/abstract_revision_20260912/摘要修订说明.md)作为历史保留，段首写法以本次用户要求为准。

摘要中的核心方法、比较前提与主要执行时长选择性加粗；当前用词见上述仿写稿，历次[重点排版说明](evidence/abstract_emphasis_20260912/摘要重点排版说明.md)保留。摘要采用 11.5 pt 字号、18 pt 行距、5 pt 段间距，见[摘要间距调整与规范核验](evidence/abstract_spacing_20260912/摘要间距调整说明.md)。

正文保留小四字号、1.30 行距系数及 5 pt 段间距，见此前[正文排版修订说明](evidence/body_spacing_20260912/正文排版修订说明.md)。10 个正文一级标题为“一、”至“十、”编号，每个标题独占一行；二级编号保持 2.1、3.1 等形式，见[一级标题调整说明](evidence/section_titles_20260912/一级标题调整说明.md)。新增推导后，正文含 AI 声明和参考文献共 27 页；摘要 1 页、附录 127 页，总计 155 页。摘要不变，第三问结果图表位于有限圆柱检验之前；见[此前推导及页面核对](evidence/derivations_20260912/derivation_check.json)及[该轮 PDF 检查](evidence/derivations_20260912/pdf_validation.json)。以下历次验收记录保留，当前 PDF 状态以页首内容修订记录为准。

- [论文 PDF](四问论文初稿_v1.pdf)
- [LaTeX 主文件](main.tex)与[可编辑源稿 ZIP](四问论文LaTeX源稿_v1.zip)
- [AI工具使用详情 PDF](AI工具使用详情.pdf)与[对应 LaTeX](ai_details.tex)
- [完整代码与复现说明](support/README.md)
- [实际验收记录](evidence/论文初稿验收.md)、[PDF机器检查](evidence/pdf_validation.json)、[主张与证据索引](evidence/主张与证据索引.md)

## 内容与当前结论

摘要、题意与统一假设、分问物性、传热传质方程和数值方法、四问结果、六张题设表、六幅图、二维与环境检验、物理适用范围、结论、AI声明、参考文献和完整代码附录均已合入。

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
