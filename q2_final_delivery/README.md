# 第二问完整数值交付

## 先看结果

正式文件为`output/result2.xlsx`：温度和水分浓度两张工作表，各10800×21个结果，时间1—10800 s、径向0—2 cm。`output/第二问论文正文.md`包含两张6×5表、推导、10幅图、实际验证及局限。第一问文件没有改写。

3 h中心/表面温度为49.8495/49.9664 ℃，中心/表面干基含水率为1.7662/1.0081 kg/kg。正式数值从0 s使用附录3联立计算，不采用第一问末态，也不把上传预计算作为标准答案或校准目标。

## 模型口径和时间域

本轮选择`S(C) T_t=div(k(C)grad T)`和`C_t=div(D(T+273.15,C)grad C)`，其中`S=ρcp`。热方程不改写成未经组成焓闭合的`∂t(ST)`，面上平均k而非alpha；全部节点每次非线性评估更新当地物性，保留局部双向耦合。

固定几何、轴向中截面、等效Robin水分边界，不显式引入潜热、辐射或收缩。经验ρcp用作有效容量，不同时把经验ρ当作精确满足静止固定体积质量关系的实际湿密度。该模型只提供声明假设下的条件性数值预测，非内部实验验证结果。

原题第二问的Excel没有明文终点，本轮采用“规定的前3h完整逐秒采样”工作解释。`result2.xlsx`不是数天全过程或第三问达标结果。核心积分器支持更长时域，但默认禁止超过实测14400s；只有显式声明`hold_last`才允许环境末值延续。

## 安装和运行

建议Python 3.11以上。本轮实际环境为Python3.13.5、NumPy2.3.5、SciPy1.17.0、Matplotlib3.10.8。requirements固定了核心数值依赖；不是对完全隔离的全新操作系统或所有版本作兼容性保证。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

本轮实际完整入口使用环境提供的artifact_tool 2.8.22生成Excel。该包不随交付分发，也没有将内部安装目录或字体打包。具备该API的环境可运行与本轮相同的路径：

```bash
python run_all.py --out reproduced --excel-engine artifact
```

普通本地环境无artifact_tool时，提供标准库OOXML备用导出接口，不需要Microsoft Excel桌面软件：

```bash
python run_all.py --out reproduced_local --excel-engine portable
```

**备用portable导出分支未在本轮运行测试**，不把它冒称已验证；实际交付与完整重跑使用artifact分支。两个分支共享同一套已执行的数值求解、验证、图文生成及独立Excel审计。portable源码完整给出，运行后须检查audit阶段。

入口只写指定新输出目录，拒绝覆盖inputs和Q1目录。已有运行状态时必须显式`--resume`，并核对原始输入哈希。长流程可在受限执行窗口中按相同阶段执行，完成标志只在所有阶段通过后置为true。

```bash
python run_all.py --out reproduced --stage mesh
python run_all.py --out reproduced --stage reference --resume
# 其他阶段：tests, time, sensitivity, geometry, assemble, excel, report, audit
# 也可继续全部未完成阶段：
python run_all.py --out reproduced --resume
```

`run_state.json`保存每阶段是否通过、耗时、输入哈希和对交付值的比较。检查原输入不变；任何求解失败、负含水率、非有限值、舍入验收差异都会报错。没有从聊天上下文读取隐藏变量。

## 交付文件映射

| 文件 | 内容 |
|---|---|
| inputs/题目原件.pdf、附件1.xlsx、result2_template.xlsx | 上传包原始字节；哈希与远端Git对象相符 |
| analysis_decisions.md | 上传候选模型逐项接受、修正或拒绝及依据 |
| source/q2_core.py | 原始读表、局部物性、完整耦合Jacobian、FV/BDF、独立热收支求积 |
| source/q2_spectral.py | 独立Chebyshev空间离散、耦合Robin消元及参考求解 |
| source/q2_axisymmetric.py、q2_geometry_tests.py | 新增二维非线性热质情景、几何算子检验 |
| source/q2_tests.py | 单位、常系数解析、无驱动、封闭、故障和敏感性检验 |
| source/q2_finalize.py | 原始数值结果、Richardson外推、CSV和验证摘要 |
| source/q2_excel.py、q2_audit.py | artifact生成正式Excel；独立OOXML全格审计 |
| source/q2_xlsx_portable.py | 未实测的公共依赖备用导出分支 |
| source/q2_report.py | 从结果和验证记录生成图与论文 |
| output/q2_unrounded.npz | 包含t=0，两场10801×21、环境及rdr加权平均 |
| output/temperature_degC_unrounded.csv、moisture_dry_basis_unrounded.csv | 17位有效数字CSV，可用普通文本软件读取 |
| output/table_temperature.csv、table_moisture.csv | 题目表3与表4，时间h、位置cm、四位小数 |
| output/第二问论文正文.md | 对应请求中的“第二问模型与答案”正文源文件 |
| output/validation/validation.json | 所有真实检验指标、误差位置与四位比较计数 |
| output/excel_audit.json | 453600个Excel状态、60个论文值、端点、格式和舍入审计 |
| output/reproduction_audit.json | 实际完整入口新目录重跑记录，只有complete=true才代表全通过 |
| output/figures/ | 10幅300dpi PNG与对应SVG |
| evidence/source_access.md、source_access.json | 实际GitHub版本、路径、阅读范围、上传副本及原件哈希 |
| evidence/execution_limits.md | 中断、失败修正、未执行和物理验证边界 |

## 数组读取

```python
import numpy as np
z = np.load('output/q2_unrounded.npz', allow_pickle=False)
print(z.files)
print(z['time_s'][10800], z['radius_cm'])
print(z['temperature_degC'][10800, [0, 20]])
print(z['moisture_dry_basis'][10800, [0, 20]])
```

温度℃，含水率kg水/kg干物质，半径cm，时间s。`environment`的两列分别为环境℃和等效水分输入。mean数组使用圆柱rdr体积权重，不是均匀半径采样的算术平均；未舍入值不提前截断到四位。

## 验证范围

主FV20—2560、独立谱128/192、固定N1280时间精度、均匀/无通量/常系数/温标/故障和二维40×80情景均已执行。正式结果采用`(4*u2560-u1280)/3`，与独立192阶参考全部453600个四位结果一致。守恒审计针对组成外推的原FV轨迹，不把外推称为新的严格守恒积分器。

二维同时计算热与非线性水分，不是只算线性导热。中截面几何情景差约0.0017K、2.25e-5kg/kg，足以支持工程近似，但不保证忽略端部后第四位均不变。传递系数与插值敏感性不是实验置信区间，潜热/真实界面闭合仍未识别。

## 原件和历史资料

远端main实际读到`1942d7506632e94853b32772c7c9bb4ba3a3c0be`，没有发现更新。二进制下载失败后使用上传原件并按Git blob哈希交叉确认；原题PDF图像已实际查看。Adrover仅核对第6页页面图像与正文，未把该页证据说成完整PDF已读。

上传预计算及历史Q1材料未作为正式求解目标。所有队伍人工复核均待实际完成后据实登记；不能把本轮AI独立实现和核验写成已完成的参赛队人工审阅。

## 压缩包的分工

`q2_complete_delivery.zip`包含原始输入、完整代码、正式Excel、未舍入最终场、CSV、论文、图表、全部JSON验证记录及日志。为避免重复的大型中间数组，逐网格/谱参考/二维情景NPZ另存于`q2_validation_arrays.zip`；两包目录结构相同，可解压到同一位置合并。

不下载额外数组也能用完整入口从原附件重新生成全部结果。若只单独运行绘图或读取某个既有参考数组，应先合并验证数组包，或先完成入口的相应计算阶段。主交付包不是隐藏中间数据；记录清单明确区分随附数组与可再生成数组。
