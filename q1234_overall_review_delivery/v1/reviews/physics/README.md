# 物理闭合专项

主报告：[物理闭合独立裁定.md](物理闭合独立裁定.md)。这是新报告，未覆盖任何正式答案或历史清单。

本轮实际读取 Git `bbf7658ea020f45564f40f90153f91960a16a40c`，仅运行保存场代数和积分诊断。未重跑 Q1–Q4 PDE；没有新达标时间、温度场或材料参数标定。

|产物|作用|
|---|---|
|[`diagnose_saved_fields.py`](diagnose_saved_fields.py)|读取冻结 Q1/Q4 数组和附件；独立密度积分、长度反证、条件性热流和边界系数缩放|
|[`saved_field_physics_diagnostics.json`](saved_field_physics_diagnostics.json)|实际结果、输入 SHA256、基线提交、运行版本及条件说明|
|[`diagnose_saved_fields.log`](diagnose_saved_fields.log)|成功运行的完整标准输出|
|[`q4_implied_dry_mass_curve.csv`](q4_implied_dry_mass_curve.csv)|3067 个保存时刻的反证性干质量比；不是新PDE轨迹|
|[`sources.json`](sources.json)|实际读取的主要本地文件、范围和本次官方网页|

成功运行命令，退出码 0：

```powershell
$env:OPENBLAS_NUM_THREADS='1'
& 'D:/Desktop/CUMCM26/review_q4_20260912/.venv/Scripts/python.exe' -X utf8 -B q1234_overall_review_delivery/v1/reviews/physics/diagnose_saved_fields.py
```

依赖为 NumPy、SciPy、openpyxl；本次实际 Python 3.13.14、NumPy 2.5.3、SciPy 1.18.1。初次试用 PATH Python 与 bundled Python 均因缺 SciPy 退出，未产生数值结论；随后使用上述已存在虚拟环境成功。此环境问题不是原正式答案错误。

脚本重新运行会覆盖本专项同名诊断 JSON/CSV，仅写其所在新目录，不写任何冻结交付。整体复审完成并冻结后，如需再运行，应把脚本复制至新版本目录并相应确认仓库根路径。

物理诊断前提必须随数值一并引用：经验ρ作真实湿密度的积分是反证；条件潜热使用附加干质量归一化及 2.45 MJ/kg 常值，不是材料实测潜热；压力和空气 W 的解释均为条件假设。
