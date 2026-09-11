"""Audit this review's fresh Q2 run without changing the Pro delivery."""
from pathlib import Path
import hashlib
import json
import platform
import re
import sys

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DELIVERY = PROJECT / 'q2_final_delivery'
FRESH = HERE / 'reproduced'
FIELDS = ('temperature_degC', 'moisture_dry_basis')
STAGES = ('mesh', 'reference', 'tests', 'time', 'sensitivity', 'geometry',
          'assemble', 'excel', 'report', 'audit')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(a, b):
    delta = np.abs(a - b)
    at = np.unravel_index(delta.argmax(), delta.shape)
    formatted_a = np.fromiter((format(float(x), '.4f') for x in a.ravel()),
                             dtype='U16', count=a.size)
    formatted_b = np.fromiter((format(float(x), '.4f') for x in b.ravel()),
                             dtype='U16', count=b.size)
    return {'max_abs': float(delta[at]), 'rms': float(np.sqrt(np.mean(delta**2))),
            'index': list(map(int, at)),
            'four_decimal_mismatches': int(np.count_nonzero(formatted_a != formatted_b))}


def main():
    original_hashes = read_json(HERE / 'original_delivery_hashes.json')
    changed = [name for name, digest in original_hashes.items()
               if not (DELIVERY / name).is_file() or sha256(DELIVERY / name) != digest]
    assert not changed, changed
    state = read_json(FRESH / 'run_state.json')
    exit_code = int((HERE / 'reproduction_exit_code.txt').read_text(encoding='utf-8-sig').strip())
    assert exit_code == 0 and state['complete']
    assert all(state['stages'][s]['passed'] for s in STAGES)
    excel = read_json(FRESH / 'excel_audit.json')
    assert excel['all_passed'] and excel['total_result_values'] == 453600
    assert excel['paper_tables_checked'] and excel['paper_values_checked'] == 60
    validation = read_json(FRESH / 'validation/validation.json')
    formal = np.load(DELIVERY / 'output/q2_unrounded.npz', allow_pickle=False)
    rerun = np.load(FRESH / 'q2_unrounded.npz', allow_pickle=False)
    assert np.array_equal(rerun['time_s'], np.arange(10801))
    assert np.allclose(rerun['radius_cm'], np.arange(21) / 10, rtol=0, atol=1e-14)
    comparisons, table_comparisons = {}, {}
    rows = np.arange(1800, 10801, 1800)
    cols = np.arange(0, 21, 5)
    for key in FIELDS:
        assert np.isfinite(rerun[key]).all() and rerun[key].shape == (10801, 21)
        comparisons[key] = compare(rerun[key][1:], formal[key][1:])
        table_comparisons[key] = compare(rerun[key][np.ix_(rows, cols)],
                                         formal[key][np.ix_(rows, cols)])
        assert comparisons[key]['four_decimal_mismatches'] == 0
        assert table_comparisons[key]['four_decimal_mismatches'] == 0
        assert validation['precision'][key]['final_vs_independent']['four_decimal_mismatches'] == 0
    input_checks = {}
    for copy_name, original in [('题目原件.pdf', 'A题/A题.pdf'),
                                ('附件1.xlsx', 'A题/附件/附件1.xlsx'),
                                ('result2_template.xlsx', 'A题/附件/附件3/result2.xlsx')]:
        h = sha256(DELIVERY / 'inputs' / copy_name)
        same = h == sha256(PROJECT / original)
        assert same
        input_checks[copy_name] = {'sha256': h, 'matches_original': same}
    log = (HERE / 'reproduction.log').read_text(encoding='utf-8-sig')
    warnings = [line for line in log.splitlines() if re.search(r'Warning:', line)]
    result = {
        'scope': 'Fresh local ten-stage reproduction of the declared effective radial Q2 model, '
                 '0..10800 s; not experimental validation or a days-long drying result.',
        'command': [sys.executable, '-X', 'utf8', '-B', str(DELIVERY / 'run_all.py'),
                    '--out', str(FRESH), '--excel-engine', 'portable'],
        'runtime': {'python': sys.version, 'platform': platform.platform(),
                    'numpy': np.__version__, 'scipy': scipy.__version__},
        'exit_code': exit_code, 'complete': True, 'stages': state['stages'],
        'sum_stage_elapsed_s': sum(state['stages'][s]['elapsed_s'] for s in STAGES),
        'original_delivery_files_checked': len(original_hashes),
        'original_delivery_files_changed': changed, 'original_inputs': input_checks,
        'full_field_comparison_with_delivery': comparisons,
        'paper_60_values_comparison_with_delivery': table_comparisons,
        'fresh_excel_audit': excel, 'fresh_independent_reference_comparison': validation['precision'],
        'fresh_balance': validation['balance'],
        'fresh_unit_tests_passed': validation['unit_tests']['passed'],
        'fresh_geometry_unit_tests_passed': validation['geometry_unit_tests']['passed'],
        'surface_at_1s': {key: float(rerun[key][1, -1]) for key in FIELDS},
        'values_at_3h': validation['values_3h'],
        'runtime_warning_lines': warnings,
        'warning_note': 'Warnings are retained; see the separate model-audit diagnosis. '
                        'Passing result checks is not a claim of a warning-free run.',
        'all_reproduction_checks_passed': True,
    }
    (HERE / 'acceptance_checks.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    independent = read_json(HERE / 'independent_numeric/independent_audit.json')
    assert independent['all_453600_independent_four_decimal_results_equal']
    assert independent['all_60_paper_values_equal_independent_rounding']
    assert read_json(HERE / 'model_audit/operator_spotcheck.json')['passed']
    assert read_json(HERE / 'model_audit/bdf_workspace_probe.json')['passed']
    end = result['values_at_3h']
    dt = comparisons['temperature_degC']['max_abs']
    dc = comparisons['moisture_dry_basis']['max_abs']
    ind = independent['new_reference_vs_original_delivery']
    report = f'''# 第二问 Pro 交付验收报告

审核日期：2026-09-11。对象：`q2_final_delivery/`。本轮原文件哈希快照、全部新运行、独立代码及检查记录保存在本目录。

## 结论

**核查通过：按已经明确的“附录3有效物性、固定几何中截面、前3h完整采样”口径，第二问数值部分可以收口。没有发现需要推翻模型内数值结果、修改正式Excel或重做两张论文表的错误。**

这不是仅根据Pro的README或旧验证JSON作出的判断。本轮分别完成了模型与代码审核、39项交付物独立审计、新目录十阶段完整重跑，以及另一套直接径向离散与Radau方法的独立求解。

结论限于所声明的有效模型。逐秒Excel取前3h是明确披露的工作解释，不能改写为已经算完数天全过程；四位数值稳定也不等于真实药材的物理预测误差达到四位。

## 关键结果

| 3h状态 | 轴心 | 表面 |
|---|---:|---:|
| 温度 / ℃ | {end['T_center']:.4f} | {end['T_surface']:.4f} |
| 干基含水率 / kg水·kg干物质⁻¹ | {end['C_center']:.4f} | {end['C_surface']:.4f} |

按圆柱r dr加权的中截面平均温度为 **{end['mean_T']:.4f} ℃**，平均含水率为 **{end['mean_C']:.4f} kg/kg**。固定参考干密度意义下的有效水分减少比例为 **{end['effective_water_reduction_percent']:.4f}%**，不把它称为真实变密度样品的实测失重率。

正式结果位于 [result2.xlsx](../q2_final_delivery/output/result2.xlsx)，两张论文表见 [第二问论文正文](../q2_final_delivery/output/第二问论文正文.md)。

## 本轮实际验证

| 核查内容 | 结果 |
|---|---|
| 模型—代码一致 | 局部双向耦合、S(C)Tt储存项、面上k而非alpha、D中的开尔文、轴心系数及Robin方向均一致 |
| 原始输入 | 三份原件哈希与项目原件一致；241条环境记录、前3h181条、线性插值及输出单位正确 |
| 原交付文件 | 两表共453600个状态逐格匹配未舍入NPZ的四位格式；两份完整CSV精确匹配NPZ；论文60值及时间列正确 |
| 全新目录重跑 | mesh、reference、tests、time、sensitivity、geometry、assemble、excel、report、audit十阶段全部通过，退出码0；阶段耗时合计{result['sum_stage_elapsed_s']:.2f}s |
| 本机复现与原交付 | 温度最大差{dt:.4e} K，含水率最大差{dc:.4e} kg/kg；453600个四位值全部一致 |
| 另一数值实现 | 新写直接r坐标谱离散、展开形式PDE、Radau及独立读表；不导入Pro、Q1或预计算RHS，完整3h另算；453600个四位值全部一致 |
| 独立实现差异 | 全场最大温差{ind['temperature_degC']['max_abs_difference']:.4e} K、含水率差{ind['moisture_dry_basis']['max_abs_difference']:.4e} kg/kg；原始60个论文位置值另核对 |
| 精度记录 | 用新生成的FV、谱和时间收紧数组，重新计算Richardson、谱128/192及固定N1280时间误差，支持原交付声明 |
| 本地Excel导出 | 本轮实际执行此前未实测的portable分支并通过全格回读，无需artifact_tool；没有进行Microsoft Excel桌面原生打开测试 |
| 原文件保护 | 初始登记的{len(original_hashes)}个Pro交付文件哈希全部保持不变；所有重跑输出写入新审核目录 |

本机实际数值环境为Python {platform.python_version()}、NumPy {np.__version__}、SciPy {scipy.__version__}；绘图使用现有Matplotlib 3.11.0，与Pro的3.10.8不同。本轮运行未依赖Pro的私有artifact_tool，数值和导出验收均实际通过。

## 之前的早期表面精度问题是否解决

已解决到题目规定的四位输出精度。此前粗网格在第1秒表面含水率有约0.005 kg/kg的级间差异；本次正式值来自FV1280/2560的Richardson组合，第1秒表面C为 **{result['surface_at_1s']['moisture_dry_basis']:.10f} kg/kg**，四位为 **2.5198**。

独立直接r实现的128/160阶短时加密使该点收敛到约2.519805232；与正式外推值之差约8.46×10⁻⁸ kg/kg，支持Pro所报8.477×10⁻⁸量级。原始FV2560自身并不能保证全部四位一致，外推及独立对照是本次精度结论的重要组成，不能在论文中省去。

## 应保留的模型边界

1. 第二问重新从0s统一采用附录3，不能接第一问1800s末态，也不能要求两问0.5h数值相同。
2. 经验ρcp用作有效容量；固定参考干密度用于有效水分积分。没有同时假定变ρ为严格相容的静止固定体积真实湿密度。
3. 等效水分边界、无显式潜热/携焓、无辐射及固定几何属于模型假设，未得到内部温湿响应或失重实验验证。
4. 本轮重新运行的二维r-z热质耦合情景支持前3h中截面近似：原交付记录的最大几何差约0.0017K、2.25×10⁻⁵ kg/kg，不能将其说成忽略端部后第四位必不改变，或视为数天阶段的严格误差界。
5. Excel正式时域为1—10800s；第3、4问的达标时间和收缩结果不在这次验收中。

## 非阻断事项与后续复用建议

**验证数组拆包。** 原交付清单的144项中，118项实物哈希匹配，另26个中间NPZ已在README声明另包提供，当前目录没有这些原数组。本轮已经从原附件重新生成相应计算阶段的数组，保存在 [新重跑验证目录](reproduced/validation/)。它们是本轮重算证据，不冒充原Pro数组。归档时将这份审核目录与Pro交付一并保存即可继续追溯。

**SciPy警告。** 本轮tests阶段出现一次`bdf.py:416: invalid value encountered in subtract`。后续测试、全场有限性、独立复算与所有导出检查均通过。隔离实验在SciPy初始未使用高阶差分槽注入信号NaN，精确复现同一警告，而有效状态、接受步数、输出与收支均与清零对照一致；自然重跑未再出现。该实验解释了可复现的非有效状态工作区机制，但原日志没有保存警告时的栈内数据，不能声称已反推出原警告确切发生在哪个测试步。详见 [诊断代码与记录](model_audit/bdf_workspace_probe.json)。本报告没有把本轮称为“无警告运行”，也未修改第三方库来掩盖警告。

**续算缓存与输出保护。** `run_all.py`目前只用输入哈希核验resume，未绑定源代码哈希及全部模型配置；输出路径保护也不是覆盖保护的完整实现。本轮使用新目录且没有resume，不影响本次结果。后续改源码或参数时使用另一个全新输出目录；若要长期复用，建议把代码/配置纳入缓存签名并禁止覆盖原交付目录。

**GitHub记录。** Pro提供的提交SHA、12个文本Git对象及三份原件身份均可与仓库对象核对；它也明确披露远端二进制下载失败后使用上传同哈希副本。本轮能核对资料身份与记录自洽，不能仅凭文件独立见证过去的每一次网页读取行为。

## 证据入口

- [本轮最终机器核验](acceptance_checks.json)、[完整运行状态](reproduced/run_state.json)、[运行日志](reproduction.log)、[本轮复现核验脚本](audit_reproduction.py)。
- [交付物独立审计](artifact_audit/交付物独立审计.md)、[逐项机器记录](artifact_audit/artifact_audit.json)。
- [独立数值核查](independent_numeric/独立数值核查.md)、[独立算法](independent_numeric/independent_radial.py)、[独立数值机器记录](independent_numeric/independent_audit.json)。
- [数学与物理口径审查](model_audit/model_audit.md)、[数学算子检查](model_audit/operator_spotcheck.json)、[BDF隔离诊断](model_audit/bdf_workspace_probe.json)。
- [本轮新生成Excel](reproduced/result2.xlsx)、[本轮新生成未舍入数组](reproduced/q2_unrounded.npz)、[本轮全格回读](reproduced/excel_audit.json)。

可再次执行`python audit_reproduction.py`复核本目录保存的运行和文件状态。完整重算命令、解释器与环境已写入`acceptance_checks.json`；重新启动整套求解时换用新的输出目录，避免与本次证据混用。

本审核针对数学模型、数值和文件交付，不把阶段Markdown等同于最终竞赛论文的版式、匿名或提交合规验收，也不把AI复核记为参赛队员已经人工审阅。
'''
    (HERE / '第二问验收报告.md').write_text(report, encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('exit_code', 'complete', 'sum_stage_elapsed_s',
        'original_delivery_files_changed', 'full_field_comparison_with_delivery',
        'runtime_warning_lines', 'all_reproduction_checks_passed')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
