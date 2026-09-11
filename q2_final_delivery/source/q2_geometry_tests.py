"""Small checks of the coupled r-z operator, independent of end-effect conclusions."""
import json
from pathlib import Path
import numpy as np
from q2_core import solve_fv
from q2_axisymmetric import AxisymmetricFV,solve_axisymmetric

def geometry_tests(env,out):
    op=AxisymmetricFV(20,8);r,z=np.meshgrid(op.r/op.p.R,op.z/(op.p.L/2))
    y=np.stack([35+3*r*r+.2*z*z,2.5-.7*r*r-.2*z*z],axis=-1).ravel()
    v=np.random.default_rng(7361).normal(size=y.size);v[1::2]*=.1;eps=1e-5
    exact=op.evaluate(1000,y,env,True)@v
    fd=(op.evaluate(1000,y+eps*v,env)-op.evaluate(1000,y-eps*v,env))/(2*eps)
    rel=float(np.max(abs(fd-exact))/np.max(abs(exact)))
    a=solve_axisymmetric(env,20,8,end=600,end_transfer=False,rtol=1e-10,atol=1e-12)
    b=solve_fv(env,n=20,end=600,rtol=1e-10,atol_T=1e-12,atol_C=1e-12,max_step=30.)
    differences={k:float(np.max(abs(a[k]-b[k]))) for k in ('temperature_degC','moisture_dry_basis')}
    report={'jacobian_central_difference_relative':rel,'no_end_flux_2D_vs_1D_600s':differences,
      'passed':rel<1e-7 and differences['temperature_degC']<3e-7 and differences['moisture_dry_basis']<3e-8}
    assert report['passed'],report
    (Path(out)/'geometry_unit_tests.json').write_text(json.dumps(report,indent=2))
    return report
