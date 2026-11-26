"""Recover clamp self-equilibrating loads and section strain from reduced model.
No PET compressive/buckling/retention approval. Actual load-path screen only.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from scipy.optimize import root
from nonlinear_finger import model
from finger_structure import ROOT,L,definition,E_PET,E_RAIL,width,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False)
    for name in ('laminate_end_loads.py','nonlinear_finger.py','finger_structure.py'):
        shutil.copyfile(Path(__file__).with_name(name),out/name)
    rows=[]
    for locked in (True,False):
        for n in (16,32,64):
            fn,H=model(n,locked);l0=fn(np.zeros(n),0.)[3];stroke=.01691;wireK=10000.
            def residual(v):
                _,g,_,length,_=fn(v[:-1],v[-1])
                return np.r_[g/L,1000*(l0-length+v[-1]/wireK-stroke)]
            answer=root(residual,np.r_[np.linspace(0,.8,n+1)[1:],.7],tol=1e-10)
            q=answer.x[:-1];t=float(answer.x[-1]);kappa=np.diff(np.r_[0.,q])/(L/n)
            EI,kr,k,d,neutral=definition(.00030,.00020)
            axial=k*(d-neutral)*q[-1] if locked else np.zeros(3)
            span=(np.arange(n)+.5)*L/n;petA=width(span)*.00030
            # Worst-case whole external tendon axial force allocated to one
            # layer, in addition to self-equilibrating end forces. Not a
            # resolved 3D contact stress distribution.
            pet_strain=np.abs(axial[0]/(E_PET*petA))+.00015*abs(kappa)+abs(t)/(E_PET*petA)
            rail_strain=max(abs(axial[1]),abs(axial[2]))/(E_RAIL*.003*.00020)+.00010*abs(kappa)+abs(t)/(E_RAIL*.003*.00020)
            gap=abs(residual(answer.x)[-1]/1000);eq=np.linalg.norm(residual(answer.x)[:-1])
            rows.append(dict(locked=locked,n=n,stroke_m=stroke,assumed_wireK_N_m=wireK,tension_N=t,rotation_deg=float(np.degrees(q[-1])),
                layer_axial_forces_N=axial.tolist(),axial_force_sum_N=float(axial.sum()),
                maximum_curvature_1_m=float(max(abs(kappa))),max_PET_section_strain=float(max(pet_strain)),
                max_rail_section_strain=float(max(rail_strain)),conditional_rail_static_FoS=float(965e6/(E_RAIL*max(rail_strain))),
                required_total_clamp_normal_N_at_assumed_mu_0_1=float(max(abs(axial))/.1),
                PET_end_travel_required_if_released_m=float(abs(d[1]-d[0])*abs(q[-1])),
                equilibrium_residual_N=float(eq),stroke_residual_m=gap,
                reduced_model_solved=bool(eq<1e-6 and gap<1e-9),
                reversible_PET_allowable=None,actual_layer_loads_qualified=False))
    convergence=[]
    for locked in (True,False):
        selected=[r for r in rows if r['locked']==locked];lo,hi=selected[-2:]
        err=abs(lo['max_rail_section_strain']/hi['max_rail_section_strain']-1)
        convergence.append(dict(locked=locked,rail_peak_strain_refinement_relative=err,status='PASS' if err<.01 else 'FAIL'))
    result=dict(status='PASS' if all(r['reduced_model_solved'] for r in rows) and all(c['status']=='PASS' for c in convergence) else 'FAIL',
        scope='REDUCED LAMINATE END-LOAD / STRAIN SCREEN, NOT CLAMP OR FINGER STRENGTH APPROVAL',
        rows=rows,convergence=convergence,source_SHA256={name:sha(Path(__file__).with_name(name)) for name in ('laminate_end_loads.py','nonlinear_finger.py','finger_structure.py')},
        next='Verify finite clamp contact/slip and PET local wrinkling before choosing locked or axially floating PET termination',
        command='python scripts/laminate_end_loads.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
