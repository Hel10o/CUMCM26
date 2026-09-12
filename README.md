# libai

项目题目、建模资料、四问计算交付、独立核验，以及四问 LaTeX 论文初稿。

论文摘要现已按每问“模型方法—主要结果—结果解释”重写，并明确温湿反馈分解、极值终点判定及干基守恒收缩处理的方法特色，见[摘要修订记录](paper/q1234_draft_v1/evidence/abstract_revision_20260912/摘要修订说明.md)。

最新论文入口：[四问论文初稿 PDF](paper/q1234_draft_v1/四问论文初稿_v1.pdf)、[LaTeX 主文件](paper/q1234_draft_v1/main.tex)、[构建与验收说明](paper/q1234_draft_v1/README.md)、[AI工具使用详情](paper/q1234_draft_v1/AI工具使用详情.pdf)。本版根据实际读取的 `ad9c6766d6db2f21ee61d6d5a1a7a9c54c28f377` 四问结果及整体复审整理，采用 2026 年官方电子稿格式，保留条件模型的适用范围与 Q4 二维补证限制；是待队员人工审阅的完整初稿，尚不等同于完成最终提交验收。旧论文阶段稿保留。

第四问交付已接收并完成[本机针对性核查](review_q4_20260912/README.md)，随后已完成[四问整体批判性模型复审](q1234_overall_review_delivery/v1/README.md)。复审基于提交 `bbf7658` 的实际题面、现行答案、代码和数组，新增有限环境情景、二维正式点续算及物理闭合诊断；结论和下一轮行动见[整体结论](q1234_overall_review_delivery/v1/四问整体复审结论.md)、[P0/P1/P2清单](q1234_overall_review_delivery/v1/问题清单与改进优先级.md)、[论文修订表](q1234_overall_review_delivery/v1/统一模型假设与论文修订表.md)和[三个补算合同](q1234_overall_review_delivery/v1/最小补算计划.md)。[本轮报告与证据ZIP](q1234_overall_review_delivery/四问整体复审报告_v1.zip)只包含新增复审成果；此前[完整交接与离线输入包](q1234_overall_review_handoff/README.md)保留为本轮输入合同，原交付未覆盖。

当前正式文件为：[Q1 result1](q1_complete_delivery/q1_delivery/output/result1.xlsx)、[Q2最新全程result2](q4_complete_delivery/v1/q123_closeout/result2.xlsx)、[Q3现行result3](q3_refinement_delivery/output/result3.xlsx)、[Q4 result4](q4_complete_delivery/v1/output/result4.xlsx)。Q3执行 **57.4741h**，Q4执行 **51.0921h**，均为已声明有效模型下的条件结果；二维配对校正属于估计，不是连续全域严格误差界。以下各节保留历次验收过程，现行版本优先按本段和整体复审版本表读取。

整体复审未检出迫使重写现行四份Excel的确定性计算硬错。新直接续算中，Q3的80×256二维正式点全节点达标，Q4的80×128粗网格正式点仍略高于阈值，因此Q4精细二维直接补证仍需完成；这不等同于推翻精细一维与配对校正估计。人工后段降1K情景使Q3/Q4根分别延后约1.87h/1.64h，说明长期工况假设比末位数值更值得验证。湿度映射、真实密度和潜热闭合仍限制物理预测；这些结论已在后续四问初稿中说明，历史答案与复审证据未覆盖。

用户已选择保留题给物性、一维径向有效传热—传质、无显式潜热的主线；二维检验目标输出和全域达标，潜热放在扩展与局限讨论。已收到[题意复审交付](q123_requirements_review_delivery/README.md)，其尚未闭合的含潜热候选R_L和[此前四组F比较](q123_model_selection_delivery/v1/README.md)均保留为背景，不覆盖用户当前选择。旧结果仍按原假设保留，不能声称官方公式已经包含潜热。

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
- [最新四问论文初稿](paper/q1234_draft_v1/四问论文初稿_v1.pdf)及[编辑与构建入口](paper/q1234_draft_v1/README.md)。
- [历史论文部分稿：第一问与第二问](paper/q1_q2_stage/第一二问论文阶段稿.pdf)，[当时编辑与构建入口](paper/q1_q2_stage/README.md)。
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
- [前三问四组模型 Pro 交付 v1](q123_model_selection_delivery/v1/README.md)、[影响评估](q123_model_selection_delivery/v1/前三问二维与潜热影响评估.md)及[模型假设契约](q123_model_selection_delivery/v1/模型推导与假设契约.md)。
- [历史模型选择质疑交接](q123_requirements_review_handoff/README.md)、[完整重分析文档](q123_requirements_review_handoff/前三问模型选择质疑与题意约束重分析_Pro交接文档.md)及[对应历史提示词](q123_requirements_review_handoff/发给Pro的提示词.txt)。
- [题意复审 Pro 原交付](q123_requirements_review_delivery/v1/README.md)及[原始ZIP](q123_requirements_review_delivery/q123_requirements_review_delivery_v1.zip)。
- [第四问与前三问收尾交接](q4_pro_handoff/README.md)、[项目论文阅读清单](q4_pro_handoff/第四问论文阅读清单.md)及[离线输入包](q4_pro_handoff/q4_inputs.zip)。
- [第四问完整交付](q4_complete_delivery/README.md)、[第四问论文正文](q4_complete_delivery/v1/第四问论文正文.md)、[表6](q4_complete_delivery/v1/output/表6.md)及[前三问收尾](q4_complete_delivery/v1/q123_closeout/README.md)。
- [第四问本机接收核查](review_q4_20260912/第四问接收核查与整体复审要点.md)与[四问整体复审交接](q1234_overall_review_handoff/README.md)。
- [四问整体模型复审交付](q1234_overall_review_delivery/v1/README.md)、[来源清单](q1234_overall_review_delivery/v1/来源清单.json)、[本轮报告ZIP](q1234_overall_review_delivery/四问整体复审报告_v1.zip)及[ZIP哈希](q1234_overall_review_delivery/四问整体复审报告_v1.zip.sha256)。

第一问结果的模型假设、验证范围和局限见交付说明、论文正文和最新审核报告。2026-09-10 的审核已在本机新目录完整复现，并独立核对热解、输出文件及四位小数；新证据保存在 `review_q1_20260910`。这支持当前假设下的数值正确性，不代表已经完成真实药材实验验证。

继续审查第一问模型假设时，建议先读最新审核入口，再对照原题、现有模型与原始结果。原交付中的历史运行记录和旧阅读说明保留原样，最新核验状态以审核报告为准。

## 第二问当前状态与继续审查

2026-09-12收到的新[完整result2](q4_complete_delivery/v1/q123_closeout/result2.xlsx)已经覆盖逐秒全过程至206906.76s，每张表206907个数据行。本机全量核对8,690,094个温湿数值与同源未舍入轨迹的四位舍入一致；旧前3h表格保留。全时域模型与输出解释见[收尾说明](q4_complete_delivery/v1/q123_closeout/第二问全时域收尾.md)。下面关于“前3h”的内容描述历史验收范围，不再表示现行完整Excel仅到3h。

第二问已在本机新目录完成十阶段复现，并以独立径向离散与 Radau 方法复算；453600 个输出的四位小数和两张论文表 60 个数值全部一致。验收支持“附录3有效物性、固定几何中截面、前3h完整采样”口径下的数值答案。3h 时轴心/表面温度为 49.8495/49.9664 ℃，干基含水率为 1.7662/1.0081 kg/kg。

第二问深化交付现已完成最终核查。新增后处理真实重跑并通过290项独立数值检查；物理闭合推导另经精确代数核查。原正式Excel及两张论文表保留，可以在上述模型和前3h口径下完成第二问数值与机制分析的定稿。采用深化材料时，应修正一处含水率增量正负号的文字误写，并使用本次审核提供的运行管理修复副本；具体问题、验证范围与安装方式见最终核查报告。原Pro文件、原审核及正式数值均保留字节完整性。

第二问曾并入 [第一、二问论文阶段稿](paper/q1_q2_stage/README.md)，包含变物性模型、两张规定表、四张分析图、数值验证、扩散机制、参数情景及物理边界，并采用最终勘误。该阶段稿与第一问原稿保留；当前完整论文入口见页首。

上述历史前3h验收不代表已经验证真实药材的物理预测误差；现行完整轨迹与工作簿已由后续收尾补齐，见本节首段。气固映射、潜热和携焓等扩展的数据需求仍须在论文中明确。新增分析还表明，扩散系数虽在3h仍高于初值，但后期已回落，不能概括为全程单调增加。

Pro 可直接从当前 GitHub 仓库读取上述目录。ZIP 是便于上传的精选副本，并未包含全部重复的重跑中间产物；具体省略项见 [omitted_review_files.json](q2_refinement_handoff/omitted_review_files.json)。阅读时记录实际提交版本，并区分原 Pro 文件、本地重算和后续新增材料。

## 第三问当前进度

第三问 Pro 完整交付已收到，并在本机从原附件完整复跑 N=2048 主模型与独立 80 阶 Radau 参考。主模型复跑与原临界时间只差约 2.66×10⁻⁷ s，独立参考与主解差约 0.0047 s；两者支持“4h后末小时观测均值平台、固定几何一维径向有效模型”下临界 **57.4740 h**、正式严格执行 **57.4741 h = 206906.76 s**。正式 Excel 已逐格核对与原未舍入数组一致；表5的50个含水率值、正式末行21个值与独立参考四位一致。

同一均值平台模型在 **206901 s** 的实际最大含水率为 **0.1500015713817738 > 0.15**，尚未达标。原交付另一个“4h后50℃、0.05”平台情景的N=512临界值为206900.352927 s，向上取整秒是206901 s；因此他人不同数字可能来自平台和取整口径，不应以更短判断更优，也不能仅凭数字认定对方方法。

首次审核还发现全Excel有8个值在独立参考下跨越四位舍入边界，以及复现工具的固定端点、报告旧数字、验证原地改写和防覆盖缺口，随后形成[定向复审任务书](review_q3_20260911/第三问审核与Pro再分析提示词.md)。原Pro的185文件、上游材料与历史论文保持完整；首次审核没有重新运行全部二维与参数套件。当前论文仍只纳入第一、二问。

第三问定向复审新包现已收到。新版统一采用历史80阶Radau及真实端点续算轨迹生成全工作簿，解决原8处末位差异；本机另从初态真实运行推荐80阶BDF冷启动，72429个水分值、表5的50个值四位全部一致。正式临界时间为206906.389932s（57.4740h），执行时间仍为206906.76s（57.4741h）。新包还实算了精细名义平台和时间平均平台。Windows只读验证路径兼容、导出/报告围绕新解更新及边界情景处理仍有工具问题，详见[本轮审核入口](review_q123_physics_20260911/README.md)。前述8格问题属于历史版本发现，不再作为新版正式表的未解决项。

## 前三问的物理适用范围

最新审核表明：第一问条件失水的潜热约45.59kJ，是原无潜热基线对流输入约4.801kJ的9.50倍；第二三问若在固定体积内把经验密度视为真实湿体密度，隐含干质量分别在3h和结束时增加约26.87%、115.39%。这两项属于实质物理闭合问题。将经验ρcp用于有效热容量可以明确简化口径，但不能声称真实质量—能量闭合已完成。

前三问原解及新版第三问可作为已声明有效模型的条件数值结果。此前物理审核提出统一空气/药材质量基准、气固平衡、同一蒸发通量和能量收支的扩展路线；用户现选择先保留有效模型推进第四问，这些物理问题继续作为适用范围和扩展讨论，不声称已经解决。详见[前三问现状与物理闭合审核](review_q123_physics_20260911/前三问现状与物理闭合审核.md)。本轮交接准备没有改写或重新编译历史论文。

## 四组比较交付与当前重新分析

2026-09-12 收到的 `q123_model_selection_delivery/v1` 保留四组比较文档、源码、配置、输出、日志和原清单。其报告认为潜热效应显著、中截面可降维，但整根失水和全域终点需分别讨论。这些是 Pro 在新增边界与物性解释下的条件结论，本机本轮未运行求解或数值验收。

随后质疑集中在：第一问 F 未保留题给 2600 比热，第二三问 F 只以经验密度初值确定固定干密度，且新增了未标定的平衡含水率与气膜假设。[题意复审交付](q123_requirements_review_delivery/v1/README.md)恢复题给物性，但推荐的R_L仍缺材料边界关系，没有新PDE解。本机只接收和阅读该包，未运行其检查器或复算；约73.44h不作为新验收的正式时长。

上轮包内关于 ZIP 分发、运行与验证的说明按原样保存；本次收到的是解压后的目录，GitHub 同步该目录，没有重新制作上轮同名 ZIP。新增材料的传输与字节检查不等于数值验收。

## 第四问当前交付与整体复审

第四问已交付在[q4_complete_delivery/v1](q4_complete_delivery/v1/README.md)。采用附录4、附件2线性半径、均匀径向材料收缩和恒长度，从题给初态重新求解；一维临界183931.211715489s，严格执行183931.56s=51.0921h，末态最大C=0.14999982116131336。表6、3066行result4、正文和未舍入轨迹齐备，本机已核对对应关系并完成定向算子/纯收缩检查。

同包`q123_closeout/`补齐第二问完整逐秒导出与前三问同物理几何证据。Q3端部配对根差约−7.4740s；Q4约−0.03s。Q4原粗二维根仍含径向误差，正式时刻的二维达标结论使用配对校正估计，不能称为精细二维直接求值。此次未在本机重跑整套四问PDE，也未合并重编历史论文。

整体复审优先处理有效密度/干质量口径、空气含水率边界、潜热和能量解释、4h后环境、收缩假设及一维适用范围。原交付中的403同步说明保持原样；本机新接收状态与Pro新任务以[最新核查报告](review_q4_20260912/第四问接收核查与整体复审要点.md)和[整体复审交接](q1234_overall_review_handoff/README.md)为准。

## 获取大PDF原件

`分析与文献/foods-11-04045-v2.pdf`通过Git LFS保存。克隆仓库后如只看到三行指针，可安装Git LFS并运行：

```bash
git lfs pull
```

其他PDF原件及所有`readable`文本直接保存在普通Git中。
