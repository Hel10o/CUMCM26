"""Read-only comparisons; every number comes from unrounded saved solutions.
No files in output case directories are changed. This file writes analysis/.
"""
from pathlib import Path
import json,sys
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'analysis';DEST.mkdir(exist_ok=True)
RP=np.array([0,.005,.01,.015,.02])
def load(name):
 p=ROOT/'output'/name
 z=np.load(p/'solution.npz',allow_pickle=False);data={k:z[k] for k in ['time','r','z','midplane_T','midplane_C','metric_names','metrics']};z.close()
 return dict(name=name,data=data,result=json.loads((p/'result.json').read_text()),ledger=json.loads((p/'ledger.json').read_text()),config=json.loads((p/'provenance.json').read_text())['config'])
def metrics(c,t):
 d=c['data'];i=np.argmin(abs(d['time']-t));assert abs(d['time'][i]-t)<1e-5
 return dict(zip(d['metric_names'],d['metrics'][i]))
def profile(c,t,col,r=RP):
 d=c['data'];i=np.argmin(abs(d['time']-t));assert abs(d['time'][i]-t)<1e-5
 return PchipInterpolator(d['r'],d['midplane_'+col][i])(r)
def scalar(c,t):
 d=metrics(c,t);q=next(v for v in c['ledger'] if abs(v['t']-t)<1e-5);v=np.array(q['cumulative5']);loss=c['result']['initial']['Mwater']-d['Mwater']
 out={k:float(d[k]) for k in ['coreT','sideT','end_centerT','cornerT','coreC','sideC','end_centerC','cornerC','meanT','meanC','maxC','minT','max_r','max_z']}
 out.update(loss_g=loss*1000,side_loss_g=v[0]*1000,end_loss_g=v[4]*1000,convective_kJ=(v[1]+v[5])/1000,latent_kJ=(v[2]+v[6])/1000,sensible_out_kJ=(v[3]+v[7])/1000,stored_kJ=d['enthalpy']/1000,side_convective_kJ=v[1]/1000,end_convective_kJ=v[5]/1000,end_latent_kJ=v[6]/1000,physical_phase_kJ=((2.501e6-2361*28)*(v[0]+v[4])-2361/4186*(v[3]+v[7]))/1000,dry_mass_g=d['Mdry']*1000)
 if c['config']['baseline']:out['physical_phase_kJ']=float('nan')
 if not c['config']['baseline']:
  # Missing phase-change energy for off cases evaluated from their OWN flux/T.
  dat=c['data'];ids=dat['time']<=t;ts=dat['time'][ids]
  # This extra metric needs surface temperatures for all faces; nodal snapshot
  # quadrature is not used to invent unresolved history. Store formal definition.
 return out

def main():
 names={1:{'B':'q1_B_r512_v2','F00':'q1_F00_r96_z0_v2','F10':'q1_F10_r96_z128_v2','F01':'q1_F01_r96_z0_v2','F11':'q1_F11_r96_z128_v2'},23:{'B':'q23_B_r512_v2','F00':'q23_F00_r96_z0_v2','F10':'q23_F10_r96_z128_retry','F01':'q23_F01_r96_z0_v2','F11':'q23_F11_r96_z128_v2'}}
 allcases={q:{g:load(n) for g,n in group.items()} for q,group in names.items()}
 tables=[];ends=[];differences=[];norms=[];event=[]
 for q,groups in allcases.items():
  times=[100,300,600,900,1200,1500,1800] if q==1 else [1800,3600,5400,7200,9000,10800]
  stage=1800 if q==1 else 10800
  for g,c in groups.items():
   for t in times:
    pp={v:profile(c,t,v) for v in ['T','C']}
    for j,r in enumerate(RP):tables.append(dict(question=1 if q==1 else 2,group=g,case=c['name'],time_s=t,r_m=r,T=pp['T'][j],C=pp['C'][j]))
   e=scalar(c,stage);ends.append(dict(question=1 if q==1 else 2,group=g,case=c['name'],time_s=stage,**e))
   if q==23:event.append(dict(group=g,case=c['name'],equal_s=c['result']['event_equal_s'],equal_h=c['result']['event_equal_s']/3600,execution_s=c['result']['execution_s'],final_maxC=c['result']['final']['maxC']))
  vals={g:scalar(c,stage) for g,c in groups.items()}
  operators={'B_to_F00':{'F00':1,'B':-1},'G0':{'F10':1,'F00':-1},'G1':{'F11':1,'F01':-1},'L1':{'F01':1,'F00':-1},'L2':{'F11':1,'F10':-1},'I':{'F11':1,'F10':-1,'F01':-1,'F00':1}}
  for op,coef in operators.items():
   for k in vals['F00']:
    differences.append(dict(question=1 if q==1 else 2,time_s=stage,contrast=op,metric=k,value=sum(v*vals[g][k] for g,v in coef.items())))
   # Signed fields are aligned first; L-infinity taken only afterwards.
   tcommon=groups['F00']['data']['time'];tcommon=tcommon[tcommon<=stage]
   for field in ['T','C']:
    delta=np.zeros((len(tcommon),len(groups['F00']['data']['r'])))
    rr=groups['F00']['data']['r']
    for g,v in coef.items():
     d=groups[g]['data'];ix=np.searchsorted(d['time'],tcommon);assert np.max(abs(d['time'][ix]-tcommon))<1e-6
     pp=PchipInterpolator(d['r'],d['midplane_'+field][ix],axis=1)(rr)
     delta+=v*pp
    loc=np.unravel_index(np.abs(delta).argmax(),delta.shape)
    norms.append(dict(question=1 if q==1 else 2,contrast=op,field=field,max_abs=float(abs(delta).max()),signed_at_max=float(delta[loc]),time_s=float(tcommon[loc[0]]),r_m=float(rr[loc[1]])))
  # Q3 every 6h profiles use the same sample axis; all groups to their own event.
  if q==23:
   for g,c in groups.items():
    for t in np.arange(21600,c['data']['time'][-1]+1e-6,21600):
     for j,r in enumerate(RP):tables.append(dict(question=3,group=g,case=c['name'],time_s=t,r_m=r,T=profile(c,t,'T')[j],C=profile(c,t,'C')[j]))
 pd.DataFrame(tables).to_csv(DEST/'sampled_fields.csv',index=False,float_format='%.17g')
 pd.DataFrame(ends).to_csv(DEST/'stage_summary.csv',index=False,float_format='%.17g')
 pd.DataFrame(differences).to_csv(DEST/'factorial_contrasts.csv',index=False,float_format='%.17g')
 pd.DataFrame(norms).to_csv(DEST/'midplane_difference_norms.csv',index=False,float_format='%.17g')
 pd.DataFrame(event).to_csv(DEST/'event_times.csv',index=False,float_format='%.17g')
 # Paired space refinement effects, no comparison to unrelated fine radial solve.
 conv=[]
 for q in [1,23]:
  for nr,nz in [(24,32),(48,64),(96,128)]:
   for latent in [0,1]:
    if q==1 and nr==24:continue # rejected wrong-D pilot not used
    n1=(f'q{q}_F0{latent}_r{nr}_z0'+('_v2' if nr>=48 else ''))
    n2=(f'q{q}_F1{latent}_r{nr}_z{nz}'+('_v2' if nr>=48 else ''))
    if q==23 and nr==96 and latent==0:n2='q23_F10_r96_z128_retry'
    if not (ROOT/'output'/n1/'result.json').exists() or not (ROOT/'output'/n2/'result.json').exists():continue
    a,b=load(n1),load(n2);t=1800 if q==1 else 10800
    aa,bb=scalar(a,t),scalar(b,t)
    row=dict(question=q,nr=nr,nz=nz,latent=latent,paired_mid_T_core=bb['coreT']-aa['coreT'],paired_mid_C_core=bb['coreC']-aa['coreC'],paired_loss_g=bb['loss_g']-aa['loss_g'],paired_heat_kJ=bb['convective_kJ']-aa['convective_kJ'])
    if q==23:row.update(equal_1D=a['result']['event_equal_s'],equal_2D=b['result']['event_equal_s'],end_effect_s=b['result']['event_equal_s']-a['result']['event_equal_s'])
    conv.append(row)
 pd.DataFrame(conv).to_csv(DEST/'paired_convergence.csv',index=False,float_format='%.17g')
 valid=[]
 for p in (ROOT/'output').glob('*/result.json'):
  d=json.loads(p.read_text());
  if 'mass_residual_rel' not in d:continue
  if '_v2' not in p.parent.name and not any(s in p.parent.name for s in ['sensitivity','retry','limit','gas','r192','Radau']):continue
  conf=json.loads((p.parent/'provenance.json').read_text())['config']
  valid.append(dict(case=p.parent.name,baseline=conf['baseline'],mass_relative=d['mass_residual_rel'],energy_relative=d['energy_residual_rel'],mass_posthoc_relative=d['mass_posthoc_rel'],energy_posthoc_relative=d['energy_posthoc_rel'],mass_absolute_kg=d['mass_residual_gauss5'],energy_absolute_J=d['energy_residual_gauss5'],elapsed_s=d['elapsed_s'],run_complete=d['run_complete']))
 pd.DataFrame(valid).to_csv(DEST/'conservation_runs.csv',index=False,float_format='%.17g')
 sens=[]
 for eq in [.05,.12,.20]:
  for dim,suffix in [(1,'paired1D'),(1,'1D'),(2,'2D')]:
   n=f'q23_sensitivity_eq{eq:.3f}_{suffix}'+('_eventchecked' if eq==.20 else '');
   if not (ROOT/'output'/n/'result.json').exists():continue
   c=load(n);d=c['result'];v=scalar(c,10800)
   sens.append(dict(case=n,ceq=eq,dimension=dim,nr=c['config']['nr'],nz=c['config']['nz'],status=d['status'],equal_s=d['event_equal_s'],equal_h=d['event_equal_s']/3600 if d['event_equal_s'] else None,final_time_s=d['t_final'],final_maxC=d['final']['maxC'],Tcore_3h=v['coreT'],Tside_3h=v['sideT'],Ccore_3h=v['coreC'],Cside_3h=v['sideC'],loss_3h_g=v['loss_g']))
 pd.DataFrame(sens).to_csv(DEST/'equilibrium_sensitivity.csv',index=False,float_format='%.17g')
 print(pd.DataFrame(ends).to_string(index=False));print(pd.DataFrame(event).to_string(index=False));print(pd.DataFrame(norms).to_string(index=False))
if __name__=='__main__':main()
