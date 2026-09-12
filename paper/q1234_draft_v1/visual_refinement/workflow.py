"""Draw a source-audited model workflow; read text only, never import solvers.

Run from the repository checkout. This diagram expresses model/output relations,
not the historical order of workbook packaging. All model text is audited at the
frozen baseline, so inserting the finished figure into the paper cannot change
the scientific source against which its arrows were checked.
"""
from common import *
import subprocess
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def baseline_text(name, needles):
    raw = subprocess.check_output(['git', 'show', f'{BASELINE}:{name}'], cwd=ROOT)
    lines = raw.decode('utf-8').splitlines()
    excerpts = []
    for needle in needles:
        hits = [i for i, line in enumerate(lines) if needle in line]
        assert hits, (name, needle)
        for i in hits:
            excerpts.append({'line': i + 1, 'text': lines[i], 'matched': needle})
    return {'git_commit': BASELINE, 'sha256': hashlib.sha256(raw).hexdigest(),
            'excerpts': excerpts}


def main():
    font = setup()
    ev = Evidence('workflow')
    source_specs = {
        'q1_complete_delivery/q1_delivery/source/q1_solver.py':
            'Read-only evidence: initial state, constant thermal parameters, D(C), and 1800 s solver contract.',
        'q4_complete_delivery/v1/q123_closeout/source/solve_unified_q23.py':
            'Read-only evidence: shared Appendix 3 cold-start coupled trajectory, environment, event and unrounded outputs.',
        'q4_complete_delivery/v1/q123_closeout/source/audit_unified_q23.py':
            'Read-only evidence: relation of unified trajectory to historical Q2 and Q3 exports, not executed this round.',
        'q4_complete_delivery/v1/source/run_q4.py':
            'Read-only evidence: independent cold start, prescribed radius, material coordinate and event output.',
        'q4_complete_delivery/v1/source/package_workbooks.py':
            'Read-only evidence: official Q2 and Q4 workbook input contracts; no workbook regenerated.',
    }
    for name, purpose in source_specs.items():
        ev.source(name, purpose).read_text(encoding='utf-8')
    baseline = {
        'paper/q1234_draft_v1/sections/problem_model.tex':
            ['初态统一', '初态并不首尾串接', '末小时', '线性插值'],
        'paper/q1234_draft_v1/sections/q1.tex': ['1800', '常热物性'],
        'paper/q1234_draft_v1/sections/q2.tex': ['同一', '3小时'],
        'paper/q1234_draft_v1/sections/q3.tex': ['极值', '执行'],
        'paper/q1234_draft_v1/sections/q4.tex': ['共同初态', '其余条件不变', '执行'],
        'paper/q1234_draft_v1/sections/validation_limits.tex': ['二维', '离散'],
    }
    baseline_records = {name: baseline_text(name, needles)
                        for name, needles in baseline.items()}

    fig = plt.figure(figsize=cm(15, 6.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 15), ylim=(0, 6.4))
    ax.axis('off')
    text_artists = []
    boxes = {}

    def text(x, y, label, size=7.5, color=INK, weight='normal', ha='center'):
        artist = ax.text(x, y, label, fontsize=size, color=color, weight=weight,
                         ha=ha, va='center', zorder=5)
        text_artists.append(artist)
        return artist

    def box(name, x, y, w, h, title, lines, color=TEAL, dashed=False,
            fill='#F7FAFB', title_size=8.0, body_size=7.4):
        boxes[name] = (x, y, w, h)
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.015,rounding_size=0.06',
                                   edgecolor=color, facecolor=fill, lw=.85,
                                   linestyle=(0, (3, 2)) if dashed else '-', zorder=3))
        if title:
            text(x+w/2, y+h-.22, title, title_size, color, 'bold')
        if lines:
            top = y+h-.53 if title else y+h-.20
            bottom = y+.20
            ys = np.linspace(top, bottom, len(lines)) if len(lines)>1 else [(top+bottom)/2]
            for yy, label in zip(ys, lines):
                text(x+w/2, yy, label, body_size, color if dashed else INK)

    def link(points, dashed=False, arrow=True, color=TEAL):
        points = np.asarray(points)
        style = (0, (3, 2)) if dashed else '-'
        ax.plot(points[:, 0], points[:, 1], color=color, lw=.9,
                linestyle=style, solid_capstyle='butt', zorder=1)
        if arrow:
            a, b = points[-2], points[-1]
            direction = (b-a)/np.linalg.norm(b-a)
            ax.add_patch(FancyArrowPatch(b-direction*.16, b,
                arrowstyle='-|>', mutation_scale=7.2, color=color, lw=.7,
                shrinkA=0, shrinkB=0, zorder=2))

    # Shared measured inputs and a separately labelled long-time assumption.
    box('input', .28, 5.48, 14.44, .76, '', [], fill='#F5F8F9')
    text(7.5, 6.00, '共同初态：28 °C、2.55 kg/kg；附件1：前 4 h 环境观测', 8.0)
    text(7.5, 5.70, '长时延拓假设（Q2 / Q3 / Q4）：4 h 后取末小时均值平台', 7.6, AMBER)
    # A bus distributes the common initial state; no result state is fed forward.
    link([(7.5, 5.48), (7.5, 5.27)], arrow=False)
    link([(2.01, 5.27), (12.65, 5.27)], arrow=False)
    for x in (2.01, 7.1, 12.65):
        link([(x, 5.27), (x, 5.05)])

    box('q1_model', .28, 3.96, 3.46, 1.09, 'Q1 · 附录2',
        ['一维径向；常热物性', 'D(C) 随含水率变化'])
    box('q23_model', 4.10, 3.96, 6.00, 1.09, 'Q2 / Q3 · 附录3，固定半径',
        ['一维径向温湿联立（变物性）', '共用同一未舍入全过程轨迹'])
    box('q4_model', 10.56, 3.96, 4.16, 1.09, 'Q4 · 附录4 + 附件2 R(t)',
        ['一维材料域温湿联立', '从共同初态独立计算'])

    box('q1_output', .28, 2.21, 3.46, 1.37, 'Q1 输出',
        ['独立计算至 1800 s', '表1–2', 'result1.xlsx'])
    box('q2_output', 4.10, 2.21, 2.64, 1.37, 'Q2 输出',
        ['前 3 h 规定表3–4', '全过程输出', 'result2.xlsx'])
    box('q3_output', 7.10, 2.21, 3.00, 1.37, 'Q3 阈值事件',
        ['空间极值 → 等号根', '加余量 → 执行点', '表5 / result3.xlsx'])
    box('q4_output', 10.56, 2.21, 4.16, 1.37, 'Q4 阈值事件与输出',
        ['空间极值 → 等号根', '加余量 → 执行点', '表6 / result4.xlsx'])
    link([(2.01, 3.96), (2.01, 3.58)])
    link([(7.10, 3.96), (7.10, 3.78)], arrow=False)
    link([(5.42, 3.78), (8.60, 3.78)], arrow=False)
    link([(5.42, 3.78), (5.42, 3.58)])
    link([(8.60, 3.78), (8.60, 3.58)])
    link([(12.65, 3.96), (12.65, 3.58)])

    box('q4_control', 10.56, 1.27, 4.16, .74, '',
        ['同物性恒半径条件对照', '其余条件保持一致'],
        color=AMBER, dashed=True, fill='#FEFAF4', body_size=7.5)
    # Association comes from the model, never from the Q4 execution state.
    link([(10.56, 4.40), (10.34, 4.40), (10.34, 1.69), (10.56, 1.69)],
         dashed=True, arrow=False, color=AMBER)

    box('validation', .28, .18, 14.44, .84, '', [], color=GREY,
        dashed=True, fill='#F8FAFA')
    text(7.5, .74, '并行校核：独立离散、网格 / 时间加密、二维中截面与全域节点检查', 7.7)
    text(7.5, .42, '用于数值可信度和适用范围；正式工作簿由各问主轨迹输出', 7.5, GREY)
    # Dashed, arrowless lines denote checks rather than state transfer.
    link([(.28, 4.40), (.09, 4.40), (.09, .59), (.28, .59)],
         dashed=True, arrow=False, color=GREY)
    link([(4.10, 4.40), (3.92, 4.40), (3.92, 1.02)],
         dashed=True, arrow=False, color=GREY)
    link([(14.72, 4.40), (14.91, 4.40), (14.91, .59), (14.72, .59)],
         dashed=True, arrow=False, color=GREY)
    text(.38, 1.62, '实线箭头：主流程', 7.4, TEAL, ha='left')
    text(4.20, 1.62, '虚线：校核 / 条件对照关系', 7.4, GREY, ha='left')

    # Layout checks only. None constitutes a scientific/model validation.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    text_bounds = []
    for artist in text_artists:
        b = artist.get_window_extent(renderer)
        assert bounds.contains(b.x0, b.y0) and bounds.contains(b.x1, b.y1), artist.get_text()
        text_bounds.append({'text': artist.get_text(), 'font_pt': artist.get_fontsize(),
                            'inside_canvas': True})
    ev.save(fig, 'model_workflow')
    details = {
        'figure_kind': 'Deterministic vector workflow, not a computed scientific field or a historical file-build graph.',
        'dimensions_cm': [15, 6.4], 'font': font, 'minimum_font_pt': 7.4,
        'scope': 'One requested overview figure. No numerical arrays, solver modules, scenario jobs, workbook edits or TeX edits.',
        'baseline_paper_texts': baseline_records,
        'arrow_evidence': [
            {'id': 'A1', 'relation': 'Common initial state and measured environment to Q1',
             'sources': ['q1_solver.py:21-35,82,167-198', 'problem_model.tex baseline excerpts'],
             'meaning': 'Q1 starts independently at 28 degC and 2.55 kg/kg; no post-4h assumption is used in its 1800s horizon.'},
            {'id': 'A2', 'relation': 'Common initial state and environment to the shared Q2/Q3 model',
             'sources': ['solve_unified_q23.py:1-6,46-60'],
             'meaning': 'One Appendix 3 fully coupled cold start; pre-4h observation interpolation and explicitly assumed last-hour mean platform thereafter.'},
            {'id': 'A3', 'relation': 'Common initial state and environment to Q4',
             'sources': ['run_q4.py:1-5,20-26', 'q4.tex baseline excerpts'],
             'meaning': 'An independent Appendix 4 cold start with prescribed attachment2 R(t), not a continuation of Q3.'},
            {'id': 'A4', 'relation': 'Q1 model to Q1 1800s output',
             'sources': ['q1_solver.py:167-198,240', 'q1.tex baseline excerpts'],
             'meaning': 'Constant thermal properties only; moisture diffusivity remains D(C), as q1_solver.py:140 explicitly computes.'},
            {'id': 'A5', 'relation': 'Shared Q2/Q3 trajectory branches to Q2 reporting',
             'sources': ['solve_unified_q23.py:46-81', 'package_workbooks.py:234-240,288', 'q2.tex baseline excerpts'],
             'meaning': 'Q2 required first-three-hour tables and full-trajectory workbook derive from unrounded coupled states.'},
            {'id': 'A6', 'relation': 'Shared Q2/Q3 trajectory branches to Q3 event and output',
             'sources': ['solve_unified_q23.py:58-60,72-81', 'audit_unified_q23.py:59-68', 'q3.tex baseline excerpts'],
             'meaning': 'Spatial extrema are checked for the equality event and execution margin. Historical result3 packaging is not asserted to be generated by solve_unified_q23.py; this is the paper model/output relation.'},
            {'id': 'A7', 'relation': 'Q4 model to Q4 event and output',
             'sources': ['run_q4.py:29-54,92-94', 'package_workbooks.py:218-230', 'q4.tex baseline excerpts'],
             'meaning': 'One-dimensional reconstructed extrema/equality event and execution point; no continuous two-dimensional guarantee is added.'},
            {'id': 'D1', 'relation': 'Q4 model associated with same-property fixed-radius control',
             'sources': ['run_q4.py:100-102', 'q4.tex baseline excerpts'],
             'meaning': 'Independent conditional comparison at common material/environment/boundary settings; not a Q3/Q4 property comparison or a state continuation. Dashed line has no arrowhead.'},
            {'id': 'D2-D4', 'relation': 'Models associated with parallel numerical and geometric checks',
             'sources': ['problem_model.tex baseline excerpts', 'validation_limits.tex baseline excerpts'],
             'meaning': 'Validation/applicability evidence; not the source of official workbooks. Dashed, arrowless associations do not encode a state pipeline or a continuous-domain certificate.'},
        ],
        'input_encoding': 'Observed first-4h data and assumed later plateau are separate text lines; the assumption is explicitly named and amber. The common frame itself is solid.',
        'text_extent_check': text_bounds,
        'numerical_recalculation': False,
        'pde_or_scenario_execution': False,
        'new_strong_claims': False,
    }
    ev.finish(__file__, details)


if __name__ == '__main__':
    main()
