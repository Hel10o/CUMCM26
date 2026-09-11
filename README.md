# libai

项目题目、建模资料、前三问计算交付，以及独立核验和第一、二问论文阶段稿。

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
- [第三问 Pro 交付](q3_final_delivery/README.md)、[第三问分析与答案](q3_final_delivery/第三问分析与最终答案.md)及[正式 result3.xlsx](q3_final_delivery/result3.xlsx)。
- [第三问本机审核入口](review_q3_20260911/README.md)、[审核与 Pro 再分析任务书](review_q3_20260911/第三问审核与Pro再分析提示词.md)及[简短启动提示词](review_q3_20260911/发给Pro的简短提示词.txt)。
- [206901 秒实际续算](review_q3_20260911/numeric/comparison_206901.json)、[独立数值核查](review_q3_20260911/numeric/numeric_audit.md)及[独立参考和复现工具审查](review_q3_20260911/runtime/runtime_review.md)。
- [第三问定向复审新交付](q3_refinement_delivery/README.md)、[新版 result3.xlsx](q3_refinement_delivery/output/result3.xlsx)及[新版第三问结论](q3_refinement_delivery/第三问最终复审与答案.md)。
- [前三问物理问题与新交付审核入口](review_q123_physics_20260911/README.md)、[潜热与干物质守恒主审核](review_q123_physics_20260911/前三问现状与物理闭合审核.md)及[独立物理/文献核查](review_q123_physics_20260911/model/物理闭合审查.md)。
- [前三问物理闭合Pro交接入口](q123_physics_pro_handoff/README.md)、[完整修正计算任务书](q123_physics_pro_handoff/前三问物理闭合与修正计算_Pro交接文档.md)及[简短启动提示词](q123_physics_pro_handoff/发给Pro的简短提示词.txt)。
- [Pro部分交付诊断与离线恢复](q123_physics_recovery_20260911/README.md)、[可直接上传的离线输入包](q123_physics_recovery_20260911/q123_physics_offline_inputs.zip)及[恢复执行提示词](q123_physics_recovery_20260911/恢复执行提示词.txt)。

第一问结果的模型假设、验证范围和局限见交付说明、论文正文和最新审核报告。2026-09-10 的审核已在本机新目录完整复现，并独立核对热解、输出文件及四位小数；新证据保存在 `review_q1_20260910`。这支持当前假设下的数值正确性，不代表已经完成真实药材实验验证。

继续审查第一问模型假设时，建议先读最新审核入口，再对照原题、现有模型与原始结果。原交付中的历史运行记录和旧阅读说明保留原样，最新核验状态以审核报告为准。

## 第二问当前状态与继续审查

第二问已在本机新目录完成十阶段复现，并以独立径向离散与 Radau 方法复算；453600 个输出的四位小数和两张论文表 60 个数值全部一致。验收支持“附录3有效物性、固定几何中截面、前3h完整采样”口径下的数值答案。3h 时轴心/表面温度为 49.8495/49.9664 ℃，干基含水率为 1.7662/1.0081 kg/kg。

第二问深化交付现已完成最终核查。新增后处理真实重跑并通过290项独立数值检查；物理闭合推导另经精确代数核查。原正式Excel及两张论文表保留，可以在上述模型和前3h口径下完成第二问数值与机制分析的定稿。采用深化材料时，应修正一处含水率增量正负号的文字误写，并使用本次审核提供的运行管理修复副本；具体问题、验证范围与安装方式见最终核查报告。原Pro文件、原审核及正式数值均保留字节完整性。

第二问现已并入 [第一、二问论文阶段稿](paper/q1_q2_stage/README.md)，包含变物性模型、两张规定表、四张分析图、数值验证、扩散机制、参数情景及物理边界，并采用最终勘误。第一问原稿保留，新版仍是待续写第三、第四问的阶段论文。

上述结论不等于已模拟数天全过程，也不代表已经验证真实药材的物理预测误差。气固映射、潜热和携焓等扩展的数据需求，以及逐秒Excel仅覆盖前3h的工作解释，仍须在论文中明确。新增分析还表明，扩散系数虽在3h仍高于初值，但后期已回落，不能概括为全程单调增加。

Pro 可直接从当前 GitHub 仓库读取上述目录。ZIP 是便于上传的精选副本，并未包含全部重复的重跑中间产物；具体省略项见 [omitted_review_files.json](q2_refinement_handoff/omitted_review_files.json)。阅读时记录实际提交版本，并区分原 Pro 文件、本地重算和后续新增材料。

## 第三问当前进度

第三问 Pro 完整交付已收到，并在本机从原附件完整复跑 N=2048 主模型与独立 80 阶 Radau 参考。主模型复跑与原临界时间只差约 2.66×10⁻⁷ s，独立参考与主解差约 0.0047 s；两者支持“4h后末小时观测均值平台、固定几何一维径向有效模型”下临界 **57.4740 h**、正式严格执行 **57.4741 h = 206906.76 s**。正式 Excel 已逐格核对与原未舍入数组一致；表5的50个含水率值、正式末行21个值与独立参考四位一致。

同一均值平台模型在 **206901 s** 的实际最大含水率为 **0.1500015713817738 > 0.15**，尚未达标。原交付另一个“4h后50℃、0.05”平台情景的N=512临界值为206900.352927 s，向上取整秒是206901 s；因此他人不同数字可能来自平台和取整口径，不应以更短判断更优，也不能仅凭数字认定对方方法。

首次审核还发现全Excel有8个值在独立参考下跨越四位舍入边界，以及复现工具的固定端点、报告旧数字、验证原地改写和防覆盖缺口，随后形成[定向复审任务书](review_q3_20260911/第三问审核与Pro再分析提示词.md)。原Pro的185文件、上游材料与历史论文保持完整；首次审核没有重新运行全部二维与参数套件。当前论文仍只纳入第一、二问。

第三问定向复审新包现已收到。新版统一采用历史80阶Radau及真实端点续算轨迹生成全工作簿，解决原8处末位差异；本机另从初态真实运行推荐80阶BDF冷启动，72429个水分值、表5的50个值四位全部一致。正式临界时间为206906.389932s（57.4740h），执行时间仍为206906.76s（57.4741h）。新包还实算了精细名义平台和时间平均平台。Windows只读验证路径兼容、导出/报告围绕新解更新及边界情景处理仍有工具问题，详见[本轮审核入口](review_q123_physics_20260911/README.md)。前述8格问题属于历史版本发现，不再作为新版正式表的未解决项。

## 前三问的物理适用范围

最新审核表明：第一问条件失水的潜热约45.59kJ，是原无潜热基线对流输入约4.801kJ的9.50倍；第二三问若在固定体积内把经验密度视为真实湿体密度，隐含干质量分别在3h和结束时增加约26.87%、115.39%。这两项属于实质物理闭合问题。将经验ρcp用于有效热容量可以明确简化口径，但不能声称真实质量—能量闭合已完成。

前三问原解及新版第三问可作为已声明有效模型的条件数值结果。下一阶段应优先统一空气/药材质量基准、气固平衡、同一蒸发通量和能量收支，再讨论守恒修正与时长变化；潜热影响不能仅凭题面未列参数而略去，也不能保持原失水轨迹只扣潜热便称为真实修正答案。详见[前三问现状与物理闭合审核](review_q123_physics_20260911/前三问现状与物理闭合审核.md)。现有论文未在本轮改写或重新编译。

## 获取大PDF原件

`分析与文献/foods-11-04045-v2.pdf`通过Git LFS保存。克隆仓库后如只看到三行指针，可安装Git LFS并运行：

```bash
git lfs pull
```

其他PDF原件及所有`readable`文本直接保存在普通Git中。
