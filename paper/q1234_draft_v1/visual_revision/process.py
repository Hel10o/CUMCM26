"""Q1 space-time fields and Q2 state paths, using stored outputs only."""
from common import *
from matplotlib.lines import Line2D

def main():
    setup()
    ev=Evidence('process')
    q1=ev.npz('q1_complete_delivery/q1_delivery/output/q1_unrounded.npz','Q1 saved seconds and 21 radial samples')
    q2=ev.npz('q4_complete_delivery/v1/q123_closeout/output/q23_unified.npz','Q2 accepted unified trajectory; first3h only')
    q1_end=at(q1['time_s'],1800)
    assert [f'{v:.4f}' for v in q1['temperature_degC'][q1_end,[0,-1]]]==['33.5753','36.7856']
    assert [f'{v:.4f}' for v in q1['moisture_dry_basis'][q1_end,[0,-1]]]==['2.5500','1.5102']
    fig=plt.figure(figsize=cm(16.4,8.15))
    q1_records=[]
    for col,(key,cmap,title,unit,lo,hi,ticks) in enumerate([
        ('temperature_degC',TEMPERATURE,'(a) 热响应的时空演化','温度 / °C',28,37,[28,31,34,37]),
        ('moisture_dry_basis',MOISTURE,'(b) 失水的时空演化','干基含水率 / (kg/kg)',1.5,2.55,[1.5,1.85,2.2,2.55])]):
        left=.095+col*.49
        ax=fig.add_axes([left,.20,.365,.56])
        grid=q1[key][:q1_end+1].T
        image=ax.pcolormesh(q1['time_s'][:q1_end+1]/60,q1['radius_cm'],grid,
            shading='nearest',cmap=cmap,vmin=lo,vmax=hi,rasterized=True)
        ax.set(xlim=(0,30),ylim=(0,2),xlabel='时间 / min',ylabel='径向距离 / cm')
        ax.set_xticks([0,10,20,30]);ax.set_yticks([0,.5,1,1.5,2])
        clean(ax,grid=None)
        # Label physical locations once without assigning a new front threshold.
        ax.text(.02,.95,'表面',transform=ax.transAxes,color=INK,fontsize=7,
            bbox={'facecolor':'white','edgecolor':'none','alpha':.78,'pad':1.5})
        ax.text(.02,.04,'轴心',transform=ax.transAxes,color=INK,fontsize=7,
            bbox={'facecolor':'white','edgecolor':'none','alpha':.78,'pad':1.5})
        ca=fig.add_axes([left,.83,.365,.023])
        cb=fig.colorbar(image,cax=ca,orientation='horizontal',ticks=ticks)
        cb.outline.set_visible(False);cb.ax.tick_params(length=2,pad=2,labelsize=7)
        fig.text(left,.944,title,fontsize=9.2,color=INK)
        fig.text(left,.89,unit,fontsize=7.5,color=GREY)
        values=q1[key][q1_end,[0,-1]]
        label=(f'末时轴心 / 表面：{values[0]:.4f} / {values[1]:.4f} '+('°C' if col==0 else 'kg/kg'))
        fig.text(left,.048,label,fontsize=7.1,color=INK)
        q1_records.append({'key':key,'shape':list(grid.shape),'saved_times_s':[0,1800],
            'display_endpoint':[f'{v:.4f}' for v in values], 'colour_limits':[lo,hi]})
    ev.save(fig,'q1_profiles')

    end=at(q2['time_s'],10800)
    times=np.arange(0,10801,15)
    ids=np.asarray([at(q2['time_s'],t) for t in times])
    field=q2['profile_TC']
    terminal=field[end]
    delta_T=terminal[-1,0]-terminal[0,0]
    delta_C=terminal[0,1]-terminal[-1,1]
    assert f'{delta_T:.4f}'=='0.1169' and f'{delta_C:.4f}'=='0.7581'
    fig=plt.figure(figsize=cm(16.4,8.1))
    left=fig.add_axes([.095,.23,.395,.61])
    right=fig.add_axes([.61,.23,.355,.61])
    marks=[1800,5400,10800]
    for radial,color,linestyle,label in [(0,TEAL,'-','轴心'),(-1,AMBER,'--','表面')]:
        TC=field[ids,radial,:]
        left.plot(TC[:,0],TC[:,1],color=color,ls=linestyle,label=label)
        for j,t in enumerate(marks):
            p=field[at(q2['time_s'],t),radial,:]
            left.plot(p[0],p[1],'o' if radial==0 else 's',ms=3.2,color=color)
            offsets=([(0,7),(-8,7),(-22,-10)] if radial==0 else [(-2,-12),(-24,-12),(-25,8)])
            dx,dy=offsets[j]
            left.annotate(f'{t/3600:g} h',xy=p,xytext=(dx,dy),textcoords='offset points',fontsize=7,color=color)
        # Direction arrow uses two saved states, never an inferred intermediate state.
        for a,b in [(2700,3150),(7200,7650)]:
            x=field[at(q2['time_s'],a),radial,:];y=field[at(q2['time_s'],b),radial,:]
            left.annotate('',xy=y,xytext=x,arrowprops={'arrowstyle':'-|>','lw':1,'color':color,'mutation_scale':9})
    left.plot(28,2.55,'o',color=GREY,ms=3)
    left.annotate('共同初态',xy=(28,2.55),xytext=(4,-13),textcoords='offset points',fontsize=7,color=GREY)
    left.set(xlabel='温度 / °C',ylabel='干基含水率 / (kg/kg)',xlim=(27,51.5),ylim=(.86,2.70),title='(a) 温湿状态路径')
    left.set_xticks([28,35,42,49]);left.set_yticks([1,1.5,2,2.5])
    clean(left)
    left.legend(loc='lower left',frameon=False,ncol=2,columnspacing=1)
    palette=['#8FBCC5','#4C91A2',TEAL]
    selected=[]
    for h,color,ls in zip([.5,1.5,3],palette,[':', '--','-']):
        i=at(q2['time_s'],h*3600)
        right.plot(q2['radius_cm'],field[i,:,1],color=color,ls=ls,label=f'{h:g} h')
        right.scatter(q2['radius_cm'][[0,-1]],field[i,[0,-1],1],s=10,color=color,zorder=3)
        selected.append({'time_s':h*3600,'profile_C':field[i,:,1].tolist()})
    right.set(xlabel='径向距离 / cm',ylabel='干基含水率 / (kg/kg)',xlim=(0,2),ylim=(.86,2.70),title='(b) 含水率径向剖面')
    right.set_xticks([0,1,2]);right.set_yticks([1,1.5,2,2.5]);clean(right)
    right.legend(loc='lower left',frameon=False,ncol=3,columnspacing=.7,handlelength=1.4)
    fig.text(.095,.073,'3 h 温差：0.1169 K',fontsize=8.2,color=INK)
    fig.text(.61,.073,'3 h 含水率差：0.7581 kg/kg',fontsize=8.2,color=INK)
    ev.save(fig,'q2_profiles')
    ev.finish(__file__,{'q1':q1_records,
        'q1_display':'All saved second/radial samples; nearest cell colours; no new time/radius states, no front threshold.',
        'q2_display':'Axis/surface T-C paths connect every15s saved state from0 to10800s. Arrows connect saved states and show time direction. Right panel retains radial C profiles; all source arrays unchanged.',
        'q2_path_times_s':times.tolist(),'q2_radial_cm':q2['radius_cm'].tolist(),'q2_profiles':selected,
        'q2_terminal_deltas':{'temperature_K_display':'0.1169','C_display':'0.7581'},
        'no_fitting_smoothing_or_solving':True})

if __name__=='__main__':main()
