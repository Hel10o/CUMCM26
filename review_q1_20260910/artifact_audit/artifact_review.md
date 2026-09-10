# 第一问交付文件独立审计

审计日期：2026-09-10。对象：`q1_complete_delivery/q1_delivery`。本次只读交付原件；独立审计程序和证据均写在本目录。

## 结论

交付文件完整性、Excel 输出契约、两张规定论文表、未舍入 CSV/NPZ 之间的一致性全部通过。未发现漏行、漏列、数值字符串、舍入错误或论文表抄写错误。本结论是对当前交付文件的实测检查，不以交付包自带的 PASS 字段代替验证。

本审计不重跑主 PDE 求解；模型物理正确性及新的独立求解由并行审查负责。下文中的参考解比较读取的是交付时保存的 Bessel/Chebyshev 数组，属于旧参考解的本次重新比对。

## 实测内容

- 原附件 1 与包内 `input/附件1.xlsx` 逐字节相同；原结果模板与包内 `input/result1_template.xlsx` 逐字节相同。
- Excel 严格包含 `温度`、`水分浓度` 两张表。各表数据区为 `B2:V1801`，共有 37,800 个数值；`A2:A1801` 为 1–1800 s，`B1:V1` 为 0–2 cm、步长 0.1 cm。
- 全部 75,600 个结果均为有限数值，显示格式为 `0.0000`，数值本身与对应未舍入值格式化至四位小数后的结果完全相等。没有省略号、空缺或多余数据区。
- 论文第 6 节两张表由审计程序直接解析：7 个指定时刻 × 5 个指定半径，70 个值全部保留四位小数，与 Excel、两份规定表 CSV 和 NPZ 完全一致。
- `temperature_unrounded.csv`、`moisture_unrounded.csv` 的 1801 × 21 数值（含初始时刻）与 NPZ 解逐位相同。
- 保存的 800 模态热参考解与正式解最大差为 7.86582532441571e-09 K，四位小数差异 0 个；保存的 240 阶水分配点解最大差为 1.5206492189889786e-06 kg/kg，四位小数差异 0 个。
- 8 个 Markdown 图片链接均有效；8 对 PNG/SVG 图均存在。已目视查看原有 Excel 局部预览与温度径向分布图，所查看区域清晰；未据此声称重新渲染并检查整份工作簿。
- `evidence/delivery_manifest.json` 的 125 个登记文件均存在，SHA-256 全部相符。

1800 s、半径 0/0.5/1/1.5/2 cm 的当前结果为：

| 量 | 0 cm | 0.5 cm | 1 cm | 1.5 cm | 2 cm |
|---|---:|---:|---:|---:|---:|
| 温度/℃ | 33.5753 | 33.7720 | 34.3642 | 35.3621 | 36.7856 |
| 干基含水率/(kg/kg) | 2.5500 | 2.5497 | 2.5383 | 2.3755 | 1.5102 |

## 复现链的小缺口

以下不构成现有数值答案错误，但影响以后更换输入或运行环境后的自动验收：

1. `run_all.py:25–30` 的完整入口没有纳入后补的 `q1_rounding_audit.py`。README 第 81 行说明需额外运行；因此一条完整入口命令不会自动生成后补的最终十进制参考审计记录。
2. `run_all.py:40–47` 将 `all_steps_successful` 设为真，并仅记录与交付解的差异；如果四位小数比较失败，入口仍可正常返回。它证明子程序成功结束，不等于自动判定复现一致。审查时仍应读取 `compared_with_delivered`。
3. `source/paper_template.md:254,264,278,284` 的四位小数变化个数/通过表述是固定文字；`source/q1_report.py:87–103` 只替换误差数值等 token，不根据这些比较计数重新生成通过/失败文案。当前交付数据已由本审计证实匹配，但以后换输入或版本后不能只信生成正文中的“一致”。

包内 `output/reproduction_audit.json`、`run.json` 记录 `/mnt/data/q1_delivery` 路径及 Python 3.13.5 / SciPy 1.17.0，是历史交付运行证据。README 第 23 行也明确历史 OOXML fallback 未实测。这些限制不应与当前 Windows 环境的新运行结果混淆。

## 本次执行证据

使用桌面 bundled Python 3.12.14、NumPy 2.3.5，独立 XML/ZIP 读取，不导入交付代码、不写出修改后的工作簿。

```powershell
& 'C:\Users\libai\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'D:\Desktop\CUMCM26\review_q1_20260910\artifact_audit\audit_artifacts.py'
```

最终退出码 0。机器可读记录为 `artifact_audit.json`。最初两次运行分别修正审计程序自身对可选 OOXML dimension 的假设及 Windows 控制台编码；最终全量检查重新执行通过，交付原件未修改。
