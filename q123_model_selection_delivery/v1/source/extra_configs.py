from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
base=json.loads((root/'configs/q23_F01_r96_z0_v2.json').read_text())
items=[]
for ceq in [.05,.12,.20]:
 for dim in [1,2]:
  c=dict(base,ceq=ceq,nr=48 if dim==1 else 32,nz=0 if dim==1 else 48,rtol=4e-8,atol_T=4e-9,atol_C=4e-11)
  n=f'q23_sensitivity_eq{ceq:.3f}_{dim}D';items.append(n);(root/'configs'/f'{n}.json').write_text(json.dumps(c,indent=2))
for latent in [False,True]:
 c=dict(base,nr=192,latent=latent);n=f'q23_F0{int(latent)}_r192';items.append(n);(root/'configs'/f'{n}.json').write_text(json.dumps(c,indent=2))
c=dict(base,method='Radau',rtol=5e-10,atol_T=5e-11,atol_C=5e-13,max_step_early=10.,max_step_late=300.)
n='q23_F01_r96_Radau';items.append(n);(root/'configs'/f'{n}.json').write_text(json.dumps(c,indent=2))
# Two-dimensional zero-end exchange limit, a real PDE reduction test.
c=dict(base,nr=24,nz=32,end_factor=0.,horizon=10800.)
n='q23_limit_closed_ends_2D';items.append(n);(root/'configs'/f'{n}.json').write_text(json.dumps(c,indent=2))
c=dict(c,nz=0);n='q23_limit_closed_ends_1D';items.append(n);(root/'configs'/f'{n}.json').write_text(json.dumps(c,indent=2))
# External film approximation, not an empirical confidence interval.
for mult in [.5,2.]:
 c=dict(base,nr=48,gas_multiplier=mult);n=f'q23_gas{mult:g}_1D';items.append(n);(root/'configs'/f'{n}.json').write_text(json.dumps(c,indent=2))
(root/'validation/extra_config_names.json').write_text(json.dumps(items,indent=2))
print(' '.join(str(root/'configs'/f'{n}.json') for n in items))
