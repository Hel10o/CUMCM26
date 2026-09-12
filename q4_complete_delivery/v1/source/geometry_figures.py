"""Scientific figures from completed saved fields only."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from geometry_solver import DEST

def preferred(case):
    for stem in (f'{case}_80x128_integral',f'{case}_40x128_integral',f'{case}_40x64_integral',f'{case}_40x64'):
        p=DEST/(stem+'.npz')
        if p.exists():return stem,np.load(p)
    return None,None

fig,axes=plt.subplots(2,2,figsize=(10,6),constrained_layout=True)
for row,case in enumerate(['q23','q4']):
    stem,b=preferred(case)
    if b is None:continue
    t=b['time_s']/3600
    axes[row,0].plot(t,b['mid'][:,0,1],label='midplane axis / global wettest')
    axes[row,0].plot(t,b['end'][:,0,1],label='end-face axis')
    axes[row,0].axhline(.15,color='0.4',ls=':',lw=1)
    axes[row,0].set(xlabel='Time (h)',ylabel='Dry-basis moisture (kg/kg)',title=case.upper()+': spatial scope')
    suffix='_integral' if '_integral' in stem else ''
    nr=int(stem.split('_')[1].split('x')[0]);a=np.load(DEST/f'{case}_{nr}x0{suffix}.npz')
    ts,ia,ib=np.intersect1d(a['time_s'],b['time_s'],return_indices=True)
    delta=np.max(np.abs(b['mid'][ib,:,1]-a['mid'][ia,:,1]),axis=1)
    axes[row,1].plot(ts/3600,delta)
    axes[row,1].set(xlabel='Time (h)',ylabel='Max sampled radial |2D - 1D| (kg/kg)',title=case.upper()+': midplane difference')
    axes[row,0].legend(fontsize=8)
for ax in axes.flat:ax.grid(alpha=.2)
fig.savefig(DEST/'midplane_and_end_effects.png',dpi=180);plt.close(fig)

stem,b=preferred('q4')
if b is not None:
    u=b['event_states'][1];r=b['reference_r_m']*b['radius_m'][-1]/.02;z=b['z_m']
    fig,axes=plt.subplots(2,1,figsize=(8,4.8),constrained_layout=True,gridspec_kw={'height_ratios':[1,2]})
    im=axes[0].pcolormesh(z*100,r*100,u[:,:,1].T,shading='auto',cmap='viridis',vmin=.0499,vmax=.15)
    axes[0].set(xlabel='Distance from midplane z (cm)',ylabel='Radius r (cm)',title=f'Q4 current half-cylinder at Cmax = 0.15; {stem}')
    fig.colorbar(im,ax=axes[0],label='C (kg/kg)')
    axes[1].plot(r*100,u[0,:,1],label='midplane')
    axes[1].plot(r*100,u[len(z)//2,:,1],label='intermediate cross-section')
    axes[1].plot(r*100,u[-1,:,1],label='end face')
    axes[1].set(xlabel='Current radius r (cm)',ylabel='C (kg/kg)');axes[1].legend();axes[1].grid(alpha=.2)
    fig.savefig(DEST/'q4_current_domain_event.png',dpi=180);plt.close(fig)
