"""RevAD separate-DOF linear distributed contact contrast; no finite CAD approval."""
import sys, json, shutil
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.linalg import block_diag
from baseline_registry import ROOT, dump, ref
sys.path.insert(0,str(ROOT.parent/'stage2_load_transfer/scripts'))
import sliding_pet_contact as contact
import flexible_rail_reference as terminal
contact.LP=terminal.LP
CRITERIA=dict(gap_m_min=-1e-9,force_N_max=1e-8,moment_Nm_max=1e-9,
              complementarity_relative_max=1e-7,energy_relative_max=1e-7,
              green_displacement_m_max=1e-10,green_rotation_rad_max=1e-8,
              finest_motion_relative_max=.01)
def green(load,length,EI):
    # Independent cantilever unit-load quadrature from nodal forces AND moments.
    nodes=np.linspace(0,length,len(load)//2)
    def moment(s):
        mask=nodes>=s
        return float(np.sum(load[0::2][mask]*(nodes[mask]-s)+load[1::2][mask]))
    tip=sum(quad(lambda s:(length-s)*moment(s)/EI(s),a,b,epsabs=1e-17)[0] for a,b in zip(nodes,nodes[1:]))
    rotation=sum(quad(lambda s:moment(s)/EI(s),a,b,epsabs=1e-17)[0] for a,b in zip(nodes,nodes[1:]))
    return tip,rotation
def run(n,force):
    r=contact.trial(n,force,True);m=2*(n+1)
    u=np.r_[r['rail_q'],r['PET_q']];er,ep=terminal.eis()
    K=block_diag(contact.beam(n,terminal.LR,er),contact.beam(n,terminal.LP,ep))
    f=np.zeros(2*m);f[m-2]=force
    pairs=[contact.gap_row(n,kind,s) for kind,s in r['constraint_locations']]
    A=np.array([a for a,b in pairs]);b=np.array([b for a,b in pairs]);dual=np.array(r['constraint_duals_N'])
    load=f-A.T@dual;res=K@u-load
    energy=float(u@K@u);external=float(f@u);wall=float(-dual@b)
    energy_error=abs(energy-external-wall)/max(abs(energy),1e-30)
    moment_error=abs(res[1]+res[m+1]+force*terminal.LR)
    errors=[]
    for offset,length,ei in ((0,terminal.LR,er),(m,terminal.LP,ep)):
        y,theta=green(load[offset:offset+m],length,ei)
        errors.append(dict(tip_m=y,rotation_rad=theta,displacement_error_m=abs(y-u[offset+m-2]),rotation_error_rad=abs(theta-u[offset+m-1])))
    checks=dict(original_contact_certificate=r['status']=='PASS',moment=moment_error<CRITERIA['moment_Nm_max'],
        energy=energy_error<CRITERIA['energy_relative_max'],dual_sign=bool(max(dual)<=1e-15),
        independent_green=all(x['displacement_error_m']<CRITERIA['green_displacement_m_max'] and x['rotation_error_rad']<CRITERIA['green_rotation_rad_max'] for x in errors))
    checks={k:bool(v) for k,v in checks.items()}
    r.update(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,independent_green=errors,
        root_moment_balance_Nm=float(moment_error),twice_stored_energy_J=energy,external_final_dot_J=external,
        contact_clearance_final_dot_J=wall,static_energy_relative_error=energy_error,
        interface_multiplier_sum_N=float(sum(-d for d,(kind,s) in zip(dual,r['constraint_locations']) if kind=='interface')))
    return r
def main():
    out=ROOT/'validation/finger'/sys.argv[1]
    if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP present')
    out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    dependencies=[Path(__file__),Path(contact.__file__),Path(terminal.__file__),ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py',ROOT.parent/'stage2_load_transfer/models/materials/evidence.json',ROOT/'cad/exports/revAD_funnel1/summary.json',ROOT/'validation/finger/flexible_reference2/summary.json',Path(contact.osqp.ext_builtin.__file__)]
    # Binary dependency may reside outside repository; record absolute provenance.
    import hashlib
    dump(out/'inputs.json',dict(criteria=CRITERIA,inputs=[dict(path=str(p),SHA256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in dependencies],lengths_m=dict(rail=terminal.LR,PET=terminal.LP),material_basis='Conditional supplier typical E, unchanged projected sections; no certified lot',normal_interface='rail_y-PET_y >=0 on [0,LP]',terminal_walls='moving Rail tip tangent on [0.083,LP], -0.1/+0.2mm; linear projected geometry only'))
    rows=[]
    for force in (-.001,.00001,.001):
        for n in (8,16,32):
            if (ROOT/'runtime/STOP').exists():raise SystemExit('STOP present')
            rows.append(run(n,force));dump(out/'cases.json',rows)
    refinement=[]
    for force in (-.001,.00001,.001):
        a,b=[r for r in rows if r['force_N']==force][-2:]
        error=max(abs(a[k]-b[k])/max(abs(b[k]),1e-12) for k in ('rail_tip_m','PET_tip_m'))
        refinement.append(dict(force_N=force,motion_relative=error,status='PASS' if error<.01 else 'FAIL'))
    contrasts=[]
    for force in (-.001,.00001,.001):
        t=terminal.solve(32,force);u=np.r_[t['rail_q'],t['PET_q']]
        gap,s=contact.exact_min(32,u,'interface')
        d=[r for r in rows if r['n']==32 and r['force_N']==force][0]
        contrasts.append(dict(force_N=force,terminal_only_interface_min_gap_m=gap,at_material_s_m=s,terminal_tip_m=t['rail_tip_m'],distributed_tip_m=d['rail_tip_m'],terminal_only_surface_valid=gap>=-1e-9))
    controls=dict(terminal_surface_counterexample=any(x['terminal_only_interface_min_gap_m']< -1e-6 for x in contrasts),distributed_interface_loaded=any(r['interface_multiplier_sum_N']>1e-6 for r in rows),open_small_positive_reference=all(abs(r['rail_tip_m']-terminal.reference(.00001)['rail_tip_m'])<1e-10 and r['interface_multiplier_sum_N']<1e-10 for r in rows if r['force_N']==.00001))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows+refinement) and all(controls.values()) else 'FAIL',scope='CONDITIONAL PROJECTED LINEAR DISTRIBUTED FRICTIONLESS CONTACT ONLY',criteria=CRITERIA,rows=rows,refinement=refinement,terminal_contrasts=contrasts,controls=controls,inputs=ref(out/'inputs.json'),whole_system_release=False,limitations=['No finite rotation or actual deformed BRep qualification','No axial strain/friction/strength/dynamic energy certificate','Terminal walls are linearized tip-tangent surfaces, not actual finite CAD','RevAD remains unadopted; RevAA unchanged'])
    dump(out/'summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 2)
if __name__=='__main__':main()
