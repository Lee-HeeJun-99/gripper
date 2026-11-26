"""Declared dimension-tolerance corners with FIXED assumed moduli.
These are not bounds on unknown material stiffness, friction or clamp slip.
"""
import argparse,itertools,json,shutil
from pathlib import Path
import numpy as np
from scipy.optimize import root
from nonlinear_finger import model
from finger_structure import ROOT,L,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/worst_case'/a.tag;out.mkdir(parents=True,exist_ok=False)
    for name in ('worst_case.py','nonlinear_finger.py','finger_structure.py'):
        shutil.copyfile(Path(__file__).with_name(name),out/name)
    base=json.loads((ROOT/'validation/integrated/stroke1/summary.json').read_text())
    rows=[]
    for tp,tr,dia,length_error,wire_k in itertools.product((.00028,.00032),(.00019,.00021),(.00048,.00052),(-.00025,.00025),(1000.,10000.)):
        fn,H=model(32,True,tp,tr,.01093+dia/2);l0=fn(np.zeros(32),0.)[3]
        stroke=.01691-length_error
        q=np.linspace(0,.8,33)[1:];initial=np.r_[q,.8]
        def residual(v):
            _,g,_,length,_=fn(v[:-1],v[-1])
            return np.r_[g/L,1000*(l0-length+v[-1]/wire_k-stroke)]
        result=root(residual,initial,tol=1e-10);v=result.x
        energy,g,p,length,end=fn(v[:-1],v[-1]);res=float(np.linalg.norm(g)/L);gap=abs(l0-length+v[-1]/wire_k-stroke)
        rows.append(dict(PET_thickness_m=tp,rail_thickness_m=tr,wire_diameter_m=dia,length_error_m=length_error,
            assumed_wire_k_N_m=wire_k,effective_stroke_m=stroke,tension_N=float(v[-1]),rotation_deg=float(np.degrees(v[-2])),
            pivot_m=p.tolist(),equilibrium_residual_N=res,stroke_residual_m=gap,
            status='PASS' if res<1e-6 and gap<1e-9 and v[-1]>=0 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',
        scope='CONDITIONAL TOLERANCE-CORNER SOLUTIONS, NOT ALL-PHYSICS WORST-CASE CAPACITY',rows=rows,
        tension_range_N=[min(r['tension_N'] for r in rows),max(r['tension_N'] for r in rows)],
        rotation_range_deg=[min(r['rotation_deg'] for r in rows),max(r['rotation_deg'] for r in rows)],
        material_and_wire_stiffness_basis='Same explicit assumed parameters as stroke1; NO certified property interval',
        source_SHA256={name:sha(Path(__file__).with_name(name)) for name in ('worst_case.py','nonlinear_finger.py','finger_structure.py')},
        next='Validate nonlinear shape vs actual mechanics; clamp slip, material bounds and motor running curve still required',
        command='python scripts/worst_case.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
