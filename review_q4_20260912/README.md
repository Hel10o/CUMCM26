# 2026-09-12 第四问本机核查

结论与边界见 [第四问接收核查与整体复审要点](第四问接收核查与整体复审要点.md)。本次接收原交付，核对实际数组/工作簿和题面，运行针对性检查，未改写Q4 v1或任何历史正式答案。

|证据|范围|
|---|---|
|[文件与表格审计](artifacts/artifact_audit.md)、[机器结果](artifacts/artifact_audit.json)|双清单、原题附件、完整Q4与870万格Q2工作簿|
|[独立Q4审核](agent_q4/Q4_独立核查.md)、[机器结果](agent_q4/saved_q4_audit.json)|方程/源码、表6、终点与数值对照、密度解释反证|
|[本机定向数值检查](numeric/numeric_audit.json)|已有结果读回、执行取整、配对几何算术；新运行72h均匀纯收缩FV算例|
|[Jacobian检查](numeric/geometry_checks/jacobian_flux_checks.json)、[维数退化](numeric/geometry_checks/dimension_reduction_check.json)|真实调用当前离散算子，全部断言通过|
|[原题页图](problem_pages/)|本机用Poppler渲染第2–4页供题意和附录逐式核对|
|[整体Pro交接](../q1234_overall_review_handoff/README.md)|四问版本选择、模型问题与改进合同|

在仓库根目录运行以下命令，输出只进入本审核目录。依赖版本及验证边界保存在机器报告中。虚拟环境不进入Git。

```powershell
# audit_numeric需要NumPy、SciPy、openpyxl
python -X utf8 -B review_q4_20260912/audit_numeric.py
# 表格审计另需要lxml；只读全部正式工作簿
python -X utf8 -B review_q4_20260912/artifacts/audit_artifacts.py
# 用新目录重做算子检查；已有同名结果会拒绝覆盖
python -X utf8 -B q4_complete_delivery/v1/source/geometry_checks.py --out-dir review_q4_20260912/numeric/geometry_checks_new
```

“检查通过”须按具体范围解释：这里没有本机全套Q4冷启动，没有新的精细二维正式终点场，没有真实药材实验误差或总相变焓验证，也没有本轮四问论文合稿和提交格式验收。
