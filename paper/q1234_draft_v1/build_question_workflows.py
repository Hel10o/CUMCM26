"""Draw four schematic solution workflows from audited paper text, never solvers."""
from pathlib import Path
import hashlib
import json
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'figures/question_workflows'
EVIDENCE = BASE / 'evidence/question_workflows_20260913'
BASELINE = 'c11fa40c72e1555a10dedf666b98b19ec0a5e863'
WIDTH, HEIGHT = 15.0, 3.2
INK, LINE = '#111111', '#1b2542'
FONT_SIZE = 9.2
FONTS = ['Times New Roman', 'SimSun']


def node(name, col, row, label, kind='process', height=.94):
    centers = [1.52, 5.39, 9.19, 13.12]
    widths = [2.80, 3.02, 3.02, 3.43]
    return dict(id=name, x=centers[col], y={0:2.38, 1:.80, 2:1.59}[row],
                w=widths[col], h=height, text=label, kind=kind)


def specifications():
    return {
        'q1_workflow': {
            'title':'问题一求解流程',
            'nodes':[
                node('input',0,2,'几何与初态\n环境记录\n附录2物性','input',1.46),
                node('heat',1,0,'常热物性\n导热方程'),
                node('water',1,1,'非线性水分扩散\nD(C)'),
                node('heat_solve',2,0,'圆环有限体积\nBDF隐式积分'),
                node('water_solve',2,1,'圆环有限体积\nBDF隐式积分'),
                node('temperature',3,0,'径向温度分布\n1800 s','output'),
                node('moisture',3,1,'径向含水率分布\n1800 s','output'),
            ],
            'edges': [('input','heat','split'),('input','water','split'),
                      ('heat','heat_solve','direct'),('water','water_solve','direct'),
                      ('heat_solve','temperature','direct'),('water_solve','moisture','direct')],
            'source_lines':[(5,30),(34,40),(76,93),(95,103)],
            'meaning':'Two separate integrations: Q1 D depends on C, not on T; no arrow transfers a thermal solution to the moisture solver.',
        },
        'q2_workflow': {
            'title':'问题二求解流程',
            'nodes':[
                node('initial',0,0,'共同初态\n环境记录与延拓','input'),
                node('properties',0,1,'固定半径\n附录3物性','input'),
                node('model',1,2,'径向热质耦合\n表面Robin闭合',height=1.13),
                node('solve',2,2,'Chebyshev配点\nRadau联立积分',height=1.13),
                node('output',3,0,'前3 h规定结果\n温度与含水率','output'),
                node('trajectory',3,1,'未舍入全程轨迹\n供问题三判定','output'),
            ],
            'edges':[('initial','model','merge'),('properties','model','merge'),
                     ('model','solve','direct'),('solve','output','split'),('solve','trajectory','split')],
            'source_lines':[(5,9),(38,56),(73,106),(110,128)],
            'meaning':'Independent common-state start, with jointly closed surface states inside the coupled Radau system; one trajectory supplies both Q2 and Q3.',
        },
        'q3_workflow': {
            'title':'问题三求解流程',
            'nodes':[
                node('trajectory',0,0,'问题二温湿轨迹\n阈值0.15 kg/kg','input'),
                node('checks',0,1,'网格加密\n独立积分对照','input'),
                node('candidate',1,0,'下降穿越检测\n括区定位候选根'),
                node('margin',1,1,'设置经验\n数值余量'),
                node('root',2,0,'径向重构极值\n复核等号根'),
                node('execution',2,1,'向上选取执行点\n复核严格不等式'),
                node('output',3,2,'模型干燥时长\n57.4741 h\n径向含水率分布','output',1.46),
            ],
            'edges':[('trajectory','candidate','direct'),('candidate','root','direct'),
                     ('checks','margin','direct'),('margin','execution','direct'),
                     ('root','execution','down'),('execution','output','merge')],
            'source_lines':[(6,28),(49,76),(93,138)],
            'meaning':'Node crossing first gives a candidate, then reconstructed radial extrema are checked; an empirical margin and upward time quantization give a separately rechecked execution point. This is the one-dimensional event procedure, not a continuous 2D guarantee.',
        },
        'q4_workflow': {
            'title':'问题四求解流程',
            'nodes':[
                node('input',0,0,'半径与环境观测\n共同初态、附录4','input'),
                node('conservation',0,1,'恒长度径向收缩\n干物质守恒','input'),
                node('coordinate',1,0,'半径历程插值\n材料坐标变换'),
                node('model',1,1,'参考域热质耦合\n表面交换条件'),
                node('solve',2,2,'Chebyshev配点\nRadau独立积分',height=1.13),
                node('event',3,0,'阈值事件与余量\n执行点复核'),
                node('output',3,1,'51.0921 h\n实际径向含水率','output'),
            ],
            'edges':[('input','coordinate','direct'),('conservation','model','direct'),
                     ('coordinate','model','down'),('model','solve','merge'),
                     ('solve','event','split'),('event','output','down')],
            'source_lines':[(6,25),(32,78),(89,101),(106,139),(168,213)],
            'meaning':'Independent initial-state integration in the moving material reference domain; event detection, margin and verification precede current-radius outputs. The conditional fixed-radius comparison and 2D validation remain in the body and are not drawn as state-transfer steps.',
        },
    }


def connect(ax, source, target, kind):
    if kind == 'down':
        points = [(source['x'],source['y']-source['h']/2),
                  (target['x'],target['y']+target['h']/2)]
    else:
        start=(source['x']+source['w']/2,source['y'])
        end=(target['x']-target['w']/2,target['y'])
        if abs(start[1]-end[1]) < .01:
            points=[start,end]
        else:
            x=(start[0]+end[0])/2
            points=[start,(x,start[1]),(x,end[1]),end]
    xs,ys=zip(*points)
    ax.plot(xs,ys,color=INK,lw=.72,zorder=1,solid_capstyle='butt')
    a,b=points[-2:]
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=8,
                                shrinkA=0,shrinkB=0,lw=.72,color=INK,zorder=2))
    return points


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':FONTS,'font.size':FONT_SIZE,
                         'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'path',
                         'axes.unicode_minus':False})
    font_files={f:font_manager.findfont(f,fallback_to_default=False) for f in FONTS}
    records={}
    for name,spec in specifications().items():
        fig=plt.figure(figsize=(WIDTH/2.54,HEIGHT/2.54))
        ax=fig.add_axes([0,0,1,1]); ax.set(xlim=(0,WIDTH),ylim=(0,HEIGHT)); ax.axis('off')
        nodes={n['id']:n for n in spec['nodes']}
        edge_records=[{'from':a,'to':b,'points':connect(ax,nodes[a],nodes[b],k)} for a,b,k in spec['edges']]
        texts=[]
        for n in spec['nodes']:
            style='round,pad=0,rounding_size=0.42' if n['kind']=='input' else 'square,pad=0'
            ax.add_patch(FancyBboxPatch((n['x']-n['w']/2,n['y']-n['h']/2),n['w'],n['h'],
                                        boxstyle=style,lw=.8,edgecolor=LINE,facecolor='white',zorder=3))
            t=ax.text(n['x'],n['y'],n['text'],ha='center',va='center',
                      fontsize=FONT_SIZE,linespacing=1.22,color=INK,zorder=4)
            texts.append((n,t))
        fig.canvas.draw(); renderer=fig.canvas.get_renderer()
        checks=[]
        for n,t in texts:
            box=t.get_window_extent(renderer)
            corners=ax.transData.transform([(n['x']-n['w']/2,n['y']-n['h']/2),
                                           (n['x']+n['w']/2,n['y']+n['h']/2)])
            fits=box.x0>=corners[0,0]+1 and box.x1<=corners[1,0]-1 and box.y0>=corners[0,1]+1 and box.y1<=corners[1,1]-1
            assert fits,(name,n['id'],n['text'],box,corners)
            checks.append({'node':n['id'],'text_inside_node':bool(fits)})
        outputs={}
        for ext in ['pdf','svg','png']:
            p=OUT/(name+'.'+ext)
            opts={'dpi':220} if ext=='png' else {}
            if ext=='pdf': opts['metadata']={'Title':spec['title'],'Creator':'Matplotlib; deterministic text workflow','CreationDate':None,'ModDate':None}
            fig.savefig(p,**opts)
            outputs[p.relative_to(BASE).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        plt.close(fig)
        source=f'paper/q1234_draft_v1/sections/{name[:2]}.tex'
        raw=subprocess.check_output(['git','show',BASELINE+':'+source],cwd=ROOT)
        lines=raw.decode().splitlines()
        records[name]={**spec,'edges':edge_records,'checks':checks,'outputs':outputs,
                       'source':{'commit':BASELINE,'path':source,'sha256':hashlib.sha256(raw).hexdigest(),
                                 'excerpts':[{'start':a,'end':b,'text':'\n'.join(lines[a-1:b])} for a,b in spec['source_lines']]}}
    result={'baseline_commit':BASELINE,'diagram_dimensions_cm':[WIDTH,HEIGHT],
            'font_size_pt':FONT_SIZE,'fonts':font_files,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'Schematic workflows from existing text. No numerical arrays, solver imports, PDE runs or scenarios.',
            'figures':records}
    (EVIDENCE/'workflow_sources.json').write_bytes(json.dumps(result,ensure_ascii=False,indent=2).encode())
    print('Four per-question workflows rendered; all node labels fit their boxes.')


if __name__=='__main__':
    main()
