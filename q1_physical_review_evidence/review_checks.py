#!/usr/bin/env python3
"""Read-only physical-model audit. All newly generated files go to --out.
No import of the production solver; no writes to any input workbook or NPZ.
Radiation is a conditional scenario: black isothermal enclosure Tw=Tair,
unit view factor, no contact heat and no latent heat; NOT a revised Q1 answer.
Humidity diagnostics additionally assume C_environment = kg vapour/kg dry air
and p=101.325 kPa. Neither assumption is specified unambiguously by the problem.
References: ASHRAE Handbook ch.1 humidity ratio; FAO56 eq.11 saturation pressure;
FAO56 Annex3 latent heat; Stefan-Boltzmann surface-to-enclosure exchange.
"""
from pathlib import Path
import argparse, json, hashlib, zipfile, xml.etree.ElementTree as ET
import base64, struct, zlib, re, platform, time
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.sparse import diags

NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def xlsx_read(path):
    """Independent standard-library OOXML reader (no spreadsheet edits)."""
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise ValueError('XLSX CRC error')
        ss=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            for e in ET.fromstring(z.read('xl/sharedStrings.xml')):
                ss.append(''.join(t.text or '' for t in e.iter('{'+NS['s']+'}t')))
        rel={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for s in ET.fromstring(z.read('xl/workbook.xml')).find('s:sheets',NS):
            rid=s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']; target=rel[rid]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            cells={}
            for c in ET.fromstring(z.read(target)).findall('.//s:sheetData/s:row/s:c',NS):
                t=c.attrib.get('t');v=c.find('s:v',NS)
                if t=='s': value=ss[int(v.text)]
                elif t=='inlineStr': value=''.join(t.text or '' for t in c.findall('.//s:t',NS))
                elif v is None: value=None
                elif t=='str': value=v.text
                else: value=float(v.text)
                cells[c.attrib['r']]=value
            result[s.attrib['name']]=cells
    return result

def sat_kPa(t):
    # FAO56 eq. 11 (Tetens); Celsius input, kPa output.
    t=np.asarray(t); return 0.6108*np.exp(17.27*t/(t+237.3))

def dew_C(pv):
    a=np.log(pv/0.6108); return 237.3*a/(17.27-a)

def thermal(env,n,eps):
    # Node-centred annular finite volumes with endpoints present explicitly.
    R=.02; rho_cp=820.*2600.; alpha=.36/rho_cp; sigma=5.670374419e-8
    r=np.linspace(0,R,n+1); f=np.r_[0,(r[1:]+r[:-1])/2,R]
    w=np.diff(f*f)/2; dr=R/n; g=alpha*f[1:-1]/dr
    lo=g/w[1:];up=g/w[:-1];dg=np.zeros(n+1)
    dg[:-1]-=up;dg[1:]-=lo
    A=diags([lo,dg,up],[-1,0,1],format='csc')
    scale=R/(rho_cp*w[-1]); y=np.full(n+1,28.)
    times=np.arange(1801.);out=np.empty((1801,21));out[0]=28.
    mean=np.empty(1801);mean[0]=28.;oi=np.arange(21)*(n//20)
    knots=env[(env[:,0]>=0)&(env[:,0]<=1800),0]
    total_steps=0
    for a,b in zip(knots[:-1],knots[1:]):
        def ta(t):return float(np.interp(t,env[:,0],env[:,1]))
        def rhs(t,u):
            v=A@u;Tair=ta(t)
            q=25.*(u[-1]-Tair)+eps*sigma*((u[-1]+273.15)**4-(Tair+273.15)**4)
            v[-1]-=scale*q
            return v
        def jac(t,u):
            d=dg.copy(); d[-1]-=scale*(25.+4*eps*sigma*(u[-1]+273.15)**3)
            return diags([lo,d,up],[-1,0,1],format='csc')
        use=(times>a)&(times<=b)
        sol=solve_ivp(rhs,(a,b),y,method='BDF',jac=jac,rtol=2e-10,atol=2e-12,max_step=5,dense_output=True)
        if not sol.success:raise RuntimeError(sol.message)
        z=sol.sol(times[use]);out[use]=z[oi].T;mean[use]=(w@z)/w.sum()
        y=sol.y[:,-1];total_steps+=len(sol.t)-1
    return out,mean,total_steps

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--delivery',type=Path,default=Path(__file__).resolve().parent/'local_delivery/q1_delivery')
    ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'calculations')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    root=args.delivery
    files=[root/'input/附件1.xlsx',root/'source/q1_solver.py',root/'output/第一问论文正文.md',root/'output/result1.xlsx',root/'output/q1_unrounded.npz']
    hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    cells=xlsx_read(files[0]);s=cells['Sheet1']
    assert [s[f'{c}1'] for c in 'ABC']==['时间','温度','水分浓度']
    env=np.array([[s.get(f'{c}{i}') for c in 'ABC'] for i in range(2,243)],float)
    assert np.isfinite(env).all() and np.all(np.diff(env[:,0])>0)
    z=np.load(root/'output/q1_unrounded.npz');T=z['temperature_degC'];C=z['moisture_dry_basis']
    wb=xlsx_read(root/'output/result1.xlsx');checks={}
    for name,key in [('温度','temperature_degC'),('水分浓度','moisture_dry_basis')]:
        cc=wb[name];arr=np.array([[cc[f'{chr(66+j)}{i+2}'] for j in range(21)] for i in range(1800)])
        assert np.isfinite(arr).all()
        assert [cc[f'A{i+2}'] for i in range(1800)]==list(range(1,1801))
        expected=np.array([[float(f'{v:.4f}') for v in row] for row in z[key][1:]])
        checks[name]={'values':arr.size,'equal_to_rounded_npz':bool(np.array_equal(arr,expected)), 'last_center_surface':arr[-1,[0,-1]].tolist()}
    R=.02;L=.25;V=np.pi*R**2*L;As=2*np.pi*R*L;rho=820.;cp=2600.;rd=rho/(1+2.55);lam=2.45e6
    delta_C=2.55-float(z['average_C'][-1]);delta_T=float(z['average_temperature_degC'][-1])-28
    loss=rd*V*delta_C;EL=loss*lam;Es=rho*cp*V*delta_T
    alpha=.36/(rho*cp);D=7e-9*np.exp(-.89/2.55)
    frag=Path(__file__).resolve().parent/'attachment2_fragment.b64'
    b=base64.b64decode(frag.read_text());i=b.index(b'PK\x03\x04');fields=struct.unpack_from('<IHHHHHIIIHH',b,i)
    nl,el=fields[-2:];o=zlib.decompressobj(-15);st=o.decompress(b[i+30+nl+el:]).decode()
    rec=dict(re.findall(r'<c\b[^>]*r="([AB][23])"[^>]*>.*?<v>(.*?)</v>.*?</c>',st))
    R1=float(rec['B3'])/100;shrink=1-R1/R
    psych=[]
    for j in [0,30]:
        t,ta,humidity=env[j];pv=101.325*humidity/(.621945+humidity)
        psych.append({'time_s':t,'air_C':ta,'assumed_humidity_ratio':humidity,'pv_kPa':pv,'dew_C':float(dew_C(pv)), 'RH_percent':float(100*pv/sat_kPa(ta))})
    sigma=5.670374419e-8;ts=T[-1,-1];ta=env[30,1]
    hr=sigma*((ts+273.15)**2+(ta+273.15)**2)*(ts+ta+2*273.15)
    tests=json.loads((root/'output/validation/validation.json').read_text())['tests']
    lp=tests['latent_conditional']
    result={'scope':'physical audit and conditional radiation scenario, NOT a rerun of full production/validation pipeline',
      'input':{'rows':len(env),'first':env[0].tolist(),'t1800':env[30].tolist(),'finite':True,'strict_time_order':True},
      'excel_crosscheck':checks,'original_file_sha256':hashes,
      'attachment2':{'read_level':'first two original numeric rows decoded from ZIP entry prefix; not full workbook CRC', 'cells':rec,'radius_decrease_percent':100*shrink,
         'area_volume_decrease_percent_fixed_L':100*(1-(R1/R)**2),'geometric_time_scale_ratio_fixed_D':(R1/R)**2,'surface_displacement_mm':1000*(R-R1),
         'displacement_over_initial_moisture_length':(R-R1)/np.sqrt(D*1800)},
      'scales':{'alpha_m2_s':alpha,'D_initial_m2_s':D,'BiT_R':25*R/.36,'BiM_R':8e-7*R/D,'heat_diffusion_length_cm':100*np.sqrt(alpha*1800),
        'moisture_diffusion_length_cm':100*np.sqrt(D*1800),'heat_diffusion_time_s':R*R/alpha,'moisture_diffusion_time_s':R*R/D,'end_side_area':R/L},
      'latent_recalculation':{'additional_assumptions':['rho=initial wet bulk density','fixed uniform dry density','all effective loss evaporates at side','lambda=2.45 MJ/kg'],
        'rho_d_kg_m3':rd,'volume_m3':V,'side_area_m2':As,'dry_mass_kg':rd*V,'average_C_1800':float(z['average_C'][-1]),'average_T_1800':float(z['average_temperature_degC'][-1]),
        'water_loss_kg':loss,'latent_J':EL,'baseline_sensible_J':Es,'ratio':EL/Es,'mean_latent_flux_W_m2':EL/(1800*As),'initial_latent_flux_W_m2':lam*rd*8e-7*(2.55-env[0,2]),
        'water_loss_fraction_initial_wet_mass':loss/(rho*V),'rho_wet_average_1800_if_mass_consistent':rd*(1+float(z['average_C'][-1]))},
      'conditional_psychrometric':{'assumptions':['environment=kg_vapour/kg_dry_air','p=101.325 kPa','ideal-gas moist air','FAO56 Tetens saturation pressure'],
        'states':psych,'p_sat_11p9_C_kPa':float(sat_kPa(11.9)),
        'p_sat_baseline_surface_1800_kPa':float(sat_kPa(ts)), 'baseline_minimum_aw_for_evaporation_at_1800':psych[-1]['pv_kPa']/float(sat_kPa(ts))},
      'radiation_scale':{'assumptions':['Tw=Tair','epsilon=1','large black enclosure/unit view factor'],'hr_W_m2K':hr,'hr_over_hT':hr/25,
          'rad_flux_W_m2':hr*(ta-ts),'conv_flux_W_m2':25*(ta-ts)},
      'existing_latent_test_record':lp,
      'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}}
    cases={};tic=time.perf_counter()
    for n in [160,320]:
        for eps in [0.,1.]:
            values,avg,steps=thermal(env,n,eps);cases[(n,eps)]=values
            print(f'radiation n={n} epsilon={eps} last={values[-1,[0,-1]]}',flush=True)
            if n==320: np.savez_compressed(args.out/f'radiation_eps{int(eps)}_n{n}.npz',time_s=np.arange(1801),radius_cm=np.linspace(0,2,21),T=values,average_T=avg)
    delta=cases[(320,1.)]-cases[(320,0.)]
    result['radiation_scenario']={'n_intervals':320,'rtol':2e-10,'atol':2e-12,'max_step_s':5,'elapsed_s':time.perf_counter()-tic,
       'no_radiation_center_surface_1800':cases[(320,0.)][-1,[0,-1]].tolist(),'epsilon1_center_surface_1800':cases[(320,1.)][-1,[0,-1]].tolist(),
       'delta_center_surface_1800':delta[-1,[0,-1]].tolist(),'max_field_temperature_change_K':float(np.max(np.abs(delta))),
       'radiation_160_vs_320_max_K':float(np.max(np.abs(cases[(160,1.)]-cases[(320,1.)]))),
       'radiation_effect_160_vs_320_max_K':float(np.max(np.abs((cases[(160,1.)]-cases[(160,0.)])-delta))),
       'no_radiation_vs_delivered_max_K':float(np.max(np.abs(cases[(320,0.)]-T))),
       'moisture_effect_in_decoupled_baseline':'identically zero by structure; not an experimental conclusion'}
    result['original_files_unchanged']=all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(root))] for p in files)
    assert result['original_files_unchanged']
    (args.out/'physical_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['attachment2','latent_recalculation','conditional_psychrometric','radiation_scale','radiation_scenario']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
