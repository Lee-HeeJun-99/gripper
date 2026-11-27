"""Independent affine Hooke reconstruction of actual P1 bolt Neumann states."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
from audit_anchor_elastic37 import internal

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');rows=[]
 for tag in sys.argv[2:]:
  src=ROOT/'validation/integrated'/tag/'summary.json';d=json.loads(src.read_text());assert sha(REPO/d['actual_part']['path'])==d['actual_part']['SHA256'];a=np.load(REPO/d['fields']['path']);p,t,u,f=a['points_mm'],a['tetra'],a['U'],a['F'];rebuilt=np.zeros_like(a['port_F']);xerr=0.
  for j,port in enumerate(d['boundary_journal']):
   total=sum(q['area_mm2'] for q in port['quadrature'])
   for q in port['quadrature']:
    nd=q['nodes'];bc=np.array(q['barycentric']);xerr=max(xerr,float(abs(bc@p[nd]-q['point_mm']).max()));force=np.array(port['normalized_direction'])*q['area_mm2']/total
    for n,b in zip(nd,bc):rebuilt[3*n:3*n+3,j]+=b*force
  force,work=internal(p,t,u,d['E_MPa'],d['nu']);res=float(abs(force-f).max());W=float((f.T@u)[0,0]);werr=abs(float(work[0])-W)/abs(W);bad=u.copy();bad[0,0]+=1e-5;bf,_=internal(p,t,bad,d['E_MPa'],d['nu']);negative=float(abs(bf-f).max());ff=rebuilt.sum(axis=1).reshape(-1,3);net=np.r_[ff.sum(0),np.cross(p,ff).sum(0)]
  checks=dict(boundary_reconstruction=float(abs(rebuilt-a['port_F']).max())<1e-12,actual_material_positions=xerr<1e-7,original_force=res<1e-8,original_moment=float(abs(net[3:]).max())*.001<1e-10,independent_work=werr<1e-8,perturbed_state_rejected=negative>1e-8,compliance_reproduced=abs(W-d['unit_compliance_mm_N'])<1e-16)
  rows.append(dict(source=ref(src),checks=checks,nodes=d['nodes'],h_mm=d['h_mm'],unit_compliance_mm_N=W,force_residual_N=res,work_relative=werr,perturbed_force_residual_N=negative,full_to_uniform20mm_ratio=d['full_bolt_to_uniform20mm_ratio']))
 # Independent same-mesh solver equivalence, including every restored DOF.
 left=ROOT/'validation/integrated/primaryP1_bolt41_h05';right=ROOT/'validation/integrated/primaryP1_bolt41_h05quotient';aa=np.load(left/'fields.npz');bb=np.load(right/'fields.npz');assert np.array_equal(aa['points_mm'],bb['points_mm']) and np.array_equal(aa['tetra'],bb['tetra']) and np.array_equal(aa['F'],bb['F']);equiv=float(abs(aa['U']-bb['U']).max()/abs(aa['U']).max());assert equiv<1e-7
 cc=np.load(ROOT/'validation/integrated/primaryP1_bolt41_h05amg/fields.npz');assert np.array_equal(aa['points_mm'],cc['points_mm']) and np.array_equal(aa['tetra'],cc['tetra']);amgequiv=float(abs(aa['U']-cc['U']).max()/abs(aa['U']).max());assert amgequiv<1e-7
 contrasts=[dict(coarse=a['source'],fine=b['source'],relative_compliance_change=abs(a['unit_compliance_mm_N']-b['unit_compliance_mm_N'])/max(a['unit_compliance_mm_N'],b['unit_compliance_mm_N']),original_one_percent_pass=abs(a['unit_compliance_mm_N']-b['unit_compliance_mm_N'])/max(a['unit_compliance_mm_N'],b['unit_compliance_mm_N'])<.01) for a,b in zip(rows,rows[1:])];ok=all(all(r['checks'].values()) for r in rows)
 dump(out/'summary.json',dict(status='ACTUAL_P1_BOLT_INDEPENDENT_LOCAL_PASS' if ok else 'ACTUAL_P1_BOLT_INDEPENDENT_FAIL',candidate=d['candidate'],verifier=ref(out/'verifier.py'),rows=rows,mesh_contrasts=contrasts,same_mesh_solver_displacement_relative=equiv,same_mesh_AMG_displacement_relative=amgequiv,same_mesh_solver_original_1e_minus7_pass=equiv<1e-7,base_to_finest_relative=abs(rows[0]['unit_compliance_mm_N']-rows[-1]['unit_compliance_mm_N'])/max(rows[0]['unit_compliance_mm_N'],rows[-1]['unit_compliance_mm_N']),all_mesh_contrasts_pass=all(c['original_one_percent_pass'] for c in contrasts),local_checks_pass=ok,physical_stack_qualified=False,whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Fullactual bolt geometry with declared terminal-end traction;NOT installed thread transfer or physical pressure.','No source material minimum,thread tolerance/flank,head-seat unilateral contact/preload,nut or external fixture qualification.']));print(json.dumps(dict(local=ok,contrasts=contrasts)));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
