"""Generate answer/entry documents from saved, unrounded computation evidence."""
import argparse,json
from pathlib import Path
from q4_common import ROOT

def build(base=ROOT):
    base=Path(base);read=lambda p:json.loads((base/p).read_text())
    e=read('output/end_event.json');m=read('output/main.json');n=read('validation/numeric_comparison.json')
    fixed=read('validation/fixed80.json')['event']['critical_h'];pchip=read('validation/pchip80.json')['event']['critical_s']
    g=read('validation/geometry/geometry_comparison.json');q2=read('q123_closeout/validation/q2_closeout_summary.json')
    q4g=g['q4_80x128_integral']['summary'];q1g=g['q1_80x128']['summary']
    q23key='q23_80x256_integral' if 'q23_80x256_integral' in g else 'q23_80x128_integral'
    q23g=g[q23key]['summary'];q2g=g[q23key]['intervals']['q2_table_range']['max_mid_difference_T_C']
    table=(base/'output/表6.md').read_text();pct=100*(1-e['critical_h']/fixed)
    convergence='|实际计算|临界时间/s|与120阶主解之差/s|\n|---|---:|---:|\n'
    convergence+=f"|120阶Radau主解|{e['critical_s']:.9f}|0|\n"
    for name in ['spectral80','spectral160','time120_bdf']:
        p=base/'validation'/(name+'.json')
        if p.exists():
            d=json.loads(p.read_text());t=d['event']['critical_s'];convergence+=f'|{name}|{t:.9f}|{t-e["critical_s"]:.9f}|\n'
    convergence+=f"|独立FV 320/640加密后二阶外推|{e['fv_extrapolated_root_s']:.9f}|{e['fv_extrapolated_root_s']-e['critical_s']:.9f}|\n"
    answer=f'''# 第四问分析与答案

在附录4有效物性、附件2分段线性半径、径向均匀材料收缩及长度固定为25cm的主模型下，本轮采用严格执行时间 **{e['execution_h']:.4f} h = {e['execution_s']:.2f} s**。原题及输入实际读取的仓库提交为 `dbb8845a783fda4eaf754ff4c906d1922cab8020`，未覆盖历史解。

## 1. 临界根与严格执行

一维径向等号根为{e['critical_s']:.9f}s，即{e['critical_h']:.12f}h，显示为{e['critical_display_h']:.4f}h。对完整径向插值多项式的驻点和端点检查表明，事件附近最大含水率在轴心；新二维原始完整状态的最湿点也在中截面轴心。

正式执行点的未舍入最大含水率为 **{e['execution_max_C']:.17g}<0.15**，半径为{e['radius_m']*100:.4f}cm。根前1s最大C为{e['one_second_before_max_C']:.16g}，根后1s为{e['one_second_after_max_C']:.16g}，因此不能用四位显示的0.1500替代严格事件判断。

执行点晚于谱根{e['actual_margin_s']:.9f}s。由本轮谱阶数变化、时间算法变化及独立有限体积加密差得到经验数值预算{e['empirical_budget_s']:.3f}s，再向上取到0.0001h的显示单位；该预算不是严格数学误差界，也不包括药材物理参数的不确定性。

## 2. 表6与完整结果

{table}

`output/result4.xlsx`保留原Sheet1及时间列，每60s和实际执行点一行，共3066行。0至2cm每0.1cm为固定实际位置，另列当前药材表面和真实R(t)。域外格为空白；表面恰与固定点重合时，两格保存相同的四位数值，不删除模板中的表面列。

`output/main.npz`保存0时刻、全部60s输出、实际半径、x=(r/R)²节点完整T/C场、固定实际径向输出、表面值、全径向最大值及位置、平均C和事件附近完整状态。`trajectory_60s_unrounded.csv`提供17位有效数字的开放文本版本，`table6_unrounded.csv`保存表6来源。

## 3. 采用的模型及文献方法

材料速度采用v_s=rR′/R，网格速度由映射r=Rξ给出；两者相等是明确的材料收缩假设。干质量守恒使ρ_d∝R⁻²，干基C满足材料导数扩散方程，参考域不再机械增加浓缩项或重复对流项。附录ρ(C)仅进入有效热容量ρc_p，不强行解释为守恒湿体密度。

Adrover第4–7、18页支撑移动输运、ALE与变量基准转换；da Silva第3–5页支撑圆柱有限体积、第三类边界和固定干质量更新；吴孟秋第3–7页提供动网格组织及轴径向收缩差异依据。均实际核对核心原页，未抄其食材物性、收缩系数或潜热参数。

Chupawa第3–5页仅辅助局部变物性耦合说明，已读项目完整提取文本，其LFS大PDF未完成本轮原页视觉核验。每篇采用/排除方法、页码、式号、单位和代码映射详见《第四问模型与文献采用》及`validation/literature_review.md`，没有把论文名称列表代替原文阅读。

## 4. 收缩效应与插值敏感性

保持附录4及其他输入相同，固定2cm半径的临界时间为{fixed:.9f}h；采用观测收缩后为{e['critical_h']:.9f}h，减少{fixed-e['critical_h']:.6f}h，即{pct:.4f}%。此对照才隔离了收缩作用。与第三问的差还包含附录3到附录4的物性变化，不能全归因于收缩。

将R(t)改为同样不超调的PCHIP插值，临界根改变{pchip-e['critical_s']:.6f}s。主结果明确采用分段线性插值，不从两种插值中挑更短者。主终点为51.09h，位于半径观测0–72h范围内，没有使用半径延拓；4h以后的环境平台仍属于声明的未来环境假设。

## 5. 数值与几何证据

{convergence}

80阶与主解共同3067时刻的实际固定位置T/C输出四位差异为0；同阶加严时间并改BDF后的四位差异也为0。独立FV采用不同圆环离散，在相同材料坐标比较，最大温度差{n['independent_fv']['max_abs_T']:.4e}℃、最大C差{n['independent_fv']['max_abs_C']:.4e}；其结果不能机械充当逐格四位完全一致的声明。

累计水量账本最大残差为{m['mass_balance_max_abs_in_mean_C']:.4e}kg/kg干物质，末平均C为{n['main_end_mean_C']:.16f}。独立72h纯几何收缩算例中，T与干基C不变，干/水质量相对变化不超过4.44×10⁻¹⁶。有效热账本单独检查瞬时容量率，未声称验证真实相变总能量。

Q4的80×128二维原网格根为{q4g['event_2d_s']:.9f}s，配对一维根为{q4g['event_1d_s']:.9f}s，差为{q4g['end_effect_s']:.9f}s。这个配对差分离几何影响，不能把带径向离散偏差的二维原根直接同精密谱根相减，也不能称粗二维已在正式执行点直接测得达标。

空间和时间配对加密给出的几何提前量约0.0286–0.0343s。以精密谱根加该配对差，当前全域临界根估计约183931.1775–183931.1831s；在正式点的全域最大C估计约0.149999804–0.149999807。这是同模型径向校正及根附近线性估计，非原粗网格直接输出或严格误差界。

Q4全程中截面配对最大温度差为{q4g['max_mid_T_difference_all_samples_K']:.4e}℃、C差为{q4g['max_mid_C_difference_all_samples']:.4e}；端面差却可达{q4g['max_end_T_difference_all_samples_K']:.4f}℃和{q4g['max_end_C_difference_all_samples']:.4f}kg/kg。证据支持一维用于中截面与保守终点，不支持用一维描述全部端部场或整根平均量。

## 6. 前三问收尾结论

新完整`q123_closeout/result2.xlsx`由同一附录3联合冷启动轨迹生成，逐秒至206906.76s，每表206907行，共8690094个温湿数值。新旧前3h的453600个正式值、论文60值均四位一致；旧第三问共同60s输出及端点也一致，因此历史表格不改写。

Q1中截面温度/C配对差为{q1g['max_mid_T_difference_all_samples_K']:.3e}℃、{q1g['max_mid_C_difference_all_samples']:.3e}；Q2前三小时分别为{q2g[0]:.3e}℃、{q2g[1]:.3e}。Q2几何误差可能改变四位显示，不能把已收敛的一维四位值解释成二维同样四位精确。

第三问当前完成的{q23g['nr']}×{q23g['nz']}配对二维终点较同网格一维提前{abs(q23g['end_effect_s']):.6f}s，全域最湿点仍在中截面轴心。保留原有效模型执行57.4741h作为有余量的时长；几何估计与原网格状态、未完成附加试验均在`q123_closeout/一维二维适用范围.md`逐项区分。

## 7. 边界与交付状态

本结果是题给有效物性、等效空气水分边界、无显式潜热及已声明几何/未来环境假设下的条件数值答案。它没有识别真实药材平衡含水率、水活度、气膜参数或组分总焓。官方公式未被称为已包含潜热；潜热继续作为扩展和局限，未用R_L或F覆盖本轮主线。

GitHub读取和来源核查成功，但写入探测被应用以403拒绝，另一本地git推送缺少登录凭据。本交付保留本地文件与提交及完整下载包，不称已同步远端。检查证据见`validation/github_sync_probe.json`；此访问问题不影响本轮已完成的数值计算。
'''
    (base/'第四问分析与答案.md').write_text(answer)
    readme=f'''# 第四问完整交付 v1

**第四问执行时间：{e['execution_h']:.4f}h = {e['execution_s']:.2f}s。** 从题给初态重新求解，采用附件2线性半径、长度固定25cm、均匀径向材料收缩、附录4局部有效物性及无显式潜热主线。临界等号根为{e['critical_s']:.9f}s，正式执行点一维最大C为{e['execution_max_C']:.17g}。

同模型二维的配对网格证据支持该一维时间作为保守执行值。几何提前量约0.03s，属于分离径向离散偏差后的估计；原粗二维网格的绝对根并不等于精密谱根。中截面适用、端部与全域估计的区别见分析报告，未把不同物理模型的旧二维差当作误差界。

## 交付入口

|文件|内容|
|---|---|
|[第四问分析与答案](第四问分析与答案.md)|时长、表6、机制、数值/几何证据和收尾结论|
|[第四问模型与文献采用](第四问模型与文献采用.md)|材料/ALE推导、质量基准、具体论文页码及代码对应|
|[第四问论文正文](第四问论文正文.md)|可供团队审核后合稿的正文|
|[result4.xlsx](output/result4.xlsx)|完整60s及结束点工作簿，3066行|
|[表6](output/表6.md)|每6h及执行点，域外符号及舍入说明|
|[未舍入主轨迹](output/main.npz)|完整参考节点T/C、实际半径、极值、事件前后状态|
|[开放CSV轨迹](output/trajectory_60s_unrounded.csv)|17位数字，实际固定径向输出，域外为空|
|[前三问收尾](q123_closeout/README.md)|完整result2及同模型一维/二维适用范围|
|[数值比较](validation/numeric_comparison.json)|真实空间、时间、独立实现与域外检查|
|[几何证据](validation/geometry/README.md)|原始二维场、配对差及全域校正估计|

## 可复现运行

数值运行实际环境为Python {m['python']}、NumPy {m['numpy']}、SciPy {m['scipy']}。安装依赖后，在本目录选择全新的输出目录运行。输入原件、核心论文阅读记录及必要历史比较基线均在包中，不依赖整个旧仓库，也不从第三问结束状态接续。

```bash
python -m pip install -r source/requirements.txt
python run_all.py --out ../recomputed_q4
# 额外复跑本轮针对性二维及完整Q2；耗时、内存更高
python run_all.py --out ../recomputed_full --geometry --closeout
```

默认入口实际重算Q4主解、必要数值比较、固定半径/PCHIP情景，导出事件、表6、未舍入CSV和图。`--geometry`补针对性二维，`--closeout`补完整逐秒Q2，`--excel`调用下述工作簿依赖；不会自动改动本交付中的冻结文件或手工修正单格。

工作簿使用`@oai/artifact-tool`的Codex主运行时构建，普通Python数值依赖不包含该组件。具体单独导出命令、离线模板、舍入规则、大表分块封装及全量读回记录见`validation/workbook_method.md`。当前工作簿已实际生成核验，复现包装入口本身不计作额外独立PDE验证。

所有主轨迹与报告指标来自实际保存的数组。120阶主解用独立边界通量积分核对累计水量，最大归一化残差{m['mass_balance_max_abs_in_mean_C']:.3e}。图在`figures/`中同时保存PNG与SVG；纯收缩、原页核查、源版本及运行中断证据均在`validation/`。

## 来源与状态

实际源提交为`dbb8845a783fda4eaf754ff4c906d1922cab8020`。另从该提交取得q4_inputs.zip并核对203个清单文件，字节和SHA256全部相符；包内的交接前base_commit另行保留，未冒充本轮读取的HEAD。模型假设详见`configs/model_contract.json`。

前三问原交付、历史审核、F/R_L及原论文保留字节完整。新完整Q2延长时域但不改变旧3h规定表，第三问保留57.4741h；几何证据属于同一无显式潜热模型。附加未完成的160阶逐秒试算和Q23 160×128检查均保留中断记录，未计为通过。

本地成果和提交可交付；GitHub应用写入探测返回403，未更新远端。`validation/github_sync_probe.json`记录实际错误，交付包不会把本地完成称为远端同步。质量账本通过是所选模型的数值证据，不等于真实药材相变和实验预测已完成验证。
'''
    (base/'README.md').write_text(readme)
    (base/'q123_closeout/README.md').write_text(f'''# 前三问两项收尾

完整第二问已统一至第三问选择的执行端点206906.76s。`result2.xlsx`两张表均从1s逐秒输出，末行另列206906.76s，每表206907行、合计8690094个温湿数值；对应未舍入联合轨迹为`output/q23_unified.npz`，包含t=0。

新解从28℃、C=2.55的共同初态采用附录3联立求解，未拼接不同模型的T、C。末小时61点均值环境平台与历史Q3相同，选定端点最大C为{q2['strict_end_max_C']:.17g}。旧Q2全部453600个正式值和论文60值四位一致，历史Q3共同输出也一致。

一维/二维收尾已使用题给有效物性、相同环境和边界、无显式潜热的同一模型。当前{q23g['nr']}×{q23g['nz']}配对证据表明第三问端部使根提前约{abs(q23g['end_effect_s']):.4f}s；保留57.4741h为有余量的执行值。中截面误差、端部差及网格误差严格区分。

|入口|说明|
|---|---|
|[完整result2](result2.xlsx)|正式逐秒两场工作簿|
|[全时域说明](第二问全时域收尾.md)|同源轨迹、旧表逐格比较、冷启动及未完成附加试算|
|[一维二维适用范围](一维二维适用范围.md)|Q1/Q2中截面及Q3全域终点的针对性证据|
|[机器摘要](validation/q2_closeout_summary.json)|实际数组维度、时间、阈值和历史比较|
|[完整旧新比较](validation/unified_audit/audit.json)|回读与未舍入差异|

数值源码和必要冻结比较基线可单独复算，不要求取得旧仓库全部历史场。Excel最终全量读回另见上一级`validation/workbook_result2.json`；纯读取旧材料、实际新运行和未完成试算分别记录，没有把旧F或R_L二维差当作本轮几何误差界。
''')
    print('Generated README, answer, and Q123 closeout README from real files')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,default=ROOT);a=p.parse_args();build(a.base)
