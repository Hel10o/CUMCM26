"""Redraw validation figures by reading frozen NPZ/JSON evidence only.

No solver, integrator, root finder, state interpolation, or scenario is run.
"""
from common import *
from matplotlib.lines import Line2D


GEOMETRY = 'q4_complete_delivery/v1/validation/geometry/'
ENVIRONMENT = 'q1234_overall_review_delivery/v1/evidence/environment/'
CASES = (
    ('q1', '问题一', 'q1_80x128', 'q1_80x0', 1800., '1800 s',
     '7.2533', ('2.274929', '2.293532'), 1e-10, '-10'),
    ('q2', '问题二', 'q23_80x256_integral', 'q23_80x0_integral', 10800., '3 h',
     '4.7118', ('1.327482', '1.382492'), 1e-5, '-5'),
    ('q4', '问题四', 'q4_80x128_integral', 'q4_80x0_integral', 21600., '6 h',
     '2.7379', ('1.024545', '1.065198'), 1e-7, '-7'),
)
SCENARIOS = ('temperature_minus_1K', 'temperature_plus_1K',
             'boundary_minus_0p005', 'boundary_plus_0p005')
SCENARIO_LABELS = ('温度 −1 K', '温度 +1 K', '边界 b −0.005', '边界 b +0.005')
EXPECTED_ROOTS = {
    'q3': ('59.341275', '55.688357', '57.382748', '57.584113'),
    'q4': ('52.729346', '49.525343', '50.993818', '51.218753'),
}
EXPECTED_DELTAS = {
    'q3': ('+1.867279', '-1.785639', '-0.091249', '+0.110117'),
    'q4': ('+1.637343', '-1.566660', '-0.098185', '+0.126750'),
}


def extract(evidence, stem, target):
    source = GEOMETRY + stem + '.npz'
    data = evidence.npz(source, 'Frozen full-grid snapshot, reference weights and geometry; read only')
    snapshot_index = at(data['snapshot_times_s'], target)
    time_index = at(data['time_s'], target)
    midplane = at(data['z_m'], 0.)
    assert midplane == 0
    field = data['snapshots'][snapshot_index, ..., 1]
    profile = field[midplane]
    weights = data['weights']
    assert weights.size == field.size and np.all(weights > 0)
    assert len(profile) == len(data['reference_r_m']) == 81
    assert data['mid'].shape[1] == 21
    np.testing.assert_allclose(profile[[0, -1]], data['mid'][time_index, [0, -1], 1], rtol=0, atol=1e-12)
    radius = float(data['radius_m'][time_index])
    radius0 = float(data['reference_r_m'][-1])
    r_cm = data['reference_r_m'] * radius / radius0 * 100
    mean = float(field.reshape(-1) @ weights / weights.sum())
    initial = data['snapshots'][at(data['snapshot_times_s'], 0.), ..., 1]
    initial_mean = float(initial.reshape(-1) @ weights / weights.sum())
    assert abs(initial_mean - 2.55) < 1e-12
    return {'source': source, 'snapshot_index': snapshot_index,
            'snapshot_time_s': float(data['snapshot_times_s'][snapshot_index]),
            'snapshot_shape': list(data['snapshots'].shape),
            'full_radial_nodes': len(profile), 'stored_mid_nodes': data['mid'].shape[1],
            'midplane_index': midplane, 'midplane_z_m': float(data['z_m'][midplane]),
            'reference_radius_m': radius0, 'current_radius_m': radius,
            'current_r_cm': r_cm.tolist(), 'C_kg_per_kg': profile.tolist(),
            'initial_mean_C': initial_mean, 'weighted_mean_C': mean,
            'weight_sum': float(weights.sum()), 'saved_mid_endpoint_check': True}


def reduction(evidence):
    records = []
    fig = plt.figure(figsize=cm(16.4, 9.0))
    fig.text(.08, .989, r'中截面终时差值  $\Delta C=C_{\mathrm{2D}}-C_{\mathrm{1D}}$', va='top', fontsize=8.4)
    for i, (case, title, two_stem, one_stem, target, timing, percent, means, scale, power) in enumerate(CASES):
        two = extract(evidence, two_stem, target)
        one = extract(evidence, one_stem, target)
        np.testing.assert_array_equal(two['current_r_cm'], one['current_r_cm'])
        diff = np.asarray(two['C_kg_per_kg']) - np.asarray(one['C_kg_per_kg'])
        observed_means = tuple(f"{d['weighted_mean_C']:.6f}" for d in (two, one))
        loss_increase = 100 * ((2.55 - two['weighted_mean_C']) / (2.55 - one['weighted_mean_C']) - 1)
        assert observed_means == means and f'{loss_increase:.4f}' == percent
        record = {'case': case, 'label': title, 'time_s': target, 'display_time': timing,
                  'two_d': two, 'one_d': one, 'difference_C_kg_per_kg': diff.tolist(),
                  'endpoint_profile_max_abs_difference': float(np.max(np.abs(diff))),
                  'endpoint_profile_min_difference': float(diff.min()),
                  'endpoint_profile_max_difference': float(diff.max()),
                  'axis_multiplier': scale, 'display_means': means,
                  'loss_increase_percent': loss_increase, 'display_loss_increase_percent': percent}
        records.append(record)
        ax = fig.add_axes([.080 + .307 * i, .595, .258, .258])
        clean(ax)
        ax.axhline(0, color=GREY, lw=.75, zorder=1)
        ax.plot(two['current_r_cm'], diff / scale, color=TEAL, lw=1.6,
                marker='o', markevery=10, ms=2.0, markeredgewidth=0)
        fig.text(.080 + .307 * i, .909, f'({chr(97+i)}) {title} · {timing}', fontsize=8.7)
        ax.text(0, 1.025, rf'$\Delta C$ / ($10^{{{power}}}$ kg/kg)', transform=ax.transAxes, fontsize=7.6, va='bottom')
        ax.set(xlabel='当前径向距离 / cm', xlim=(0, two['current_r_cm'][-1]))
        ax.xaxis.label.set_fontsize(7.7)
        ax.set_xticks([0, 1, 2] if i < 2 else [0, .5, 1])
        if i == 0:
            ax.set_ylim(-8.0, 3.5); ax.set_yticks([-6, -3, 0, 3])
        elif i == 1:
            ax.set_ylim(-2.5, 1.0); ax.set_yticks([-2, -1, 0, 1])
        else:
            ax.set_ylim(-9.6, .6); ax.set_yticks([-9, -6, -3, 0])

    fig.text(.080, .429, '(d) 各时窗终点的整根平均', fontsize=8.7)
    handles = [Line2D([], [], color=TEAL, marker='o', ls='', ms=4.1, label='二维'),
               Line2D([], [], color=AMBER, marker='s', ls='', ms=3.9, label='配对一维')]
    fig.legend(handles=handles, loc='center left', bbox_to_anchor=(.49, .441), ncol=2,
               frameon=False, handletextpad=.4, columnspacing=1.2)
    fig.text(.935, .429, '失水增加', ha='right', fontsize=7.8)
    lower = fig.add_axes([.215, .173, .600, .204])
    clean(lower, 'x')
    lower.spines['left'].set_visible(False)
    lower.tick_params(axis='y', length=0, pad=7)
    for i, record in enumerate(records):
        a = record['two_d']['weighted_mean_C']
        b = record['one_d']['weighted_mean_C']
        # A small, declared visual y-offset separates close point markers;
        # the moisture value is carried only by the shared horizontal axis.
        ya, yb = i-.105, i+.105
        lower.plot([a, b], [ya, yb], color='#B7C0C4', lw=1.1, zorder=2)
        lower.scatter([a], [ya], color=TEAL, marker='o', s=19, zorder=3)
        lower.scatter([b], [yb], color=AMBER, marker='s', s=18, zorder=3)
        lower.annotate(record['display_means'][0], (a, ya), xytext=(-5, 0),
                       textcoords='offset points', ha='right', va='center', fontsize=7.4, color=TEAL)
        lower.annotate(record['display_means'][1], (b, yb), xytext=(5, 0),
                       textcoords='offset points', ha='left', va='center', fontsize=7.4, color=AMBER)
        lower.text(1.20, i, record['display_loss_increase_percent']+'%',
                   transform=lower.get_yaxis_transform(), ha='right', va='center', fontsize=7.7)
    lower.set_yticks(range(3), [r['label']+' · '+r['display_time'] for r in records])
    lower.set(xlim=(.79, 2.55), ylim=(2.45, -.45), xlabel='体积加权平均含水率 / (kg/kg)')
    lower.set_xticks([1.0, 1.5, 2.0, 2.5])
    fig.text(.215, .018, '各行时窗不同；失水增加仅按各行的一维、二维配对计算。', color=GREY, fontsize=7.0)
    evidence.save(fig, 'dimension_reduction')
    return records


def environment(evidence):
    records = []
    fig, ax = plt.subplots(figsize=cm(16.4, 6.2))
    fig.subplots_adjust(left=.218, right=.974, top=.81, bottom=.29)
    clean(ax, 'x')
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', length=0, pad=9)
    ax.axvline(0, color=GREY, lw=.9, zorder=1)
    for i in range(4):
        ax.axhline(i, color=PALE, lw=.55, zorder=0)
    for case, title, color, marker, offset in (
        ('q3', '问题三 · 固定半径', TEAL, 'o', -.19),
        ('q4', '问题四 · 规定收缩', AMBER, 's', .19)):
        baseline = evidence.json(ENVIRONMENT+case+'_baseline_n40.json', 'Frozen same-n40 scenario baseline root')
        assert baseline['n'] == 40 and baseline['start_s'] == 14400.
        entries = []
        for i, scenario in enumerate(SCENARIOS):
            name = ENVIRONMENT+case+'_'+scenario+'_n40.json'
            data = evidence.json(name, 'Frozen n40 environmental scenario root; this script does not execute it')
            assert data['case'] == case and data['n'] == 40 and data['start_s'] == 14400.
            assert data['source_npz_sha256'] == baseline['source_npz_sha256']
            delta = (data['critical_s'] - baseline['critical_s']) / 3600
            assert f"{data['critical_h']:.6f}" == EXPECTED_ROOTS[case][i]
            assert f'{delta:+.6f}' == EXPECTED_DELTAS[case][i]
            yy = i + offset
            ax.scatter([delta], [yy], marker=marker, color=color, s=25, zorder=3,
                       label=title if i == 0 else None)
            ax.annotate(f'{delta:+.6f}', (delta, yy), xytext=(6 if delta > 0 else -6, 0),
                        textcoords='offset points', ha='left' if delta > 0 else 'right',
                        va='center', fontsize=7.7, color=color)
            entries.append({'scenario': scenario, 'label': SCENARIO_LABELS[i], 'source': name,
                            'critical_s': data['critical_s'], 'critical_h': data['critical_h'],
                            'delta_root_h': delta, 'display_delta_root_h': f'{delta:+.6f}',
                            'same_4h_source_state_hash': True})
        records.append({'case': case, 'baseline_source': ENVIRONMENT+case+'_baseline_n40.json',
                        'baseline_critical_s': baseline['critical_s'],
                        'baseline_critical_h': baseline['critical_h'], 'scenarios': entries})
    ax.set(ylim=(3.48, -.48), xlim=(-2.62, 2.62), xlabel='相对同阶基线的临界根变化 / h')
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_yticks(range(4), SCENARIO_LABELS)
    fig.text(.218, .936, '4 h 后单因素情景', fontsize=9, va='center')
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='center right', bbox_to_anchor=(.983, .936), ncol=2,
               frameon=False, handletextpad=.4, columnspacing=1.0)
    fig.text(.218, .042, '负值：根提前     正值：根后移     人工设定幅度；第四问规定半径不变。',
             color=GREY, fontsize=7.0)
    evidence.save(fig, 'environment_sensitivity')
    return records


def main():
    font = setup()
    evidence = Evidence('validation')
    # Read implementation text solely to bind the saved coordinate convention.
    evidence.source('q4_complete_delivery/v1/source/geometry_solver_executed.py',
                    'Coordinate interpretation only; never imported or executed')
    reduction_records = reduction(evidence)
    environment_records = environment(evidence)
    evidence.finish(__file__, {
        'font': font, 'figure_size_cm': {'dimension_reduction': [16.4, 9.0], 'environment_sensitivity': [16.4, 6.2]},
        'reduction': reduction_records, 'environment': environment_records,
        'methods': {
            'midplane': 'z_m=0 is index 0 of the half-cylinder; full 81-node snapshots used. The 21-node mid archive is only an endpoint check.',
            'current_radius': 'reference_r_m * radius_m(target) / reference_r_m[-1]. No spatial interpolation.',
            'difference': 'Subtract paired stored profiles at the single named target time. This is not a maximum over the checked time window, a physical error estimate or a continuous bound.',
            'mean': 'sum(saved target C * saved control-volume weights) / sum(weights). The common current-volume factor for affine Q4 shrinkage cancels.',
            'mass_basis': '体积加权平均在空间均匀干密度假设下等于干质量加权平均。',
            'loss_increase': '100 * ((2.55 - mean_2D) / (2.55 - mean_1D) - 1); not relative error of mean moisture.',
            'mean_marker_offsets': 'The two mean markers are offset vertically by +/-0.105 row solely to prevent overlap. Only the horizontal coordinate encodes mean moisture.',
            'environment_delta': '(frozen scenario critical_s - frozen same-n40 baseline critical_s) / 3600; no change relative to an official rounded execution time.',
            'environment_scope': 'Artificial single-factor after-4h scenarios with a shared saved 4h state in each question and prescribed Q4 radius held fixed. No error bars or confidence intervals.',
        },
        'checks': {'paired_current_radii_equal': True, 'all_exact_target_snapshots_found': True,
                   'six_means_three_loss_percentages_match_existing_table_values': True,
                   'eight_environment_roots_and_eight_deltas_match_existing_table_values': True,
                   'all_scenario_initial_state_hashes_match_their_baseline': True},
        'limitations': ['No PDE, numerical integration, new parameter scenario, or numerical-result revision.',
                        'No claim that the different Q1/Q2/Q4 time windows rank reduction accuracy.',
                        'Endpoint subtraction can expose solver-scale small residual differences; it does not isolate physical dimensional error.',
                        'The new reduction figure displays endpoint means, not the old mean time histories.'],
    })


if __name__ == '__main__':
    main()
