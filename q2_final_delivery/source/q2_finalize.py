"""Assemble independently checked Q2 fields; never read the handoff preflight as a target."""
from __future__ import annotations
import argparse,csv,json,platform,sys
from pathlib import Path
import numpy as np
import scipy
from q2_core import load_environment,properties,P
from q2_tests import difference,FIELDS


def dec4(a):
    a=np.asarray(a)
    return np.fromiter((float(format(float(x),'.4f')) for x in a.ravel()),float,count=a.size).reshape(a.shape)

def comparison(a,b,times,radii):
    d=difference(a,b,times,radii)
    d['four_decimal_mismatches']=int(np.count_nonzero(dec4(a)!=dec4(b)))
    return d

def readsol(v,name):
    path=v/f'{name}.npz';a=dict(np.load(path,allow_pickle=False))
    if path.with_suffix('.json').exists():a['stats']=json.loads(path.with_suffix('.json').read_text())
    return a

def finalize(input_path,out):
    out=Path(out);v=out/'validation';out.mkdir(parents=True,exist_ok=True)
    data,audit=load_environment(input_path)
    (out/'input_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    fine=readsol(v,'fv_n2560');coarse=readsol(v,'fv_n1280');previous=readsol(v,'fv_n640')
    ref=readsol(v,'cheb_n192');ref0=readsol(v,'cheb_n128')
    tim=fine['time_s'];rad=fine['radius_cm'];it=np.arange(1800,10801,1800);ir=np.arange(0,21,5)
    assert np.array_equal(tim,np.arange(10801)) and np.array_equal(rad,np.linspace(0,2,21))
    result={k:fine[k].copy() for k in ('time_s','radius_cm','environment')}
    extrapkeys=FIELDS+('average_temperature_degC','average_moisture_dry_basis')
    for k in extrapkeys:result[k]=(4*fine[k]-coarse[k])/3
    np.savez_compressed(out/'q2_unrounded.npz',**result)
    report={'model':'S(C)*T_t=div(k(C)*grad(T)); C_t=div(D(TK,C)*grad(C)); midplane equivalent Robin',
      'output_scope':'1..10800 seconds; working interpretation of the 3-hour Q2 output, not days-long full drying',
      'method':'Vertex-centred finite volume + local coupled BDF + Richardson (4*u_2560-u_1280)/3',
      'environment_interpolation':'piecewise linear, knots every 60 seconds; no extrapolation',
      'dimensions':[10800,21,2],'total_values':453600,'table_values':60,
      'precision':{},'grid_convergence':[],'runtime':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform()}}
    for k in FIELDS:
        old=(4*coarse[k]-previous[k])/3
        report['precision'][k]={
          'final_vs_independent':comparison(result[k][1:],ref[k][1:],tim[1:],rad),
          'table_vs_independent':comparison(result[k][np.ix_(it,ir)],ref[k][np.ix_(it,ir)],tim[it],rad[ir]),
          'Richardson_1280_vs_2560':comparison(old[1:],result[k][1:],tim[1:],rad),
          'spectral_128_vs_192':comparison(ref0[k][1:],ref[k][1:],tim[1:],rad),
          'fine_FV_vs_independent':comparison(fine[k][1:],ref[k][1:],tim[1:],rad)}
        assert report['precision'][k]['final_vs_independent']['four_decimal_mismatches']==0
        assert report['precision'][k]['Richardson_1280_vs_2560']['four_decimal_mismatches']==0
        assert report['precision'][k]['spectral_128_vs_192']['four_decimal_mismatches']==0
        assert np.isfinite(result[k]).all()
        np.savetxt(out/f'{k}_unrounded.csv',np.column_stack([tim,result[k]]),delimiter=',',fmt='%.17g',
          header='time_s,'+','.join(f'r={x:.1f}cm' for x in rad),comments='')
        name='temperature' if k==FIELDS[0] else 'moisture'
        np.savetxt(out/f'table_{name}.csv',np.column_stack([tim[it]/3600,dec4(result[k][np.ix_(it,ir)])]),
          delimiter=',',fmt=['%.1f']+['%.4f']*5,header='time_h,0cm,0.5cm,1cm,1.5cm,2cm',comments='')
    for n in (20,40,80,160,320,640,1280,2560):
        a=readsol(v,f'fv_n{n}');row={'N':n,'dr_cm':2/n,'stats':a['stats']}
        row.update({k:comparison(a[k][1:],ref[k][1:],tim[1:],rad) for k in FIELDS})
        row['table_errors']={k:comparison(a[k][np.ix_(it,ir)],ref[k][np.ix_(it,ir)],tim[it],rad[ir]) for k in FIELDS}
        report['grid_convergence'].append(row)
    tight=readsol(v,'fv_n1280_time_tight')
    report['time_convergence']={'fixed_N':1280,'baseline':coarse['stats'],'tight':tight['stats'],
       'differences':{k:comparison(coarse[k][1:],tight[k][1:],tim[1:],rad) for k in FIELDS}}
    assert max(q['max_abs'] for q in report['time_convergence']['differences'].values())<1e-8
    if (v/'geometry_unit_tests.json').exists():
        report['geometry_unit_tests']=json.loads((v/'geometry_unit_tests.json').read_text())
    report['unit_tests']=json.loads((v/'unit_tests.json').read_text())
    report['balance']={'grid':1280,'method':'six-point Gauss quadrature of independently differentiated accepted BDF polynomial and boundary flux on every accepted step',
       'mass_quantity':'volume average of C; multiply by constant reference dry density for an effective water inventory',
       'thermal_quantity':'space-time integral of S(C)*T_t, NOT endpoint difference of integral S(C)*T',
       'note':'Constituent FV balance is tested. Richardson postprocessing is not itself a new conservative time integrator.',
       **{k:coarse['stats'][k] for k in ('water_balance_max_kgkg','effective_heat_balance_max_J_m3','net_heat_input_J_m3','effective_heat_balance_relative')}}
    cpS=properties(coarse['snapshots_temperature_degC'][-1],coarse['snapshots_moisture_dry_basis'][-1])[0]
    ww=coarse['internal_weights_rdr']
    proxy=float(ww@(cpS*(coarse['snapshots_temperature_degC'][-1]-28))/ww.sum())
    report['balance']['endpoint_ST28_proxy_J_m3']=proxy
    report['balance']['proxy_minus_effective_heat_input_J_m3']=proxy-coarse['stats']['net_heat_input_J_m3']
    # Independent one-sided surface derivatives; measured on fine internal snapshots.
    T=fine['snapshots_temperature_degC'][1:];C=fine['snapshots_moisture_dry_basis'][1:]
    st=fine['snapshot_times_s'][1:];dr=P.R/2560
    deriv=lambda U:(25*U[:,-1]-48*U[:,-2]+36*U[:,-3]-16*U[:,-4]+3*U[:,-5])/(12*dr)
    Te=np.interp(st,data[:,0],data[:,1]);Ce=np.interp(st,data[:,0],data[:,2]);S,k,D=properties(T[:,-1],C[:,-1])
    bt=-k*deriv(T);qt=P.hT*(T[:,-1]-Te);bc=-D*deriv(C);qc=P.hm*(C[:,-1]-Ce)
    report['boundary_diagnostic']={'times_s':st.tolist(),'thermal_flux_relative_max':float(np.max(abs(bt-qt)/np.maximum(abs(qt),1e-14))),
      'mass_flux_relative_max':float(np.max(abs(bc-qc)/np.maximum(abs(qc),1e-14))),
      'thermal_outward_flux_W_m2':qt.tolist(),'mass_outward_effective_flux_m_s':qc.tolist(),
      'scope':'Fourth-order one-sided derivative diagnostic of fine-grid snapshots, not an analytical error bound'}
    report['field_checks']={'T_min':float(result[FIELDS[0]].min()),'T_max':float(result[FIELDS[0]].max()),
      'C_min':float(result[FIELDS[1]].min()),'C_max':float(result[FIELDS[1]].max()),
      'C_min_space_difference':float(np.diff(result[FIELDS[1]],axis=1).min()),
      'C_max_unexpected_radial_increase':float(np.diff(result[FIELDS[1]],axis=1).max()),
      'T_max_above_current_ambient':float(np.max(result[FIELDS[0]]-result['environment'][:,0,None])),
      'initial_T_error':float(np.max(abs(result[FIELDS[0]][0]-28))),
      'initial_C_error':float(np.max(abs(result[FIELDS[1]][0]-2.55)))}
    S,k,D=properties(result[FIELDS[0]],result[FIELDS[1]])
    assert result[FIELDS[0]].min()>=28-1e-10
    assert result[FIELDS[0]].max()<=np.max(data[data[:,0]<=10800,1])+1e-10
    assert result[FIELDS[1]].min()>0 and result[FIELDS[1]].max()<=2.55+1e-10
    assert np.all(S>0) and np.all(k>0) and np.all(D>0)
    report['local_property_ranges']={name:[float(val.min()),float(val.max())] for name,val in [('S_J_m3K',S),('k_W_mK',k),('D_m2_s',D)]}
    report['values_3h']={
      'T_center':float(result[FIELDS[0]][-1,0]),'T_surface':float(result[FIELDS[0]][-1,-1]),
      'C_center':float(result[FIELDS[1]][-1,0]),'C_surface':float(result[FIELDS[1]][-1,-1]),
      'mean_T':float(result['average_temperature_degC'][-1]),'mean_C':float(result['average_moisture_dry_basis'][-1]),
      'effective_water_reduction_percent':float((1-result['average_moisture_dry_basis'][-1]/2.55)*100)}
    sens0=readsol(v,'sensitivity_baseline');sens={}
    for name in ('hT_0.8','hT_1.2','hm_0.8','hm_1.2','pchip_all241','freeze_all_initial'):
        s=readsol(v,'sensitivity_'+name)
        sens[name]={'differences':{k:comparison(s[k],sens0[k],tim,rad) for k in FIELDS},
            'T_center_end':float(s[FIELDS[0]][-1,0]),'T_surface_end':float(s[FIELDS[0]][-1,-1]),
            'C_center_end':float(s[FIELDS[1]][-1,0]),'C_surface_end':float(s[FIELDS[1]][-1,-1]),'stats':s['stats']}
    sens['scope']='Deterministic scenarios; not parameter confidence intervals. Same N=320 and tolerances.'
    report['sensitivity']=sens
    (v/'sensitivity.json').write_text(json.dumps(sens,ensure_ascii=False,indent=2),encoding='utf-8')
    geom={}
    for nr,nz in ((20,40),(20,80),(40,80)):
        if not (v/f'axisymmetric_{nr}_{nz}.npz').exists():continue
        a=readsol(v,f'axisymmetric_{nr}_{nz}');pair=readsol(v,f'axisymmetric_paired1d_{nr}')
        geom[f'{nr}x{nz}']={'stats':a['stats'],
          'midplane_differences':{k:comparison(a[k],pair[k],tim,rad) for k in FIELDS},
          'full_volume_mean_T_3h':float(a['average_temperature_degC'][-1]),
          'full_volume_mean_C_3h':float(a['average_moisture_dry_basis'][-1]),
          'end_center_T_3h':float(a['end_temperature_degC'][-1,0]),
          'end_center_C_3h':float(a['end_moisture_dry_basis'][-1,0])}
    for (nra,nza),(nrb,nzb) in [((20,40),(20,80)),((20,80),(40,80))]:
        if f'{nrb}x{nzb}' not in geom:continue
        ga=readsol(v,f'axisymmetric_{nra}_{nza}');gb=readsol(v,f'axisymmetric_{nrb}_{nzb}')
        pa=readsol(v,f'axisymmetric_paired1d_{nra}');pb=readsol(v,f'axisymmetric_paired1d_{nrb}')
        geom[f'effect_{nra}x{nza}_vs_{nrb}x{nzb}']={k:comparison(ga[k]-pa[k],gb[k]-pb[k],tim,rad) for k in FIELDS}
    geom['scope']='Both Q2 nonlinear fields solved in r,z with identical end/side h; paired 1D same radial grid. Geometric scenario, not experiment or strict 4-decimal guarantee.'
    report['geometry']=geom
    (v/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'delivery_summary.json').write_text(json.dumps({k:report[k] for k in ('model','output_scope','method','total_values','precision','values_3h','field_checks')},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report['values_3h'],ensure_ascii=False,indent=2),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();finalize(a.input,a.out)
