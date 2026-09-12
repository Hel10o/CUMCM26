# 前三问二维、潜热与交互作用选型交付 v1

## 先读什么

从《前三问二维与潜热影响评估.md》看实际比较，再读《最终建模思路.md》与《最终模型选择表.csv》。完整单位、初边值与焓推导见《模型推导与假设契约.md》；原文访问和参数身份见《参数与文献证据表.md》。本目录不覆盖原基线、审核或论文。

## 核心结论

在主条件情景C_eq=0.075下，有潜热的二维端面使Q1/Q2整根失水增加约13.87%/9.93%，但中截面差很小。Q3无潜热端面效应约−16.57s，有潜热约−237.37s，交互项约−220.79s。推荐Q1/Q2中截面一维分析、整体量二维；Q3二维全域终判。

主二维潜热模型的等号临界约73.4446h，不是已经识别的真实药材唯一时长。共同F与旧B的气固映射、容量和携焓解释不同；其差异单列，不能全算成潜热。原正式B的57.4741h执行值保留。本轮没有重新生成正式Excel或全文论文。

## 实际来源及范围

GitHub根README与新任务书实际提交为f5c06bb276062b52b61c092f16c436c9d971f4f9；资料按1feb7686a371179bc6f545217e229f388a9bc379读取。输入CSV的18123字节与Git对象d55880786a62ff55933c045998a6a7de033b83c5一致，覆盖0–14400s的241个时点。

本轮没有收到离线输入ZIP，也没有声称核验离线INPUT_MANIFEST。原XLSX和冻结NPZ二进制逐元素复核、原PDF页图视觉逐式核对未完成；已读的源码段、原文页提取文本、出版社HTML和原始失败消息逐项列于source_access.json。新计算实际使用核验后的完整CSV。

## 运行环境与冷启动

实跑环境为Python3.13.5、NumPy2.3.5、SciPy1.17.0。代码不用本机固定绝对路径找输入；要求从新目录冷启动，目标已经存在会报错。BLAS单线程是为了避免共享环境线程竞争，网格及物理参数由configs中的JSON指定。

```bash
python -m pip install -r requirements.txt
python source/run_selection.py --scope main --run-root ../q123_model_selection_reproduce
```

该命令从原始环境CSV重新计算10个主结果（Q1及Q23各有B和四组F），再在新根目录生成比较CSV，不改本交付。它不会复用旧温湿轨迹作为新解初值，也不会把原B预测当实验参数标定。读完四组原始结果后，可运行新根目录自己的validate.py。

```bash
python ../q123_model_selection_reproduce/source/validate.py --report-root ../q123_reproduce_checks
```

`--scope all`在主结果之外追加48格配对、单独轴向加密、径向192格、紧Radau、气膜/平衡情景和关闭端面的检查；它不重跑全部历史仓库，也不自动重跑独立H/C参照。这里只通过smoke真实检查过统一工作流；主算例本身均已逐项真实执行，没有再重复完整main/all组合一遍。

独立H/C状态、单元中心、无储量表面Radau参照可以在任一含source和inputs的新工作根内单独运行。下面的目标目录必须不存在；384和768格可形成一组独立收敛检查，不能把粗独立离散与精细主解的差全当模型差。

```bash
python source/independent_cell_fv_jac.py 384 0.075 ../independent_HC_384
python source/independent_cell_fv_jac.py 768 0.075 ../independent_HC_768
```

`source/analyse.py`只读取输入和output，写入所在根的analysis；`source/make_report.py`从这些CSV和原数组生成报告/图。完整评估报告还需要本交付包含的敏感性、独立参照与单独轴向加密输出，不应在只有main的目录中宣称完整报告依赖齐全。

## 成本

主算例逐项实测耗时见validation/main_run_costs.json。本次共享容器下，最重主二维作业约十几分钟；更轻的一维与独立求解快得多。总耗时包含不同时间的并发及反复读写，不将各作业耗时简单相加冒充用户复算的墙钟时间，也不承诺固定完成时长。

## 数据与证据索引

|路径|内容|
|---|---|
|inputs/environment_extracted.csv|唯一实际环境数值输入，原CSV字节完整|
|inputs/inherited_baseline_evidence.json|明确标识的旧审核JSON数值；非冻结NPZ逐元素验证|
|configs/|每个实际场景的参数文件|
|output/<case>/solution.npz|未舍入场、时间、全域指标、通量/能量数据|
|output/<case>/history.csv|与NPZ重叠的便读时序；不是另一来源|
|output/<case>/ledger.json、result.json|分侧/端面累计水热量、事件、实际耗时和守恒残差|
|analysis/sampled_fields.csv|Q1/Q2规定时刻和半径、Q3每6h采样，17位写出|
|analysis/stage_summary.csv|中心、侧面、端面、整体水/能量比较|
|analysis/factorial_contrasts.csv|B→F00、G0/G1、L1/L2及交互项|
|analysis/paired_convergence.csv|匹配径向网格的二维配对误差|
|analysis/separate_axis_radial_refinement.csv|轴向与径向单独加密|
|validation/independent_checks_v1/|独立几何/账本重算与合成极限测试，分别标识|
|validation/run_bindings.json|每次运行的配置、输入、实际核心源码和未舍入结果散列|
|validation/rejected_runs/|误参数试算、超时/内存失败等原日志和隔离输出，不用于主结论|
|figures/|由未舍入结果生成的图，图源对应表也保留|
|source_access.json、MANIFEST.sha256|实际读取范围和本轮完整文件清单|

## 只读验收与误差

`python source/validate.py`不带report-root时只输出到标准输出，不改输入、配置或结果；新报告目录必须不存在。运行前后的散列对照和防覆盖反例在validation内保留。合成测试、原题退化试算、新物理情景与旧证据不混用。

本轮主数值可分辨约4分钟几何效应和约14小时潜热效应，但不能宣称连续PDE精确到0.36s。Q1及Q2有潜热的中截面微小几何差与时间误差同量级，仅支持工程降维，不支持严格零影响或四位完全一致。600s续算是本轮数值缓冲，不是物理工艺保证。

## 分发文件

完整档案保留本目录全部实际材料，含原数组、历史运行失败隔离证据及便读CSV。轻量阅读包只包含文档、源码、配置、输入、比较CSV、图和验证摘要；它不包含全部PDE原数组，不能当作完整数值证据包。具体打包范围另见PACKAGE_CONTENTS.json。

## 人工审查

本交付是AI辅助计算与技术审查材料，不自动成为参赛队的核心建模定稿。采用时应由队员检查模型选择、未知参数假设、代码结果与引文；AI使用过程须据实际填写，不能把未做的人工核验或未完成的原PDF视觉核验写成已经完成。

完整档案是研究与审计交付，不是可直接提交的比赛支撑压缩包。它保留多网格和重复时序，体积大于用户所附2026论文规范的20MB支撑材料限额；正式参赛支撑材料应另按实际采用模型整理最小可复算代码、必要输入与核验，并完成匿名化和AI使用说明。
