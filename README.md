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
- [最新论文部分稿：前置章节与第一问](paper/第一问论文阶段稿.pdf)，[编辑与构建入口](paper/README.md)。
- [原交付第一问正文（保留历史版本）](q1_complete_delivery/q1_delivery/output/第一问论文正文.md)。
- [代码及复现入口](q1_complete_delivery/q1_delivery/run_all.py)。
- [2026-09-10 第一问独立审核入口](review_q1_20260910/README.md)。
- [第一问完成情况与答案审核报告](review_q1_20260910/第一问审核报告.md)。
- [第二问 Pro 完整交付说明](q2_final_delivery/README.md)与[模型选择记录](q2_final_delivery/analysis_decisions.md)。
- [第二问结果 Excel](q2_final_delivery/output/result2.xlsx)、[论文正文与两张结果表](q2_final_delivery/output/第二问论文正文.md)及[代码复现入口](q2_final_delivery/run_all.py)。
- [2026-09-11 第二问验收报告](review_q2_20260911/第二问验收报告.md)、[机器检查结果](review_q2_20260911/acceptance_checks.json)及[独立数值核查](review_q2_20260911/independent_numeric/独立数值核查.md)。
- [第二问深化审查提示词](q2_refinement_handoff/第二问深化分析提示词.md)、[简短启动提示词](q2_refinement_handoff/发给Pro的简短提示词.txt)及[交接说明](q2_refinement_handoff/README.md)。
- [第二问改进复审包 ZIP](第二问_改进复审包.zip)：原 Pro 交付与精选最新验收证据，包内文件可用 [SHA256 清单](q2_refinement_handoff/MANIFEST.sha256) 核验。

第一问结果的模型假设、验证范围和局限见交付说明、论文正文和最新审核报告。2026-09-10 的审核已在本机新目录完整复现，并独立核对热解、输出文件及四位小数；新证据保存在 `review_q1_20260910`。这支持当前假设下的数值正确性，不代表已经完成真实药材实验验证。

继续审查第一问模型假设时，建议先读最新审核入口，再对照原题、现有模型与原始结果。原交付中的历史运行记录和旧阅读说明保留原样，最新核验状态以审核报告为准。

## 第二问当前状态与继续审查

第二问已在本机新目录完成十阶段复现，并以独立径向离散与 Radau 方法复算；453600 个输出的四位小数和两张论文表 60 个数值全部一致。验收支持“附录3有效物性、固定几何中截面、前3h完整采样”口径下的数值答案。3h 时轴心/表面温度为 49.8495/49.9664 ℃，干基含水率为 1.7662/1.0081 kg/kg。

上述结论不等于已模拟数天全过程，也不代表已经验证真实药材的物理预测误差。继续审查应优先分析表面水分边界的含义与可识别性、潜热等扩展的物理闭合、升温与失水对扩散系数的竞争，以及题目要求的时域；详见本仓库的深化审查提示词。已验收原交付和原审核记录保留原样，新分析应写入新的 `q2_refinement_delivery/`。

Pro 可直接从当前 GitHub 仓库读取上述目录。ZIP 是便于上传的精选副本，并未包含全部重复的重跑中间产物；具体省略项见 [omitted_review_files.json](q2_refinement_handoff/omitted_review_files.json)。阅读时记录实际提交版本，并区分原 Pro 文件、本地重算和后续新增材料。

## 获取大PDF原件

`分析与文献/foods-11-04045-v2.pdf`通过Git LFS保存。克隆仓库后如只看到三行指针，可安装Git LFS并运行：

```bash
git lfs pull
```

其他PDF原件及所有`readable`文本直接保存在普通Git中。
