# 问题二流程图与扩散率机制图

本目录为 2026-09-13 问题二修订新增图件。旧图、数值数组与历史证据不覆盖。

- `q2_workflow.pdf/svg/png`：由统一模型代入问题二条件与附录3物性，经过固定半径径向温湿耦合、Robin 交换边界、Chebyshev 配点和 Radau 联立积分，输出前 3 h 规定结果及供问题三使用的全程轨迹。框内为白色，流程从共同初态开始。
- `q2_mechanism.pdf/svg/png`：从已保存的 `q4_complete_delivery/v1/q123_closeout/output/q23_unified.npz` 提取前 3 h 共 10801 个逐秒样本，分别绘制轴心与表面的温度项 `H`、含水率项 `M` 和合计 `H+M=ln(D/D0)`。坐标与曲线直接采用保存数组的代数后处理，不插值、不平滑、不重新求解。

中文使用宋体，英文及数字使用 Times New Roman；PDF 保留矢量文字和曲线，PNG 为 600 dpi。流程图尺寸为 15.0 × 3.2 cm，机制图为 15.0 × 5.5 cm。机制图的 2.46 h / 2.02 h 标记是前 3 h 逐秒样本中的峰值位置，不构成连续时间极值的严格证明；曲线分解也不是独立因果贡献百分比。

构建命令（从论文目录执行）：

```powershell
python -X utf8 build_q2_revision_assets.py
```

数据 SHA256、公式、样本与图形数组签名、峰值核对、文本边界和 PDF 字体检查见 `../../evidence/q2_revision_20260913/figure_provenance.json`。该脚本只生成本目录图件及本轮来源记录，不运行 PDE、积分或参数情景。
