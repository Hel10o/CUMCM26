# 四问整体模型复审 v1

2026-09-12，基于完整本地仓库提交 [`bbf7658ea020f45564f40f90153f91960a16a40c`](https://github.com/Hel10o/libai/commit/bbf7658ea020f45564f40f90153f91960a16a40c)。先读了根 README、整体交接与 Q4 接收核查，再按版本表读取现行答案、原题、代码与证据。本轮未使用离线输入 ZIP；个别文献网页访问失败时使用已经取得的本地原文页，并记录了阅读范围，没有把连接失败当材料缺失。

**结论：现行四问可保留为条件有效模型答案；物理闭合与强全域达标主张仍有重要限制。** Q2 完整过程已补齐，Q3/Q4 继续保留 57.4741 h / 51.0921 h。新证据支持 Q3 的粗二维正式点节点达标；Q4 精细二维直接补证仍需开展。下一轮最值得做的是 Q4 终点验证、传质系数口径对照和有工况依据的长期环境稳定性检查。

## 阅读顺序

1. [四问整体复审结论](四问整体复审结论.md)：逐问裁定、核心物理争议、新运行结果、最小定稿与提升方案。
2. [问题清单与改进优先级](问题清单与改进优先级.md)：P0/P1/P2、证据位置、影响、最小修复和验收门槛。
3. [统一模型假设与论文修订表](统一模型假设与论文修订表.md)：统一符号/单位/公式、现有或待防止表述的逐条修订、合稿结构。保留的历史原文不覆盖。
4. [最小补算计划](最小补算计划.md)：三个具体实验合同，明确已做部分、剩余建议及停止条件。
5. [来源清单](来源清单.json)、[运行配置](configs/review_contract.json)、[交付验证](evidence/delivery_validation.json)与[文件哈希](MANIFEST.sha256)。

## 本轮新增了什么证据

|工作|真实执行与结论|原始记录|
|---|---|---|
|一维环境后段压力测试|10个n40情景+4个基线/降温加密；从4 h已存场开始。降1 K使Q3/Q4根延后约1.8673/1.6373 h。不是物理误差区间。|[源码](source/environment_probe.py)、[14组JSON/NPZ](evidence/environment/)、[Q3日志](q3_environment.log)、[Q4日志](q4_environment.log)、[Q3加密日志](q3_environment_refined.log)、[Q4加密日志](q4_environment_refined.log)|
|环境证据独立后处理|14组哈希、共同内部初态、边界与独立多项式全径向事件核对均通过；没有另求PDE。|[独立短评](reviews/environment_check/环境情景独立复核短评.md)、[机器结果](reviews/environment_check/environment_evidence_audit.json)|
|二维正式时刻局部续算|Q3 80×256的Cmax=0.149998606290；Q4 80×128的Cmax=0.150001406623。后者为粗网格未达标，不能抹去或冒充精细结论。|[几何报告](reviews/geometry/几何降维与全域阈值专项复审.md)、[两段续算配置/结果](reviews/geometry/endpoint_audit.json)、[源码及完整场](reviews/geometry/README.md)|
|保存场物理诊断|Q4真实密度解释的干质量矛盾、轴长修复方向、稳温期潜热反例、ρd hm缩放。仅代数/积分，没有新时长。|[物理报告](reviews/physics/物理闭合独立裁定.md)、[机器诊断](reviews/physics/saved_field_physics_diagnostics.json)、[源码与数据](reviews/physics/README.md)|
|原文与模型合同审阅|题意、现行/历史来源、论文原句逐条定位，未编译或重写正式稿。|[论文专项](reviews/paper/论文题意与现行表述独立审查.md)|

## 现行正式版本

|问题|正式文件|范围|
|---|---|---|
|Q1|[result1.xlsx](../../q1_complete_delivery/q1_delivery/output/result1.xlsx)|1800 s逐秒径向输出，附录2。|
|Q2|[最新完整result2.xlsx](../../q4_complete_delivery/v1/q123_closeout/result2.xlsx)|每表206907行，至206906.76 s；源为同包`output/q23_unified.npz`。|
|Q3|[现行result3.xlsx](../../q3_refinement_delivery/output/result3.xlsx)|57.4741 h条件执行值，历史8格已修复。|
|Q4|[result4.xlsx](../../q4_complete_delivery/v1/output/result4.xlsx)|51.0921 h条件执行值，源为`output/main.npz`。|

所有旧版本、正式 Excel、原数组和清单保持原字节。本轮完整接收哈希复核及 Git 变更范围检查见交付验证。历史 F、R_L 不作为新主答案；本报告不是已经生成的四问最终论文。

## 复现与核对

本机已有运行环境为 Python 3.13.14、NumPy 2.5.3、SciPy 1.18.1；存放于 `review_q4_20260912/.venv`，不提交环境。新程序的精确条件在每组 JSON 和配置内。只检查本轮文件与来源而不重跑 PDE：

```powershell
& 'D:/Desktop/CUMCM26/review_q4_20260912/.venv/Scripts/python.exe' -X utf8 -B q1234_overall_review_delivery/v1/source/finalize_review.py --check
```

环境脚本会拒绝覆盖已有同名结果；如需重算，用新的输出目录。以下示例只重算一个基线，其余参数见配置，**不是本轮又一次已执行命令**：

```powershell
$env:OPENBLAS_NUM_THREADS='1'
& 'D:/Desktop/CUMCM26/review_q4_20260912/.venv/Scripts/python.exe' -X utf8 -B q1234_overall_review_delivery/v1/source/environment_probe.py --case q4 --n 60 --scenario baseline --out q1234_overall_review_delivery/reproduction_new/environment
```

专项脚本有默认输出到自身目录的设计，冻结后不要原地重跑；复制到明确新版本并核对根目录/输出参数后执行。旧 Q4 `check_numerics.py` 也会默认写原验证文件，不能作为“纯只读”复审命令直接运行。

## 打包与未完成事项

父目录的 `四问整体复审报告_v1.zip` 是本轮报告、源码、日志和新原始场的打包，归档路径保留 `q1234_overall_review_delivery/v1/`。它**不重复包含**原题、四问旧原始交付和此前大文件；完整审阅需配本仓库基线，或原来的“`四问整体复审输入包.zip`”。包内 `MANIFEST.sha256` 覆盖本版本其他全部文件；包外 `四问整体复审报告_v1.zip.sha256` 核对归档。`来源清单.json` 的哈希对应读取基线，不因本轮根 README 更新而改写历史来源。

本轮复审交付已完成；**尚未完成的模型工作**为：精细二维正式点补证/连续严格界、气固映射与材料数据标定、真实质量—能量闭合支线、四问合稿修改编译及整链冷启动导出。报告里的建议不会被视为已运行成果。下次工作按[最小补算计划](最小补算计划.md)开展，并在新版本中记录任何答案变化。
