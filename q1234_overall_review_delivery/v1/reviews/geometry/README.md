# 几何与全域阈值复审证据

先读[专项报告](几何降维与全域阈值专项复审.md)。本专题读取Git提交`bbf7658ea020f45564f40f90153f91960a16a40c`，仅向当前目录生成文件。

实际新运行：

1. `audit_geometry_endpoints.py`：从已保存二维状态作局部续算，生成`endpoint_audit.json`、完整正式点温湿场及日志。Q3正式点80×256全节点达标；Q4正式点80×128粗网格尚未达标。两者不构成连续模型严格误差界，也不是完整冷启动。
2. `audit_saved_geometry_scope.py`：对同网格保存场重新积分，生成`saved_geometry_scope.json`和日志；此项只读回已有PDE结果。

实际命令（仓库根目录，PowerShell）：

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
& review_q4_20260912/.venv/Scripts/python.exe q1234_overall_review_delivery/v1/reviews/geometry/audit_geometry_endpoints.py
& review_q4_20260912/.venv/Scripts/python.exe q1234_overall_review_delivery/v1/reviews/geometry/audit_saved_geometry_scope.py
```

两项运行退出码均为0；脚本完成后拒绝覆盖已有JSON。再次执行应复制脚本至等深度的新版本目录或修改输出配置，不删除或覆盖原证据。Python3.13.14、NumPy2.5.3、SciPy1.18.1，具体配置与源数据SHA256见JSON。生成文件哈希见`MANIFEST.sha256`。

来源定位见专项报告，主要输入为Q4的`validation/geometry/`原始NPZ、JSON及`source/geometry_solver_executed.py`。本次继承原FV算子及已存前史，独立性只在重新组织局部续算、端点判据和后处理；不能称为独立完整二维求解器。
