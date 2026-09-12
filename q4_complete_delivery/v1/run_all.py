"""Reproduce into a NEW directory, leaving every frozen delivery untouched.

Default: Q4 solution, numeric checks, mechanism/interpolation comparisons,
strict endpoint, CSV/table/Excel input. --geometry and --closeout additionally
run the targeted tasks; --excel requires the documented artifact-tool runtime.
The component commands were run for this delivery; this orchestration wrapper
does not represent another independent cold-start validation.
"""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--geometry',action='store_true');p.add_argument('--closeout',action='store_true');p.add_argument('--excel',action='store_true')
    a=p.parse_args();out=a.out.resolve()
    if out.exists():raise FileExistsError('Choose a new output directory; no existing result is overwritten')
    out.mkdir(parents=True);shutil.copytree(ROOT/'inputs',out/'inputs')
    for sub in ['output','validation/geometry','figures','q123_closeout/output']:(out/sub).mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    calls=[]
    def execute(script,args,log):
        cmd=[sys.executable,str(ROOT/script),*[str(x) for x in args]];calls.append(cmd)
        print('Running',Path(script).name,flush=True)
        with (out/log).open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
    for n,label,method,rtol,step,kind,audit in [
        (80,'validation/spectral80','Radau',2e-10,180,'linear',False),
        (120,'output/main','Radau',2e-11,90,'linear',True),
        (120,'validation/time120_bdf','BDF',1e-11,45,'linear',False),
        (80,'validation/fixed80','Radau',2e-10,180,'fixed',False),
        (80,'validation/pchip80','Radau',2e-10,180,'pchip',False)]:
        args=['--n',n,'--out',out/label,'--method',method,'--rtol',rtol,'--max-step',step,'--kind',kind]
        if audit:args+=['--audit']
        execute('source/run_q4.py',args,label+'.log')
    for n,rtol,step in [(40,2e-9,240),(80,2e-9,240),(160,2e-9,240),(320,2e-9,240),(320,2e-10,120),(640,2e-10,120),(640,2e-11,60)]:
        execute('source/geometry_solver.py',['--case','q4','--nr',n,'--rtol',rtol,'--max-step',step,'--out-dir',out/'validation/geometry','--input-dir',out/'inputs'],f'validation/geometry/independent_{n}_{rtol}.log')
    execute('source/finalize_q4.py',['--base',out],'validation/finalize.log')
    execute('source/check_numerics.py',['--base',out],'validation/check_numerics.log')
    execute('source/make_figures.py',['--base',out,'--font',out/'inputs/fonts/NotoSansCJKsc-Regular.otf'],'validation/figures.log')
    if a.geometry:
        for case,n,z in [('q1',80,0),('q1',80,128),('q23',80,0),('q23',80,128),('q23',80,256),('q4',40,64),('q4',40,128),('q4',80,128)]:
            execute('source/geometry_solver.py',['--case',case,'--nr',n,'--nz',z,'--flux','harmonic' if case=='q1' else 'integral','--out-dir',out/'validation/geometry','--input-dir',out/'inputs'],f'validation/geometry/{case}_{n}_{z}.log')
    if a.closeout:
        execute('q123_closeout/source/solve_unified_q23.py',['--n',80,'--method','Radau','--rtol',2e-13,'--max-step',30,'--input',out/'inputs/attachment1.xlsx','--out',out/'q123_closeout/output/q23_unified'],'q123_closeout/output/q23_unified.log')
    if a.excel:
        cmd=['--root',ROOT.parents[1],'--out-dir',out,'--q4-json',out/'output/result4_data.json','--font','Noto Sans CJK SC']
        if a.closeout:cmd+=['--q2-npz',out/'q123_closeout/output/q23_unified.npz','--workers',1]
        execute('source/package_workbooks.py',cmd,'validation/workbook_build.log')
    (out/'run_commands.json').write_text(json.dumps({'commands':calls,'geometry_included':a.geometry,'closeout_included':a.closeout,'excel_included':a.excel},ensure_ascii=False,indent=2))
    print('Completed:',out)
if __name__=='__main__':main()
