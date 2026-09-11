# libai

项目题目、建模资料、第一问与第二问计算交付，以及独立核验和论文阶段稿。

## 通过 ChatGPT 的 GitHub 连接读取

先读取 [网页模型阅读入口](readable/README.md)。其中包含4篇论文和原题的逐页Markdown全文，均为普通Git文件，不需要PDF解析或Git LFS下载。

如果连续全文被截断，可按每篇论文的页码索引分批读取。复杂公式、表格和图像应对照原始PDF；提取文本不替代逐式核验。

```text
请使用 GitHub 连接读取 Hel10o/libai 的 README.md，然后读取 readable/README.md。
按该索引打开题面和相关论文的 fulltext.md；若返回被截断，继续按 pages 目录逐页读取。
引用时注明论文与 PDF 页码，不要把 PDF 下载指针、旧摘要或截断内容当作全文。
```

仓库当前按所有者要求设为公开，名称为 `Hel10o/libai`，此前名为 `Hel10o/CUMCM26`。普通README也无法读取时，先核对仓库新名称和连接账号；如果以后改为私密，还需为连接单独授权。本地Git命令的登录权限与ChatGPT GitHub连接的权限需分别核对。

## 项目内容

- [题目原件](A题/A题.pdf)与[原始附件](A题/附件/)。
- [题目分析](分析与文献/01_题目分析.md)与[文献说明](分析与文献/02_相关论文.md)。
- [论文和题目的可读全文](readable/README.md)。
- [第一问交付说明](q1_complete_delivery/q1_delivery/README.md)。
- [第一问结果Excel](q1_complete_delivery/q1_delivery/output/result1.xlsx)。
- [最新论文部分稿：第一问与第二问](paper/q1_q2_stage/第一二问论文阶段稿.pdf)，[编辑与构建入口](paper/q1_q2_stage/README.md)。
- [第一问论文阶段稿（保留历史版本）](paper/第一问论文阶段稿.pdf)。
- [原交付第一问正文（保留历史版本）](q1_complete_delivery/q1_delivery/output/第一问论文正文.md)。
- [代码及复现入口](q1_complete_delivery/q1_delivery/run_all.py)。
- [2026-09-10 第一问独立审核入口](review_q1_20260910/README.md)。
- [第一问完成情况与答案审核报告](review_q1_20260910/第一问审核报告.md)。
- [第二问 Pro 完整交付说明](q2_final_delivery/README.md)与[模型选择记录](q2_final_delivery/analysis_decisions.md)。
- [第二问结果 Excel](q2_final_delivery/output/result2.xlsx)、[论文正文与两张结果表](q2_final_delivery/output/第二问论文正文.md)及[代码复现入口](q2_final_delivery/run_all.py)。
- [2026-09-11 第二问验收报告](review_q2_20260911/第二问验收报告.md)、[机器检查结果](review_q2_20260911/acceptance_checks.json)及[独立数值核查](review_q2_20260911/independent_numeric/独立数值核查.md)。
- [第二问深化审查提示词](q2_refinement_handoff/第二问深化分析提示词.md)、[简短启动提示词](q2_refinement_handoff/发给Pro的简短提示词.txt)及[交接说明](q2_refinement_handoff/README.md)。
- [第二问改进复审包 ZIP](第二问_改进复审包.zip)：原 Pro 交付与精选最新验收证据，包内文件可用 [SHA256 清单](q2_refinement_handoff/MANIFEST.sha256) 核验。
- [第二问 Pro 深化交付](q2_refinement_delivery/README.md)与[第二问最终核查报告](review_q2_final_20260911/第二问最终核查报告.md)。
- [深化材料采纳与勘误](review_q2_final_20260911/采纳与勘误.md)、[新增数值独立复算](review_q2_final_20260911/numeric/numeric_audit.md)及[运行管理修复与验证](review_q2_final_20260911/runtime/runtime_audit.md)。
- [第三问 Pro 分析交接](q3_pro_handoff/README.md)、[完整分析与提示词](q3_pro_handoff/第三问分析与Pro交付说明.md)及[简短启动提示词](q3_pro_handoff/发给Pro的简短提示词.txt)。
- [第三问预分析证据](q3_pro_handoff/预分析结果与限制.md)、[相关论文方法核查](q3_pro_handoff/evidence/literature_review.md)及[第三问交接 ZIP](第三问_Pro分析交付包.zip)。

第一问结果的模型假设、验证范围和局限见交付说明、论文正文和最新审核报告。2026-09-10 的审核已在本机新目录完整复现，并独立核对热解、输出文件及四位小数；新证据保存在 `review_q1_20260910`。这支持当前假设下的数值正确性，不代表已经完成真实药材实验验证。

继续审查第一问模型假设时，建议先读最新审核入口，再对照原题、现有模型与原始结果。原交付中的历史运行记录和旧阅读说明保留原样，最新核验状态以审核报告为准。

## 第二问当前状态与继续审查

第二问已在本机新目录完成十阶段复现，并以独立径向离散与 Radau 方法复算；453600 个输出的四位小数和两张论文表 60 个数值全部一致。验收支持“附录3有效物性、固定几何中截面、前3h完整采样”口径下的数值答案。3h 时轴心/表面温度为 49.8495/49.9664 ℃，干基含水率为 1.7662/1.0081 kg/kg。

第二问深化交付现已完成最终核查。新增后处理真实重跑并通过290项独立数值检查；物理闭合推导另经精确代数核查。原正式Excel及两张论文表保留，可以在上述模型和前3h口径下完成第二问数值与机制分析的定稿。采用深化材料时，应修正一处含水率增量正负号的文字误写，并使用本次审核提供的运行管理修复副本；具体问题、验证范围与安装方式见最终核查报告。原Pro文件、原审核及正式数值均保留字节完整性。

第二问现已并入 [第一、二问论文阶段稿](paper/q1_q2_stage/README.md)，包含变物性模型、两张规定表、四张分析图、数值验证、扩散机制、参数情景及物理边界，并采用最终勘误。第一问原稿保留，新版仍是待续写第三、第四问的阶段论文。

上述结论不等于已模拟数天全过程，也不代表已经验证真实药材的物理预测误差。气固映射、潜热和携焓等扩展的数据需求，以及逐秒Excel仅覆盖前3h的工作解释，仍须在论文中明确。新增分析还表明，扩散系数虽在3h仍高于初值，但后期已回落，不能概括为全程单调增加。

Pro 可直接从当前 GitHub 仓库读取上述目录。ZIP 是便于上传的精选副本，并未包含全部重复的重跑中间产物；具体省略项见 [omitted_review_files.json](q2_refinement_handoff/omitted_review_files.json)。阅读时记录实际提交版本，并区分原 Pro 文件、本地重算和后续新增材料。

## 第三问当前进度

第三问已完成原题/模板核查、独立数学分析、相关论文方法核对，以及8个长时先导算例。已发现低含水率阶段的通量离散和4h后环境延拓会明显影响所需时长，详见交接说明。先导结果不是最终答案，尚未完成长期独立方法、时间误差和有限圆柱的完整验收，也未生成正式 `result3.xlsx`。请让 Pro 从第三问交接目录继续独立分析并返回新的 `q3_final_delivery/`。

## 获取大PDF原件

`分析与文献/foods-11-04045-v2.pdf`通过Git LFS保存。克隆仓库后如只看到三行指针，可安装Git LFS并运行：

```bash
git lfs pull
```

其他PDF原件及所有`readable`文本直接保存在普通Git中。
