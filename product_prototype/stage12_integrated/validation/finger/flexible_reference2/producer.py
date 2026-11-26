"""Independent terminal-contact Green-function/FEM reference, not full surface contact.
Two independent clamped beams, finite-clearance frictionless moving terminal guide.
Acceptance is declared before execution; typical moduli are conditional inputs.
"""
import json, hashlib, shutil, sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.linalg import block_diag
from baseline_registry import ROOT, dump, ref
sys.path.insert(0,str(ROOT.parent/'stage2_load_transfer/scripts'))
from sliding_pet_contact import beam, shape
from finger_structure import E_RAIL,E_PET,width
LR=.088; LP=.0862
CRITERIA=dict(reference_relative_max=1e-5,force_N_max=1e-8,moment_Nm_max=1e-9,
              gap_m_min=-1e-12,complementarity_J_max=1e-12,energy_relative_max=1e-8)
def eis():return (lambda s:2*E_RAIL*.003*.0002**3/12,lambda s:E_PET*width(s)*.0003**3/12)
def reference(force):
    er,ep=eis();d=LP-LR
    # Rail guide displacement at LP is y(LR)+d*theta(LR).
    rr=quad(lambda s:(LP-s)**2/er(s),0,LR,epsabs=1e-13)[0]
    rf=quad(lambda s:(LP-s)*(LR-s)/er(s),0,LR,epsabs=1e-13)[0]
    pp=quad(lambda s:(LP-s)**2/ep(s),0,LP,epsabs=1e-13)[0]
    free=-force*rf;target=np.clip(free,-.0001,.0002)
    signed=(target-free)/(rr+pp)
    rail=quad(lambda s:(LR-s)*(force*(LR-s)-signed*(LP-s))/er(s),0,LR,epsabs=1e-13)[0]
    pet=signed*pp
    return dict(rail_tip_m=rail,PET_tip_m=pet,relative_m=target,signed_contact_N=signed)
def solve(n,force):
    er,ep=eis();m=2*(n+1);K=block_diag(beam(n,LR,er),beam(n,LP,ep));f=np.zeros(2*m);f[m-2]=force
    a=np.r_[np.zeros(m),shape(n,LP,LP)];a[m-2]=-1;a[m-1]=LR-LP
    free=np.r_[np.arange(2,m),np.arange(m+2,2*m)]
    k=K[np.ix_(free,free)];af=a[free];u0=np.linalg.solve(k,f[free]);response=np.linalg.solve(k,af)
    g0=float(af@u0);target=float(np.clip(g0,-.0001,.0002));signed=(target-g0)/float(af@response)
    u=np.zeros(2*m);u[free]=u0+signed*response
    A=np.array([a,-a]);b=np.array([-.0001,-.0002]);lam=np.array([max(signed,0),max(-signed,0)])
    gap=A@u-b;res=K@u-f-A.T@lam
    eq=res[free].copy();eq[free%2==1]/=LR
    U=float(.5*u@K@u);work=float(f@u);contact_work=float(lam@b)
    energy=abs(2*U-work-contact_work)/max(abs(2*U),1e-30)
    force_err=abs(res[0]+res[m]+force)
    moment_err=abs(res[1]+res[m+1]+force*LR)
    expected=reference(force);errors={key:abs(float(value)/expected[key]-1) for key,value in [('rail_tip_m',u[m-2]),('PET_tip_m',u[-2]),('signed_contact_N',signed)] if abs(expected[key])>1e-20}
    checks=dict(reference=max(errors.values(),default=0)<CRITERIA['reference_relative_max'],force=np.linalg.norm(eq)<CRITERIA['force_N_max'] and force_err<CRITERIA['force_N_max'],moment=moment_err<CRITERIA['moment_Nm_max'],gap=min(gap)>=CRITERIA['gap_m_min'],complementarity=max(abs(lam*gap))<CRITERIA['complementarity_J_max'],energy=energy<CRITERIA['energy_relative_max'])
    checks={key:bool(value) for key,value in checks.items()}
    return dict(n=n,force_N=force,status='PASS' if all(checks.values()) else 'FAIL',checks=checks,reference=expected,reference_errors=errors,rail_tip_m=float(u[m-2]),PET_tip_m=float(u[-2]),relative_m=float(a@u),normal_multipliers_N=lam.tolist(),gap_m=gap.tolist(),force_equivalent_N=float(np.linalg.norm(eq)),root_force_balance_N=float(force_err),root_moment_balance_Nm=float(moment_err),stored_energy_J=U,external_final_load_dot_displacement_J=work,contact_final_load_dot_displacement_J=contact_work,energy_relative_error=energy,naive_half_external_energy_relative_error=abs(2*U-work)/max(abs(2*U),1e-30),rail_q=u[:m].tolist(),PET_q=u[m:].tolist())
def main():
    tag=sys.argv[1];out=ROOT/'validation/finger'/tag
    if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP present')
    out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    dependencies=[Path(__file__),ROOT.parent/'stage2_load_transfer/scripts/sliding_pet_contact.py',ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py',ROOT.parent/'stage2_load_transfer/models/materials/evidence.json',ROOT/'cad/exports/revAD_funnel1/summary.json',ROOT/'validation/finger/owner_states2/summary.json']
    dump(out/'inputs.json',dict(criteria=CRITERIA,inputs=[ref(p) for p in dependencies],conditional_material=dict(rail_E_Pa=E_RAIL,PET_E_Pa=E_PET),lengths_m=dict(rail=LR,PET=LP)))
    rows=[solve(n,f) for f in (-.001,.00001,.001) for n in (8,16,32)]
    controls=dict(both_contact_sides_exercised=any(r['normal_multipliers_N'][0]>0 for r in rows) and any(r['normal_multipliers_N'][1]>0 for r in rows),open_gap_exercised=any(sum(r['normal_multipliers_N'])==0 for r in rows),omitted_clearance_work_rejected=any(r['naive_half_external_energy_relative_error']>.01 for r in rows))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) and all(controls.values()) else 'FAIL',scope='CONDITIONAL SMALL-LOAD MOVING TERMINAL GUIDE REFERENCE ONLY',criteria=CRITERIA,rows=rows,controls=controls,inputs=ref(out/'inputs.json'),whole_system_release=False,limitations=['No distributed interface contact: terminal-only reference may cross actual Rail surface','No actual deformed BRep clearance qualification','No finite rotation, axial strain, friction, material certification or strength','RevAD candidate remains unadopted; RevAA release unchanged'])
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],controls=controls,rows=[{k:r[k] for k in ('n','force_N','status','reference_errors','energy_relative_error')} for r in rows]),indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 2)
if __name__=='__main__':main()
