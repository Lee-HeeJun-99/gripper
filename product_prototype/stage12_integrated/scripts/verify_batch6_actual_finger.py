"""Independent force/moment, line-length virtual work and section-energy audit."""
import json, shutil
import numpy as np
from pathlib import Path
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/finger/batch6_actual_specimen_verify3';out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'validation/finger/batch6_actual_specimen3/summary.json';d=json.loads(src.read_text())
    inputs=json.loads((REPO/d['inputs']['path']).read_text())
    refs=[inputs['candidate'],*inputs['parts'].values(),*inputs['dependencies'],inputs['producer'],d['inputs'],d['producer']]
    checks={'source_hashes':all(sha(REPO/r['path'])==r['SHA256'] for r in refs),'producer_checks':all(d['checks'].values())}
    P=np.array(d['tendon']['P_mm']);Q=np.array(d['tendon']['Q_mm']);T=d['tendon']['tension_N'];t=np.array(d['tendon']['direction']);force=T*t
    root=np.array([d['rail_axis_x_mm'],0.,d['cut_root_z_mm']]);moment=np.cross(P-root,force)
    c=d['refinements'][-1];rx,rm,rs=c['root_reaction']
    force_error=float(np.linalg.norm(np.array([rx,0,-rs])+force));moment_error=abs(-rm+moment[1])
    checks['spatial_root_balance']=max(force_error,moment_error)<1e-8
    # Differentiate the free straight segment at fixed tangent Q. At tangency
    # the envelope theorem cancels first-order motion of the Idler tangency.
    end=np.array([d['rail_axis_x_mm'],0.,d['cut_tip_z_mm']]);e=P-end
    def cable_length(q):
        u,th,v=q;rot=np.array([[np.cos(th),0,-np.sin(th)],[0,1,0],[np.sin(th),0,np.cos(th)]])
        p=end+np.array([u,0,-v])+rot@e
        return np.linalg.norm(Q-p)
    numeric=[]
    for i in range(3):
        dq=np.zeros(3);dq[i]=1e-5
        numeric.append(float(-T*(cable_length(dq)-cable_length(-dq))/(2e-5)))
    expected=np.array(d['equivalent_tip_wrench_N_Nmm']);work_error=float(max(abs(np.array(numeric)-expected)))
    checks['line_length_virtual_work']=work_error<1e-9
    # Independent Gaussian integration of internal N,M squared, not assembled K.
    gx,gw=np.polynomial.legendre.leggauss(5);L=d['L_mm'];s=L/2*(gx+1);F,M,N=expected
    integrand=(F*(L-s)+M)**2/(d['E_N_mm2']*d['combined_Iyy_mm4'])+N*N/(d['E_N_mm2']*d['combined_A_mm2'])
    U=float(L/4*np.dot(gw,integrand));energy_error=abs(U/c['energy_Nmm']-1)
    checks['internal_energy_vs_FEM']=energy_error<1e-8
    # Both refinement and base-to-finest retained, even though this uniform
    # linear element has an exactly representable cubic bending solution.
    mesh_errors=[abs(x['tip_rotation_rad']/c['tip_rotation_rad']-1) for x in d['refinements']]
    checks['all_mesh_pairs']=max(mesh_errors)<.01
    checks['wrong_eccentricity_control']=abs(expected[1]-(d['terminal_offset_s_mm']*F-(43-d['rail_axis_x_mm']+1)*N))>1e-7
    checks['wrong_tangent_control']=abs(float((P-(Q+np.array([1,0,0])))@(Q+np.array([1,0,0])-np.array([44,0,25]))))>1e-8
    # Numerical validity is explicitly separate from the physically unjustified1N extrapolation.
    checks['one_N_linear_domain_rejected']=not d['extrapolation_1N']['small_rotation_005rad']
    checks={k:bool(v) for k,v in checks.items()}
    dump(out/'summary.json',dict(status='BOUNDED_ACTUAL_AO_REFERENCE_AUDIT_PASS' if all(checks.values()) else 'BOUNDED_ACTUAL_AO_REFERENCE_AUDIT_FAIL',source=ref(src),producer=ref(out/'producer.py'),checks=checks,force_error_N=force_error,moment_error_Nmm=moment_error,numeric_tip_wrench=numeric,virtual_work_absolute_error=work_error,integrated_energy_Nmm=U,energy_relative_error=energy_error,base_to_finest_rotation_relative_errors=mesh_errors,actual_loaded_connection_qualified=False,whole_system_release=False,scope='Independent actual AO reference verification only; no full specimen, strength, buckling or global energy certificate'))
    print(json.dumps(dict(checks=checks,energy_error=energy_error,work_error=work_error)))
    raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
