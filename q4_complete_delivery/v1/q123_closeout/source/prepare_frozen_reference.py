"""Assemble historical 160-order samples and its existing execution endpoint.
This only reorganizes already computed independent-reference arrays; it solves
nothing and must never be described as a new reference simulation.
"""
from pathlib import Path
import argparse,numpy as np
p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parents[1]/'inputs/historical_baseline');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
if a.out.exists():raise FileExistsError(a.out)
f=a.inputs/'q3_refinement_delivery/validation/numeric'
x=np.load(f/'reference160_bdf_historical.npz');y=np.load(f/'reference160_official_endpoint_historical.npz')
t=np.r_[x['time_s'][:-1],float(y['time_s'])];v=np.concatenate([x['sample_TC'][:-1],y['profile_TC'][None]],axis=0)
assert np.all(np.diff(t)>0) and t[-1]==206906.76
np.savez_compressed(a.out,time_s=t,profile_TC=v,radius_cm=np.linspace(0,2,21))
