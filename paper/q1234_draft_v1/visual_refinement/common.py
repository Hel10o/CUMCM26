"""Shared presentation helpers. Frozen inputs only; never imports a solver."""
from pathlib import Path
import hashlib
import json
import platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
OUT = BASE / 'figures/visual_refinement'
EVIDENCE = BASE / 'evidence/figure_refinement_20260912'
BASELINE = 'e1ae2bc23917cbbbd357cb14ca795896f4a39f25'
INK = '#253E4A'
TEAL = '#176B80'
AMBER = '#C77C35'
GREY = '#6C7C83'
PALE = '#E8EEF0'
MOISTURE = 'YlGnBu'
TEMPERATURE = 'YlOrBr'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def setup():
    OUT.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    names = {f.name for f in font_manager.fontManager.ttflist}
    font = next(n for n in ('Microsoft YaHei', 'SimSun') if n in names)
    plt.rcParams.update({'font.family':font,'font.size':8.5,'axes.labelsize':8.2,
        'axes.titlesize':9.2,'axes.titleweight':'normal','axes.titlepad':9,
        'xtick.labelsize':7.3,'ytick.labelsize':7.3,'legend.fontsize':7.3,
        'axes.linewidth':.65,'lines.linewidth':1.5,'axes.unicode_minus':False,
        'pdf.fonttype':42,'ps.fonttype':42,'figure.facecolor':'white',
        'axes.labelcolor':INK,'text.color':INK,'xtick.color':INK,'ytick.color':INK,
        'savefig.dpi':300})
    return font

def cm(w,h):
    return w/2.54,h/2.54

def clean(ax, grid='y'):
    ax.spines[['top','right']].set_visible(False)
    for spine in ax.spines.values():spine.set_color('#AAB6BA')
    ax.tick_params(direction='out',length=3,pad=3)
    ax.set_axisbelow(True)
    if grid:ax.grid(axis=grid,color=PALE,lw=.65)

def at(values,t):
    ids=np.flatnonzero(np.isclose(values,t,rtol=0,atol=1e-7))
    assert len(ids)==1,(t,ids)
    return int(ids[0])

class Evidence:
    def __init__(self,group):
        self.group=group
        self.sources={}
        self.outputs={}
        self.methods=[]
        self.checks=[]

    def source(self,name,purpose):
        path=ROOT/name
        assert path.is_file(),path
        self.sources[name]={'sha256':sha(path),'purpose':purpose}
        return path

    def npz(self,name,purpose):
        path=self.source(name,purpose)
        with np.load(path,allow_pickle=False) as a:
            return {k:a[k] for k in a.files}

    def json(self,name,purpose):
        return json.loads(self.source(name,purpose).read_text(encoding='utf-8'))

    def save(self,fig,name):
        for ext in ('pdf','svg','png'):
            p=OUT/(name+'.'+ext)
            kwargs={'metadata':{'CreationDate':None,'ModDate':None}} if ext=='pdf' else {}
            fig.savefig(p,dpi=600,**kwargs)
            self.outputs[p.relative_to(ROOT).as_posix()]={'sha256':sha(p),'bytes':p.stat().st_size}
        plt.close(fig)

    def finish(self,script,details):
        for name,item in self.sources.items():assert sha(ROOT/name)==item['sha256'],name
        s=Path(script).resolve()
        record={'baseline_commit':BASELINE,'scope':'Read frozen arrays and evidence; graphical postprocessing only, no PDE or scenario execution.',
            'script':s.relative_to(ROOT).as_posix(),'script_sha256':sha(s),'common_sha256':sha(Path(__file__)),
            'runtime':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},
            'sources':self.sources,'outputs':self.outputs,'details':details,
            'all_input_hashes_unchanged':True}
        p=EVIDENCE/(self.group+'_sources.json')
        p.write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
        print(json.dumps({'group':self.group,'frozen_inputs':len(self.sources),'outputs':len(self.outputs),'inputs_unchanged':True}))
