# q3_final_delivery

## 最终答案

主情景为前4小时原始观测线性插值、以后保持末1小时均值，附录3物性从0秒使用，固定几何并忽略端部交换。临界时长 **57.4740 h**；正式表5与result3.xlsx结束于 **57.4741 h = 206906.76 s**，该时刻全网格最大含水率 **0.14999989358790375 < 0.15**。

这是一维轴向均匀有效模型的结果，不是脱离假设的实测时长。长时二维匹配网格比较显示端部约提前7.5—7.7秒；最后观测值保持与末段均值保持则相差约18.28分钟。四位小时格式不代表真实环境与几何也具有同等预测精度。

## 文件入口

| 文件 | 内容 |
|---|---|
| 第三问分析与最终答案.md | 可用于论文的模型、求解、表5、验证及限制 |
| result3.xlsx | 正式数值工作簿，Sheet1，3450×22，已全量独立回读 |
| output/table5.csv、table5.md | 6小时表及统一结束行；CSV保存未舍入数值 |
| output/main.npz | 初态、全部60秒内部网格、21半径输出、关键状态、事件两侧与执行端点 |
| output/end_event.json | 未舍入根、两侧最大值、数值预算及执行端点 |
| output/result3_unrounded.csv、curves.npz、*.png | 完整数值、时间曲线、径向剖面及二维对照 |
| validation/ | 空间、时间、独立参考、几何、边界、收支、算子和Excel回读证据 |
| source_access.md、inputs/UPSTREAM_MANIFEST.sha256 | 实际提交、读取途径、原始哈希和文献可用性边界 |
| source/、run_all.py | 本轮真实求解器、独立参考、验收、制表及复现入口 |

## 运行环境与命令

数值环境：Python 3.13.5，NumPy 2.3.5，SciPy 1.17.0；图形依赖Matplotlib。科学计算依赖见requirements.txt。正式Excel由artifact_tool生成；普通本地环境可用已通过内存序列化及全量数值回读测试的标准库OOXML导出，不需要Office或额外电子表格包。

```bash
python -m pip install -r requirements.txt
# 从原附件重新计算全部成功数值算例，顺序执行，避免多进程内存峰值
python run_all.py --out ../q3_rerun --scope full --excel-engine portable
# 只重算主模型、导出表5/Excel和端点，不能称为新一轮完整长期验收
python run_all.py --out ../q3_main_rerun --scope main --excel-engine portable
# 对现有交付执行独立验证；不会重算全部场景
python run_all.py --scope verify
```

完整数值套件按已成功算例配置编排，不重跑被内存限制中断的80×128全耦合试算。单个主计算积分约108秒，几何算例更耗时；实际运行时间取决于硬件、线性代数库和线程设置。建议顺序运行或最多两个数值进程，Excel导出放在所有大算例之后。

从单个配置运行：

```bash
python source/q3_solver.py --config validation/configs/main.json --out ../new_main --input inputs/attachment1.xlsx
python source/q3_reference.py --n 80 --method Radau --out ../new_reference80 --input inputs/attachment1.xlsx
python source/validate_results.py --xlsx-only
```

主配置的206906.76秒执行端点来自本次输入的收敛预算与量化规则，不是物理调参。改变原始数据、未来边界或传递系数后应重新求根及决定结束行，不能沿用该端点。普通情景配置不固定执行时间，默认导出其根右侧0.01秒的半离散合格状态。

## 实际验收摘要

主解与两种独立配置的临界差小于0.0064秒；6小时常规表格的水分差约1.17×10⁻⁸。水分累计收支残差4.697e-12，有效热量相对残差1.733e-11。前3小时回归不掩盖极少数末位舍入差异，详细数目见validation/q2_regression.json。

result3.xlsx独立读取了全部72429个水分单元格，数值和未舍入数组完全一致；3449个时间值及21个半径也通过检查。最后一行是第3450行，不是模板示例行数。最末中心显示0.1500但原值严格小于0.15，未以显示值作达标判断。

来源提交：`ab45397ce383fd968256997d61e3b701c8a9ac5f`。上传ZIP的153项清单文件逐一验证通过；原资料未覆盖，远程仓库未写入。包内MANIFEST.sha256核查最终交付自身，inputs/UPSTREAM_MANIFEST.sha256核查上游交接资料，两者用途不同。

## 不应扩大解释的结论

0.03秒是根据实际收敛和独立算法差异采用的工程数值预算，不是连续PDE的区间算术误差证书，更不是实际药材预测的置信区间。未来环境、气固边界映射、传质系数、潜热闭合和收缩仍需新数据验证；本问不得直接替代第四问。
