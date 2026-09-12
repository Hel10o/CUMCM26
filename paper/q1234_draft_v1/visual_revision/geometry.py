"""Q3/Q4 presentation only: stored trajectories, discrete events and geometry.

No solver is imported.  The small event rulers connect stored times, not an
interpolated moisture trajectory and not a confidence or error interval.
"""
from common import *
from matplotlib.colors import LogNorm
from matplotlib.ticker import FixedLocator, FixedFormatter
from openpyxl import load_workbook


def draw_process(ev, q23, q4, q23_meta, q4_event):
    fig = plt.figure(figsize=cm(16.4, 8.0))
    axes = [fig.add_axes([left, .44, .365, .405]) for left in (.10, .605)]
    qi = np.asarray([at(q23['time_s'], t) for t in np.r_[np.arange(0, 206907, 60), 206906.76]])
    records = [
        {'title':'(a) 问题三：附录3 · 固定半径', 'time':q23['time_s'][qi]/3600,
         'axis':q23['profile_TC'][qi, 0, 1], 'surface':q23['profile_TC'][qi, -1, 1],
         'root_s':q23_meta['events'][0]['root_s'], 'exec_s':q23_meta['end_s'],
         'exec_C':q23_meta['end_max_C'], 'exec_h':'57.4741', 'margin_display':'0.3701'},
        {'title':'(b) 问题四：附录4 · 规定收缩', 'time':q4['time_s']/3600,
         'axis':q4['full_TC'][:, 0, 1], 'surface':q4['surface_TC'][:, 1],
         'root_s':q4_event['critical_s'], 'exec_s':q4_event['execution_s'],
         'exec_C':q4_event['execution_max_C'], 'exec_h':'51.0921', 'margin_display':'0.3483'},
    ]
    assert q23_meta['events'][0]['max_C'] == .15
    assert q4_event['execution_s'] == q4['time_s'][-1]
    for ax, rec, left in zip(axes, records, (.10, .605)):
        clean(ax)
        ax.plot(rec['time'], rec['axis'], color=TEAL, label='轴心')
        ax.plot(rec['time'], rec['surface'], color=AMBER, ls='--', label='当前表面')
        ax.axhline(.15, color=GREY, lw=.9, ls=':', label='阈值 0.15')
        execution = float(rec['exec_h'])
        ax.scatter([execution], [rec['exec_C']], s=18, color=TEAL, zorder=5)
        ax.annotate(rec['exec_h']+' h', xy=(execution, rec['exec_C']),
                    xytext=(execution-13, .245), fontsize=7.5,
                    arrowprops={'arrowstyle':'-', 'lw':.65, 'color':GREY})
        ax.set(xlim=(0,60), ylim=(.045,2.9), yscale='log', xlabel='时间 / h', title=rec['title'])
        ax.set_xticks([0,12,24,36,48,60])
        ax.yaxis.set_major_locator(FixedLocator([.05,.15,.5,1.,2.5]))
        ax.yaxis.set_major_formatter(FixedFormatter(['0.05','0.15','0.5','1','2.5']))
        ax.minorticks_off()
        if ax is axes[0]:ax.set_ylabel('干基含水率 / (kg/kg)')
        # Each horizontal segment is a discrete time ruler, not C(t).
        ruler = fig.add_axes([left, .19, .365, .065])
        delta = rec['exec_s'] - rec['root_s']
        assert f'{delta:.4f}' == rec['margin_display']
        assert rec['exec_C'] < .15 and abs(rec['axis'][-1]-rec['exec_C']) < 1e-12
        ruler.plot([0, delta], [0,0], color='#AAB6BA', lw=1.)
        ruler.scatter([0], [0], s=25, facecolors='white', edgecolors=GREY, lw=1., zorder=3)
        ruler.scatter([delta], [0], s=25, color=TEAL, zorder=3)
        ruler.set(xlim=(-.012,.415), ylim=(-.4,.4))
        ruler.axis('off')
        ruler.text(0,.47,'等号根：0 s', ha='left', va='bottom', fontsize=7.3)
        ruler.text(.402,.47,'执行点：+'+rec['margin_display']+' s', ha='right', va='bottom', fontsize=7.3)
        fig.text(left+.1825,.108, f"执行最大值 {rec['exec_C']:.12f} < 0.15", ha='center', fontsize=7.6)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.555,1.01), ncol=3,
               frameon=False, handlelength=2.4, columnspacing=1.5)
    fig.text(.555,.035,'下方仅标示已存临界根与执行点；横向距离表示相对临界根的秒数。',ha='center',fontsize=7.0,color=GREY)
    ev.save(fig, 'q3_q4_drying')
    return [{k:v for k,v in rec.items() if k not in ('time','axis','surface')} for rec in records]


def draw_shrinkage(ev, q4, observations):
    fig=plt.figure(figsize=cm(16.4,9.2))
    top=fig.add_axes([.10,.55,.79,.33])
    cax=fig.add_axes([.915,.55,.018,.33])
    profiles=fig.add_axes([.10,.135,.47,.255])
    radius=fig.add_axes([.725,.135,.235,.255])
    clean(top, None);clean(profiles);clean(radius)
    times=q4['time_s']/3600
    radii_cm=100*q4['radius_m'][:,None]*np.sqrt(q4['x'])[None,:]
    field=q4['full_TC'][:,:,1]
    assert np.all(field>0) and field.shape==radii_cm.shape
    assert np.allclose(radii_cm[:,-1],100*q4['radius_m'],rtol=0,atol=1e-12)
    # Gouraud shading only interpolates colors within saved time/radius cells.
    # Every outer vertex is exactly on the saved current material boundary.
    mesh=top.pcolormesh(np.broadcast_to(times[:,None],field.shape),radii_cm,field,
                        cmap=MOISTURE,norm=LogNorm(vmin=.05,vmax=2.55),shading='gouraud',rasterized=True)
    top.plot(times,radii_cm[:,-1],color=INK,lw=1.,label='输入半径边界')
    shown=observations[observations[:,0]<=q4['time_s'][-1]][::4]
    top.scatter(shown[:,0]/3600,shown[:,1],s=9,facecolor='white',edgecolor=INK,lw=.6,zorder=4,
                label='附件2观测点（抽样）')
    top.set(xlim=(0,times[-1]),ylim=(0,2.04),xlabel='时间 / h',ylabel='当前半径 / cm',
            title='(a) 收缩材料域内的一维模型含水率')
    top.set_xticks([0,12,24,36,48]);top.set_yticks([0,1,2])
    top.text(18,1.50,'材料域外',fontsize=8,color=GREY,ha='center')
    top.annotate('执行 '+f'{times[-1]:.4f}'+' h',xy=(times[-1],1.2),xytext=(times[-1]-12,1.43),
                 fontsize=7.0,arrowprops={'arrowstyle':'-','lw':.6,'color':GREY})
    top.legend(loc='upper center',bbox_to_anchor=(.55,.995),ncol=2,frameon=False,
               fontsize=7.0,handlelength=1.8,columnspacing=1.2)
    bar=fig.colorbar(mesh,cax=cax,ticks=[.05,.15,.5,1.,2.55])
    bar.ax.set_yticklabels(['0.05','0.15','0.5','1','2.55'])
    bar.ax.tick_params(labelsize=6.8,length=2,pad=2)
    bar.ax.set_title('C / (kg/kg)\n对数色标',fontsize=6.5,pad=6)
    bar.outline.set_edgecolor('#AAB6BA');bar.outline.set_linewidth(.6)
    slice_hours=[6,12,24,51.0921]
    profile_rows=[]
    for hour,col,style in zip(slice_hours,(TEAL,AMBER,INK,GREY),('-','--','-.',':')):
        i=at(q4['time_s'],hour*3600)
        r=radii_cm[i];c=field[i]
        profiles.plot(r,c,color=col,ls=style,lw=1.4,label=f'{hour:g} h')
        profiles.scatter([r[-1]],[c[-1]],s=8,color=col,zorder=3)
        profile_rows.append({'time_h':hour,'time_index':i,'current_radius_cm':float(r[-1]),
                             'axis_C':float(c[0]),'surface_C':float(c[-1])})
    profiles.axhline(.15,color='#AAB6BA',lw=.7,ls=':')
    profiles.set(xlim=(0,1.45),ylim=(0,1.85),xlabel='当前径向距离 / cm',ylabel='干基含水率 / (kg/kg)',
                 title='(b) 曲线止于各时刻的材料表面')
    profiles.set_xticks([0,.5,1]);profiles.set_yticks([0,.5,1,1.5])
    profiles.legend(loc='upper right',ncol=2,frameon=False,fontsize=6.8,columnspacing=.8,handlelength=1.9)
    radius.plot(observations[:,0]/3600,observations[:,1],color=INK,lw=1.)
    radius.scatter(observations[::4,0]/3600,observations[::4,1],s=7,facecolor='white',edgecolor=INK,lw=.6,zorder=3)
    radius.axvline(times[-1],color=AMBER,ls='--',lw=.85)
    radius.set(xlim=(0,72),ylim=(1.16,2.05),xlabel='时间 / h',ylabel='半径 / cm',title='(c) 附件2观测输入')
    radius.set_xticks([0,24,48,72]);radius.set_yticks([1.2,1.6,2.0])
    radius.annotate('执行时刻',xy=(times[-1],1.68),xytext=(30,1.90),fontsize=6.5,color=AMBER,ha='center',
                    arrowprops={'arrowstyle':'-','lw':.6,'color':AMBER})
    ev.save(fig, 'q4_shrinkage')
    return {'profiles':profile_rows,'heatmap_time_count':len(times),'radial_node_count':field.shape[1],
            'current_radius_mapping':'r_cm=100*radius_m(t)*sqrt(x)',
            'time_stop_h':float(times[-1]),'radius_observations_count':len(observations),
            'log_color_limits':[.05,2.55],'heatmap_visual_interpolation':'Gouraud color interpolation between saved mesh nodes; no PDE state evaluated or extrapolated.',
            'outside_material':'No mesh or fill beyond the current outer vertex R(t); white background.',
            'observation_time_end_h':float(observations[-1,0]/3600)}


def main():
    font=setup()
    ev=Evidence('geometry')
    q23=ev.npz('q4_complete_delivery/v1/q123_closeout/output/q23_unified.npz','Q3 frozen full trajectory, axis and surface moisture')
    q4=ev.npz('q4_complete_delivery/v1/output/main.npz','Q4 frozen time/radius/material field, current surface and formal endpoint')
    q23_meta=ev.json('q4_complete_delivery/v1/q123_closeout/output/q23_unified.json','Saved Q3 exact root and execution extrema')
    q4_event=ev.json('q4_complete_delivery/v1/output/end_event.json','Saved Q4 root, execution point and endpoint maximum')
    path=ev.source('q4_complete_delivery/v1/inputs/attachment2.xlsx','Observed external radius history; visual input trace only')
    wb=load_workbook(path,read_only=True,data_only=True)
    observations=np.asarray([row[:2] for row in list(wb.active.values)[1:] if row[0] is not None],float)
    wb.close()
    assert observations.shape==(145,2)
    np.testing.assert_allclose(np.interp(q4['time_s'],observations[:,0],observations[:,1])/100,q4['radius_m'],rtol=0,atol=1e-12)
    events=draw_process(ev,q23,q4,q23_meta,q4_event)
    shrinking=draw_shrinkage(ev,q4,observations)
    details={'font':font,'events':events,'shrinkage':shrinking,
        'process_sampling':'Q3 every stored 60 s plus exact execution output; Q4 all 3067 stored outputs. Rulers read exact saved JSON root and execution metadata.',
        'event_scope':'Each root/execution result is for its one-dimensional effective model and assumed environment; no continuous 2D or physical execution guarantee.',
        'between_question_scope':'Q3 uses appendix 3 and fixed radius; Q4 uses appendix 4 and prescribed shrinkage. Difference between these two curves is not a pure shrinkage effect.',
        'old_new_mapping':{'q3_q4_drying':'Retains axis, current surface, threshold and official execution labels; adds stored discrete root-to-execution evidence.',
                           'q4_shrinkage':'Retains all 145 radius observations through 72 h in a small panel and four exact-time current-radius profiles; adds moisture map only through official execution.'},
        'checks':{'q3_event_max_matches_last_frozen_axis':True,'q4_event_max_matches_last_frozen_axis':True,
                  'displayed_root_to_execution_deltas_match_paper':True,'saved_radius_matches_linear_observation_input':True,
                  'no_outside_material_mesh':True}}
    ev.finish(__file__,details)


if __name__=='__main__':
    main()
