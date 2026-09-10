# 第一问独立审核入口

审核日期：2026-09-10。本目录保存对现有第一问交付的独立审查、新目录复现及参考解证据。原求解代码和原交付结果位于 [q1_delivery](../q1_complete_delivery/q1_delivery/)，本目录没有替换正式答案。

## 建议阅读顺序

1. [第一问完成情况与答案审核报告](第一问审核报告.md)：范围、结论、模型适用条件与待改进项。
2. [原题](../A题/A题.pdf)及[可读文本](../readable/problem/fulltext.md)：先确认第一问与附录2的要求。
3. [现有模型正文](../q1_complete_delivery/q1_delivery/output/第一问论文正文.md)与[主求解器](../q1_complete_delivery/q1_delivery/source/q1_solver.py)。
4. 按下表核验实际运行记录；不要仅依据正文中的通过表述。

| 证据 | 内容 |
|---|---|
| [本机完整复现记录](reproduced/reproduction_audit.json) | 五个阶段均退出0，输入哈希保持不变，重跑解与原交付四位小数一致 |
| [额外四位小数审计](reproduced/rounding_reference_audit.json) | 两场各37800个结果与本轮参考解一致 |
| [数值验证](reproduced/validation/validation.json) | 网格、时间、守恒、配点及情景敏感性 |
| [独立热解说明](independent_heat/README.md) | 新编Bessel解析推进，不导入交付求解函数 |
| [独立热解记录](independent_heat/heat_audit.json) | 200/800/3200模态对照及Excel比较 |
| [交付文件审查](artifact_audit/artifact_review.md) | 原附件、模板、75600个Excel值、70个论文表值与清单哈希 |
| [交付文件机器记录](artifact_audit/artifact_audit.json) | 独立ZIP/XML读取的核验结果 |
| [场性质检查](field_properties.json) | 初值、单调性、细网格快照及表面Robin残差 |
| [原PDF第1页核验图](pdf_check/problem-1.png)、[第3页核验图](pdf_check/appendix-3.png) | 第一问要求及附录2公式的直接图像证据 |

`reproduced/` 是本次复跑副本，包含全部输出、日志、图和参考数组。审计记录中的本机绝对路径是历史运行来源信息；审查者可按同名仓库相对路径定位文件。

## 结论范围

已获得的证据支持“中截面径向、等效Robin交换、无显式潜热”模型内的数值结果。气固水分变量的对应关系、蒸发潜热、固定几何及其他边界物理仍应独立讨论。本目录不是官方标准答案，也不包含真实药材内部响应的实验验证。

原交付记录中“原PDF未核验”和“OOXML回退未实测”等说明描述的是原交付时状态；本轮已补充对应核验事实，详见审核报告。不要把单纯上传或文本提取视为模型验证。

## 复现环境

已记录的本轮数值环境：Python 3.13.14、NumPy 2.3.5、SciPy 1.17.0、Matplotlib 3.11.0。虚拟环境及缓存不上传GitHub，需要在自己的环境重新安装依赖：

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r q1_complete_delivery/q1_delivery/requirements.txt
```

从仓库根目录运行；完整复现建议使用一个新的输出目录：

```bash
python -X utf8 q1_complete_delivery/q1_delivery/run_all.py --out reproduced_local
python -X utf8 q1_complete_delivery/q1_delivery/source/q1_rounding_audit.py --out reproduced_local
python -X utf8 review_q1_20260910/independent_heat/independent_heat.py
python -X utf8 review_q1_20260910/artifact_audit/audit_artifacts.py
python -X utf8 review_q1_20260910/check_field_properties.py
```

独立热解、文件审计及场性质检查命令会刷新对应审计文件；如需保持发布证据原样，请在仓库副本中运行。完整入口的正式模型限制及各阶段运行方式见[原交付说明](../q1_complete_delivery/q1_delivery/README.md)。
