"""Publication figures built only from actual unrounded trajectories."""
from pathlib import Path
import argparse,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from q4_common import ROOT,read_numeric

def figures(base=ROOT,font=None):
    base=Path(base);dest=base/'figures';dest.mkdir(exist_ok=True)
    if font and Path(font).exists():font_manager.fontManager.addfont(font)
    plt.rcParams.update({'font.family':'Noto Sans CJK SC','axes.unicode_minus':False,'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':130,'savefig.dpi':240})
    z=np.load(base/'output/main.npz');fixed=np.load(base/'validation/fixed80.npz');ev=json.loads((base/'output/end_event.json').read_text())
    rd=read_numeric(base/'inputs/attachment2.xlsx',2)[1]
    def save(name):
        plt.savefig(dest/(name+'.png'),bbox_inches='tight');plt.savefig(dest/(name+'.svg'),bbox_inches='tight');plt.close()
    fig,ax=plt.subplots(figsize=(7.2,3.6));ax.plot(rd[:,0]/3600,rd[:,1],color='#176f85',lw=1.7,label='分段线性 R(t)')
    ax.scatter(rd[:,0]/3600,rd[:,1],s=11,color='#176f85',zorder=3,label='附件2观测')
    ax.axvline(ev['execution_h'],color='#ba6530',ls='--',label=f"执行时刻 {ev['execution_h']:.4f} h")
    ax.set(xlabel='时间 / h',ylabel='实际半径 / cm',title='观测半径与采用的收缩几何',xlim=(0,72));ax.legend(frameon=False);ax.grid(alpha=.18);save('radius_history')
    fig,axes=plt.subplots(1,2,figsize=(10,3.8));ids=[int(np.argmin(abs(z['time_s']-t))) for t in [1800,10800,21600,43200,86400,172800,ev['execution_s']]]
    for i in ids:
        r=np.sqrt(z['x'])*z['radius_m'][i]*100;lab=f"{z['time_s'][i]/3600:.2f} h"
        axes[0].plot(r,z['full_TC'][i,:,1],label=lab,lw=1.5)
    axes[0].set(xlabel='当前径向位置 / cm',ylabel='干基含水率 / (kg/kg)',title='移动域内的含水率分布');axes[0].legend(ncol=2,fontsize=8,frameon=False)
    for t in [600,1800,3600,10800]:
        i=int(np.argmin(abs(z['time_s']-t)));r=np.sqrt(z['x'])*z['radius_m'][i]*100
        axes[1].plot(r,z['full_TC'][i,:,0],label=f'{t/3600:.2f} h',lw=1.5)
    axes[1].set(xlabel='当前径向位置 / cm',ylabel='温度 / ℃',title='温度由耦合方程全程求解');axes[1].legend(frameon=False)
    for ax in axes:ax.grid(alpha=.18)
    fig.tight_layout();save('radial_profiles')
    fig,ax=plt.subplots(figsize=(7.2,4));ax.semilogy(fixed['time_s']/3600,fixed['max_C'],color='#81929d',lw=2,label='固定半径 2 cm，同附录4')
    ax.semilogy(z['time_s']/3600,z['max_C'],color='#176f85',lw=2,label='附件2收缩半径，同附录4')
    ax.axhline(.15,color='#ba6530',ls='--',label='严格阈值 0.15')
    ax.scatter([ev['execution_h']],[ev['execution_max_C']],color='#176f85',zorder=3)
    ax.set(xlabel='时间 / h',ylabel='全径向最大干基含水率 / (kg/kg)',title='控制物性不变的收缩机制比较',ylim=(.12,3));ax.legend(frameon=False);ax.grid(alpha=.18,which='both');save('shrinkage_comparison')
    fig,ax=plt.subplots(figsize=(7.2,4));sel=np.unique(np.r_[np.arange(0,len(z['time_s']),10),len(z['time_s'])-1])
    X=np.broadcast_to(z['time_s'][sel,None]/3600,(len(sel),len(z['x'])))
    Y=z['radius_m'][sel,None]*np.sqrt(z['x'])[None,:]*100
    pc=ax.pcolormesh(X,Y,z['full_TC'][sel,:,1],shading='gouraud',cmap='viridis',rasterized=True)
    ax.plot(z['time_s']/3600,z['radius_m']*100,color='#ba6530',lw=2,label='材料表面 R(t)')
    ax.set(xlabel='时间 / h',ylabel='实际径向位置 / cm',title='实际位置上的含水率轨迹：表面以外不适用',ylim=(0,2));fig.colorbar(pc,ax=ax,label='干基含水率 / (kg/kg)');ax.legend(frameon=True);save('current_domain_map')
    g=base/'validation/geometry';ns=[40,80,160,320];roots=[]
    for n in ns:roots.append(json.loads((g/f'q4_{n}x0_integral.json').read_text())['event_root_s'])
    tight=[320,640];tr=[json.loads((g/f'q4_{n}x0_integral_rtol2e-10.json').read_text())['event_root_s'] for n in tight]
    fig,axes=plt.subplots(1,2,figsize=(10,3.7));axes[0].loglog(ns,np.abs(np.array(roots)-ev['critical_s']),'o-',label='独立FV，标准时间配置');axes[0].loglog(tight,np.abs(np.array(tr)-ev['critical_s']),'s-',label='独立FV，加严时间配置')
    axes[0].set(xlabel='径向网格区间数',ylabel='相对谱主解的事件时间差 / s',title='独立空间与时间验证');axes[0].legend(frameon=False,fontsize=8);axes[0].grid(alpha=.18,which='both')
    b=z['balance'];axes[1].plot(b[:,0]/3600,b[:,-1],color='#176f85');axes[1].set(xlabel='时间 / h',ylabel='归一化水量残差 / (kg/kg)',title='移动材料域累计水量账本');axes[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0));axes[1].grid(alpha=.18);fig.tight_layout();save('verification')
    print('Saved 5 figure pairs PNG/SVG')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,default=ROOT);p.add_argument('--font');a=p.parse_args();figures(a.base,a.font)
