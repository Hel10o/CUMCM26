# 第一问完整数值交付

本项目求解固定圆柱中截面的显热扩散与非线性干基水分扩散。正式结果采用等效浓度差Robin边界，不显式加潜热；这是条件性题意基线，不是已由内部实验验证的完整气固相变模型。潜热诊断显示该简化有重大物理不确定性，阅读论文第8节。

## 快速查看

`output/result1.xlsx`为正式结果；两张表“温度”“水分浓度”，各1800×21个结果，t=1～1800 s、r=0～2 cm。`output/第一问论文正文.md`包含模型、全部规定结果表、图及实际验证；`evidence/MATERIALS.md`说明源文件和文献访问缺口。

## 安装及完整复现

本轮使用Python 3.13.5、NumPy 2.3.5、SciPy 1.17.0。数值部分依赖公开的NumPy、SciPy、Matplotlib，固定核心版本见requirements.txt；可在Windows、Linux或macOS的独立虚拟环境运行。不同BLAS或版本末位误差可能不同，应以输出审计和数值对照判断。

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python run_all.py --out reproduced
```

入口会重新读取原始附件，完成主求解、各网格和时间精度、守恒与独立解析/配点参考、二维热和潜热敏感性、Excel、图表、正文生成，并比较交付的未舍入结果。默认写入新的reproduced目录，不改动input或已交付output。

本轮Excel用预装的artifact_tool生成。普通本地环境没有该包时，`q1_excel.py`会走随代码提供的标准库OOXML回退实现，无需Excel应用或网络；**该回退路径未在本轮运行测试**。交付与复现验证实际执行的是artifact_tool路径，不能把回退也称为已验证。

完整运行会保存细网格快照及多个参考解，建议留出至少200 MB磁盘空间。入口将BLAS线程数设为1，避免大量小型线性代数任务过度开线程；主求解只有稀疏带状Jacobian，未生成10241×10241的稠密主矩阵。

## 分阶段运行

```bash
python source/q1_solver.py --input input/附件1.xlsx --out work --quadrature
python source/q1_validate.py --input input/附件1.xlsx --out work/validation
python source/q1_refine.py --input input/附件1.xlsx --out work/validation
python source/q1_excel.py --template input/result1_template.xlsx --raw work/q1_unrounded.npz --out work/result1.xlsx
python source/q1_report.py --input input/附件1.xlsx --out work
```

Windows单独运行上述命令前可设置 `$env:OPENBLAS_NUM_THREADS='1'`；Linux可在命令前加 `OPENBLAS_NUM_THREADS=1`。要完整复现正式结果，使用默认N=10240和容差，不把0.1 cm输出间隔当成内部网格。

## 文件说明

| 路径 | 含义 |
|---|---|
| input/附件1.xlsx | 原始附件完整字节，241条记录，哈希已核对 |
| input/result1_template.xlsx | 原始模板完整字节，没有覆盖 |
| source/q1_solver.py | SI计算、原始读取、局部D、节点中心有限体积、BDF、原始导出 |
| source/q1_validate.py | 常系数Bessel、实际热卷积、二维热、各网格、边界/守恒、敏感性 |
| source/q1_refine.py | 5120/10240与时间复核、独立非线性Chebyshev、二维热模态复核 |
| source/q1_excel.py | 模板展开及独立全表OOXML读取审计 |
| source/q1_report.py、paper_template.md | 从未舍入结果生成论文、8幅PNG/SVG图和表 |
| output/q1_unrounded.npz | 两场1801×21未舍入解，包含t=0，环境和体积权重平均 |
| output/*_unrounded.csv | 17位有效数字的公开文本数据，包含t=0 |
| output/T_n10240.npz、C_n10240.npz | 10241节点八个时刻快照、体积权重、通量累计与输出场 |
| output/validation/validation.json | 各实际验证指标，不是验证计划 |
| output/excel_audit.json | 全75600个数值和显示格式、端点、表格一致性核验 |
| output/figures/ | 环境2图、时间历程2图、径向分布2图、网格收敛2图，各PNG/SVG |
| output/reproduction_audit.json | 本轮新目录重跑完整入口的返回码及数值对比（交付时保存） |
| evidence/MATERIALS.md | 材料读取层级及未成功取得的PDF说明 |

## 数组读取示例

```python
import numpy as np
z = np.load('output/q1_unrounded.npz')
print(z.files)
# 温度单位℃；C单位kg水/kg干物质；半径已经转换为cm。
print(z['time_s'][1800], z['radius_cm'])
print(z['temperature_degC'][1800, [0, 20]])
print(z['moisture_dry_basis'][1800, [0, 20]])
```

正式Excel只保存四位小数的数值，显示0.0000；NPZ/全量CSV不提前舍入。小数格式仅是输出要求，不能证明物理预测有四位小数准确度。特别是中心C显示2.5500时，未舍入值并非严格等于初值。

## 模型适用边界

本文r表示中截面到轴线距离。实际二维有限圆柱热对照表明中截面端效应很小，但端面局部和全体积平均并不等于一维解。二维水分未运行；潜热只作为有明确附加假设的单向诊断，不应将其低温结果当作真实药材预测。

严格空气湿度—固相含水率映射和蒸发反馈缺少材料关系。原PDF公式图像及部分文献PDF没有成功获取，不能声称原题和四篇PDF均已全文核验；本问参数按用户明确公式及同源提取文本实现，附件数据本身完整且独立核验。

## 最终十进制舍入的额外回读

本轮另外执行 `python source/q1_rounding_audit.py --out output`，将实际Excel四位小数规则与独立800模态热解、240阶非线性水分配点解逐项比较。记录见rounding_reference_audit.json；该额外审计脚本可对完整入口生成的任何输出目录运行。
