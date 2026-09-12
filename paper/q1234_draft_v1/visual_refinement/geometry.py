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
    axes = [fig.add_axes([left, .43, .365, .37]) for left in (.10, .605)]
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
        ax.set(xlim=(0,60), ylim=(.045,2.9), yscale='log', xlabel='时间 / h')
        fig.text(left+.1825,.845,rec['title'],ha='center',fontsize=8.7)
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
    fig.text(.535,.985,'物性不同，非收缩效应对照',ha='center',va='top',
             fontsize=8.7,fontweight='bold',color=INK)
    fig.legend(handles, labels, loc='center', bbox_to_anchor=(.555,.920), ncol=3,
               frameon=False, handlelength=2.4, columnspacing=1.5)
    fig.text(.555,.035,'下方仅标示已存临界根与执行点；横向距离表示相对临界根的秒数。',ha='center',fontsize=7.0,color=GREY)
    ev.save(fig, 'q3_q4_drying')
    return [{k:v for k,v in rec.items() if k not in ('time','axis','surface')} for rec in records]


def draw_shrinkage(ev, q4, observations, q4_event, fixed):
    fig=plt.figure(figsize=cm(16.4,9.2))
    top=fig.add_axes([.10,.55,.79,.33])
    cax=fig.add_axes([.915,.55,.018,.33])
    profiles=fig.add_axes([.10,.175,.47,.215])
    comparison=fig.add_axes([.725,.250,.235,.140])
    clean(top, None);clean(profiles);clean(comparison, 'x')
    times=q4['time_s']/3600
    radii_cm=100*q4['radius_m'][:,None]*np.sqrt(q4['x'])[None,:]
    field=q4['full_TC'][:,:,1]
    assert np.all(field>0) and field.shape==radii_cm.shape
    assert np.allclose(radii_cm[:,-1],100*q4['radius_m'],rtol=0,atol=1e-12)
    # Gouraud shading only interpolates colors within saved time/radius cells.
    # Every outer vertex is exactly on the saved current material boundary.
    mesh=top.pcolormesh(np.broadcast_to(times[:,None],field.shape),radii_cm,field,
                        cmap=MOISTURE,norm=LogNorm(vmin=.05,vmax=2.55),shading='gouraud',rasterized=True)
    # Full observed radius input is retained through 72 h. The moisture mesh
    # stops at the official execution point and is never filled after it.
    top.plot(observations[:,0]/3600,observations[:,1],color=INK,lw=.9,label='分段线性半径输入')
    top.scatter(observations[:,0]/3600,observations[:,1],s=4.4,facecolor='white',edgecolor=INK,lw=.45,zorder=4,
                label='附件2观测点')
    top.axvline(times[-1],color=AMBER,ls='--',lw=.8)
    top.set(xlim=(0,72),ylim=(0,2.04),xlabel='时间 / h',ylabel='当前半径 / cm',
            title='(a) 收缩材料域内的一维模型含水率')
    top.set_xticks([0,12,24,36,48,60,72]);top.set_yticks([0,1,2])
    top.text(18,1.46,'材料域外',fontsize=7.5,color=GREY,ha='center')
    top.text(62, .62, '仅观测半径', fontsize=7.3, color=GREY, ha='center')
    top.annotate('执行 '+f'{times[-1]:.4f}'+' h',xy=(times[-1],1.2),xytext=(times[-1]-12,1.43),
                 fontsize=7.0,arrowprops={'arrowstyle':'-','lw':.6,'color':GREY})
    top.legend(loc='upper center',bbox_to_anchor=(.37,.995),ncol=2,frameon=False,
               fontsize=6.8,handlelength=1.8,columnspacing=1.2)
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
    profiles.text(1.445,.18,'0.15',ha='right',va='bottom',fontsize=6.0,color=GREY)
    profiles.set(xlim=(0,1.45),ylim=(0,2.2),xlabel='当前径向距离 / cm',ylabel='干基含水率 / (kg/kg)',
                 title='(b) 曲线止于各时刻的材料表面')
    profiles.set_xticks([0,.5,1]);profiles.set_yticks([0,.5,1,1.5])
    profiles.legend(loc='upper right',ncol=2,frameon=False,fontsize=6.8,columnspacing=.8,handlelength=1.9)
    fixed_h=float(fixed['event']['critical_s'])/3600
    shrink_h=float(q4_event['critical_s'])/3600
    assert fixed_h==float(fixed['event']['critical_h'])
    assert shrink_h==float(q4_event['critical_h'])
    delta_h=fixed_h-shrink_h
    percent=100*delta_h/fixed_h
    assert f'{fixed_h:.4f}'=='129.8484' and f'{shrink_h:.4f}'=='51.0920'
    assert f'{delta_h:.4f}'=='78.7564' and f'{percent:.2f}'=='60.65'
    assert fixed['radius_interpolation']=='fixed' and fixed['event']['root_is_1d']
    comparison.spines['left'].set_visible(False)
    for yy,h,col,label in [(1.,fixed_h,INK,'恒半径'),(.15,shrink_h,TEAL,'规定收缩')]:
        comparison.plot([0,h],[yy,yy],color=col,lw=3.0,solid_capstyle='butt')
        comparison.scatter([h],[yy],s=10,color=col,zorder=3)
        comparison.annotate(f'{label}  {h:.4f} h',(0,yy),xytext=(0,6),
                            textcoords='offset points',fontsize=7.0,color=col,ha='left',va='bottom')
    comparison.set(xlim=(0,140),ylim=(-.25,1.65),xlabel='模型临界时间 / h')
    comparison.xaxis.label.set_fontsize(7.2)
    comparison.set_xticks([0,60,120]);comparison.set_yticks([])
    fig.text(.8425,.428,'(c) 附录4 同物性 · 同环境',ha='center',fontsize=8.1)
    fig.text(.725,.099,f'临界时间差 {delta_h:.4f} h',fontsize=7.1,color=INK)
    fig.text(.725,.056,f'模型临界时间缩短 {percent:.2f}%',fontsize=7.1,color=TEAL)
    fig.text(.10,.018,'条件对照包含扩散尺度与干基边界交换标度的共同变化。',fontsize=7.0,color=GREY)
    ev.save(fig, 'q4_shrinkage')
    return {'profiles':profile_rows,'heatmap_time_count':len(times),'radial_node_count':field.shape[1],
            'current_radius_mapping':'r_cm=100*radius_m(t)*sqrt(x)',
            'time_stop_h':float(times[-1]),'radius_observations_count':len(observations),
            'log_color_limits':[.05,2.55],'heatmap_visual_interpolation':'Gouraud color interpolation between saved mesh nodes; no PDE state evaluated or extrapolated.',
            'outside_material':'No mesh or fill beyond the current outer vertex R(t); white background.',
            'observation_time_end_h':float(observations[-1,0]/3600),
            'all_145_observations_drawn':True,
            'post_execution_display':'Observed piecewise-linear radius only through 72 h; no moisture mesh, zero fill or PDE continuation beyond execution.',
            'controlled_comparison':{'fixed_source':'q4_complete_delivery/v1/validation/fixed80.json',
                'shrinking_source':'q4_complete_delivery/v1/output/end_event.json',
                'fixed_critical_h':fixed_h,'shrinking_critical_h':shrink_h,
                'fixed_critical_s':fixed['event']['critical_s'],'shrinking_critical_s':q4_event['critical_s'],
                'unit_conversion':'critical_s / 3600; exact equality to each stored critical_h asserted',
                'critical_difference_h':delta_h,'model_critical_time_reduction_percent':percent,
                'display_hours':['129.8484','51.0920'],'display_difference_h':'78.7564','display_percent':'60.65',
                'scope':'Appendix 4 same properties and environment; fixed dry-basis hm. Difference includes diffusion length and boundary exchange scaling; not a Q3/Q4 property comparison.'}}


def main():
    font=setup()
    ev=Evidence('geometry')
    q23=ev.npz('q4_complete_delivery/v1/q123_closeout/output/q23_unified.npz','Q3 frozen full trajectory, axis and surface moisture')
    q4=ev.npz('q4_complete_delivery/v1/output/main.npz','Q4 frozen time/radius/material field, current surface and formal endpoint')
    q23_meta=ev.json('q4_complete_delivery/v1/q123_closeout/output/q23_unified.json','Saved Q3 exact root and execution extrema')
    q4_event=ev.json('q4_complete_delivery/v1/output/end_event.json','Saved Q4 root, execution point and endpoint maximum')
    q4_meta=ev.json('q4_complete_delivery/v1/output/main.json','Frozen main-run metadata for shared conditional environment and source identity')
    fixed=ev.json('q4_complete_delivery/v1/validation/fixed80.json','Frozen appendix4 fixed-radius conditional critical root; no new scenario')
    assert q4_meta['radius_interpolation']=='linear'
    assert q4_meta['source_sha256']==fixed['source_sha256']
    assert q4_meta['future_environment']==fixed['future_environment']
    assert q4_meta['event']['critical_s']==q4_event['critical_s']
    path=ev.source('q4_complete_delivery/v1/inputs/attachment2.xlsx','Observed external radius history; visual input trace only')
    wb=load_workbook(path,read_only=True,data_only=True)
    observations=np.asarray([row[:2] for row in list(wb.active.values)[1:] if row[0] is not None],float)
    wb.close()
    assert observations.shape==(145,2)
    np.testing.assert_allclose(np.interp(q4['time_s'],observations[:,0],observations[:,1])/100,q4['radius_m'],rtol=0,atol=1e-12)
    events=draw_process(ev,q23,q4,q23_meta,q4_event)
    shrinking=draw_shrinkage(ev,q4,observations,q4_event,fixed)
    details={'font':font,'events':events,'shrinkage':shrinking,
        'process_sampling':'Q3 every stored 60 s plus exact execution output; Q4 all 3067 stored outputs. Rulers read exact saved JSON root and execution metadata.',
        'event_scope':'Each root/execution result is for its one-dimensional effective model and assumed environment; no continuous 2D or physical execution guarantee.',
        'between_question_scope':'Q3 uses appendix 3 and fixed radius; Q4 uses appendix 4 and prescribed shrinkage. Difference between these two curves is not a pure shrinkage effect.',
        'old_new_mapping':{'q3_q4_drying':'Retains all stored process and discrete-event information within original 16.4x8.0 cm; adds prominent non-causal between-property warning above the legend.',
                           'q4_shrinkage':'Retains moisture mesh only through execution and all four current-radius profiles. Full 145 observations move into upper panel through 72h; old radius-only lower panel is replaced by frozen same-property conditional root comparison within 16.4x9.2 cm.'},
        'figure_size_cm':{'q3_q4_drying':[16.4,8.0],'q4_shrinkage':[16.4,9.2]},
        'controlled_comparison_metadata':{'same_recorded_source_sha256':q4_meta['source_sha256'],
            'same_future_environment':q4_meta['future_environment'],
            'fixed_n':fixed['n'],'shrinking_n':q4_meta['n'],
            'scope':'Reuses the accepted fixed80 versus main120 roots already reported in the paper; does not claim same grid or a newly run convergence check.'},
        'checks':{'q3_event_max_matches_last_frozen_axis':True,'q4_event_max_matches_last_frozen_axis':True,
                  'displayed_root_to_execution_deltas_match_paper':True,'saved_radius_matches_linear_observation_input':True,
                  'no_outside_material_mesh':True,'fixed_and_shrinking_comparison_uses_roots_not_execution_times':True,
                  'controlled_comparison_numbers_match_existing_paper':True}}
    ev.finish(__file__,details)


if __name__=='__main__':
    main()
