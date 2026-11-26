"""Projected small-deflection beam FEM vs independent quadrature.

Unbonded layers can slip internally but are axially locked at BOTH clamps.
Eliminating common end extension gives K_end=sum(k_i*(d_i-dbar)^2).
Free-slip-at-terminal is a control, not the current mechanical definition.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.linalg import solve
ROOT=Path(__file__).resolve().parents[1]
L=.088
E_PET=507000*6894.757293168 # supplier Mylar A typical; NOT selected actual lot
E_RAIL=193e9 # supplier annealed typical, full-hard actual value unverified
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def width(s):return .024-.12*(s+.007)
def definition(tp,tr):
    # Projected width/length ignores 0.06 rail edge slope (not 3D qualification).
    ea=[lambda s:E_PET*width(s)*tp,lambda s:E_RAIL*.003*tr,lambda s:E_RAIL*.003*tr]
    d=np.array([tp/2,tp+tr/2,tp+tr/2])
    axial_k=np.array([1/quad(lambda s:1/f(s),0,L,epsabs=1e-14)[0] for f in ea])
    neutral=float(axial_k@d/axial_k.sum())
    krot=float(axial_k@(d-neutral)**2)
    def EI(s):return E_PET*width(s)*tp**3/12+2*E_RAIL*.003*tr**3/12
    return EI,krot,axial_k,d,neutral
def fem(n,EI,krot,force):
    K=np.zeros((2*(n+1),2*(n+1)));h=L/n;gx,gw=np.polynomial.legendre.leggauss(4)
    for j in range(n):
        ke=np.zeros((4,4))
        for x,w in zip((gx+1)/2,gw/2):
            B=np.array([(-6+12*x)/h**2,(-4+6*x)/h,(6-12*x)/h**2,(-2+6*x)/h])
            ke+=w*h*EI((j+x)*h)*np.outer(B,B)
        ids=np.arange(2*j,2*j+4);K[np.ix_(ids,ids)]+=ke
    K[-1,-1]+=krot;f=np.zeros(len(K));f[-2]=force
    u=np.zeros_like(f);u[2:]=solve(K[2:,2:],f[2:],assume_a='pos')
    reactions=K@u-f;energy=.5*float(u@K@u)
    # Force and moment balance against applied load plus spring internal couple.
    force_error=abs(reactions[0]+force)
    moment_error=abs(reactions[1]+force*L-krot*u[-1])
    return dict(n=n,tip_m=float(u[-2]),rotation_rad=float(u[-1]),energy_J=energy,
        external_work_J=.5*force*float(u[-2]),root_force_N=float(reactions[0]),root_moment_Nm=float(reactions[1]),
        balance_force_error_N=force_error,balance_moment_error_Nm=moment_error,
        energy_relative_error=abs(energy-.5*force*u[-2])/energy)
def reference(EI,krot,force):
    a=quad(lambda s:(L-s)/EI(s),0,L,epsabs=1e-12)[0]
    b=quad(lambda s:1/EI(s),0,L,epsabs=1e-12)[0]
    c=quad(lambda s:(L-s)**2/EI(s),0,L,epsabs=1e-12)[0]
    theta=force*a/(1+krot*b)
    return force*c-krot*theta*a,theta
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
    out=ROOT/'validation/finger'/args.tag;out.mkdir(parents=True,exist_ok=False)
    allcases=[]
    for tp,tr in ((.00030,.00020),(.00028,.00019),(.00032,.00021)):
        EI,krot,k,d,dbar=definition(tp,tr)
        cases=[]
        for name,kr in [('terminal_free_slip_control',0.),('both_clamps_axially_locked',krot)]:
            force=.001;y,theta=reference(EI,kr,force)
            refinements=[fem(n,EI,kr,force) for n in (8,16,32,64)]
            err=max(abs(x['tip_m']/y-1) for x in refinements)
            refine=abs(refinements[-1]['tip_m']/refinements[-2]['tip_m']-1)
            passed=err<.01 and refine<.01 and all(x['energy_relative_error']<1e-8 and x['balance_force_error_N']<1e-8 and x['balance_moment_error_Nm']<1e-8 for x in refinements)
            cases.append(dict(boundary=name,status='PASS' if passed else 'FAIL',force_N=force,
                independent_tip_m=y,independent_rotation_rad=theta,reference_error_relative=err,
                refinement_error_relative=refine,rotational_axial_coupling_Nm_rad=kr,refinements=refinements))
        allcases.append(dict(PET_thickness_m=tp,rail_thickness_m=tr,EI_root_Nm2=EI(0),EI_tip_Nm2=EI(L),
            axial_stiffness_N_m=k.tolist(),layer_centroids_m=d.tolist(),end_neutral_m=dbar,
            clamped_tip_compliance_ratio=cases[1]['independent_tip_m']/cases[0]['independent_tip_m'],cases=cases))
    result=dict(status='PASS' if all(c['status']=='PASS' for x in allcases for c in x['cases']) else 'FAIL',
        scope='SMALL-DEFLECTION PROJECTED BEAM / BOUNDARY SENSITIVITY ONLY',case='revAA_heel_relief2',
        source_SHA256=sha(Path(__file__)),material_evidence_SHA256=sha(ROOT/'models/materials/evidence.json'),
        CAD_integrals_SHA256=sha(ROOT/'models/geometry/revAA_extract2/summary.json'),
        assumed_PET_E_Pa=E_PET,assumed_rail_E_Pa=E_RAIL,cases=allcases,
        exclusions=['large bending','tendon compression and postbuckling','torsion','3D oblique rail effect','local clamp/contact/slip/pullout','fatigue','actual material certification'],
        actual_Finger_strength_status='NOT QUALIFIED',command='python scripts/finger_structure.py --tag '+args.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],scope=result['scope'],nominal=allcases[0]),indent=2))
if __name__=='__main__':main()
