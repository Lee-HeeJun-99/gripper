"""Objective Root port on actual P1 surface and NEW actual upstream equilibrium.
Same geometry/source parts/conditional planar Finger. No new support FE solve.
"""
import sys,json,shutil
import numpy as np
from scipy.linalg import expm
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_port import ObjectiveRootPort,RootPort,skew
from primary_seated_string import SeatedString
from primary_seated_finger_v2 import solve

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_reclosure3/summary.json';s=json.loads(src.read_text());assert sha(REPO/s['field']['path'])==s['field']['SHA256'];a=np.load(REPO/s['field']['path']);old=json.loads((REPO/s['state']['path']).read_text());name='F0_ROOT_BACK';pall=a[name+'_points_mm'];off=int(a[name+'_offset']);sel=abs(pall[:,0]-50.5)<1e-5;p=pall[sel];u=a['u_mm'][off:off+3*len(pall)].reshape(-1,3)[sel];w=a['Root_port_weights_mm2'][sel];port=ObjectiveRootPort(p,w);R,c,B=port.pose(u);tr=c*.001-R@(port.center*.001);mo=int(a['motor_offset']);um=a['u_mm'][mo:mo+6];Rm=Rotation.from_rotvec(um[3:]).as_matrix();C=np.array([0,0,.020])+um[:3]*.001
 seedpath=ROOT/'validation/finger/primaryP1_gravity_cat_demand32_2/cases.json';masspath=ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json';seed=json.loads(seedpath.read_text())[0];points=json.loads(masspath.read_text());E=R@np.array([seed['cable_end_m'][0],0,seed['cable_end_m'][1]])+tr
 initial=SeatedString(points,Rm,C,E,.01125).solve(seed);parent=dict(root_R=R.tolist(),root_translation_m=tr.tolist(),motor_R=Rm.tolist(),motor_C_m=C.tolist(),actual_wire_center_radius_m=.01125,actual=initial);actual=solve(parent,seed,points);dump(out/'curves.json',{k:actual['string'].pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')});dump(out/'state.json',actual)
 # solve returns a small freeY INCREMENT: carry it explicitly in point transport.
 dy=np.array([0,actual['string']['root_free_Y_shift_mm']*.001,0]);F=[];Q=[];labels=[]
 for q,f,label in [(actual['string']['E_m'],actual['string']['Fe_N'],'cable'),(actual['tip_world_m'],[actual['normal_N'],0,0],'object')]:Q.append(q);F.append(f);labels.append(label)
 for kind in ('moving_mass_points','fixed_mass_points'):
  for item in actual[kind]:Q.append(item['position_m']);F.append([0,0,-item['mass_kg']*9.80665]);labels.append(kind+':'+item['part_ID'])
 Q=np.array(Q);F=np.array(F);W=np.r_[F.sum(0),np.cross(Q,F).sum(0)];RW=np.array(actual['Root_origin_wrench_N_Nm']);qref=(Q-dy-c*.001)@R+port.center*.001;g=port.pullback(u,RW-np.r_[np.zeros(3),np.cross(dy,RW[:3])])
 # Independent scipy align_vectors pose uses no polar differential implementation.
 def pos(v):
  cur=p+v;cc=w@cur/w.sum();rr,_=Rotation.align_vectors(cur-cc,p-port.center,weights=w);return (qref-port.center*.001)@rr.as_matrix().T+cc*.001+dy
 def work(v):return float(np.sum(pos(v)*F))
 rng=np.random.default_rng(1317);D=[np.tile(e,(len(p),1)) for e in np.eye(3)]+[np.cross(e,p+u) for e in np.eye(3)]+[rng.normal(size=u.shape) for _ in range(12)];fd=[]
 for d in D:
  d=d/max(np.max(np.linalg.norm(d,axis=1)),1);gg=float(np.sum(g*d));hs=[1e-3,5e-4,2.5e-4];err=[abs((work(u+h*d)-work(u-h*d))*1000/(2*h)-gg) for h in hs];fd.append(dict(analytic_N=gg,steps_mm=hs,absolute_error_N=err))
 # Exclude explicit dy in rigid-motion comparison: it is an external free coordinate,
 # with generalized force FY = sum F_y and must also move under common rigid motion.
 rigid=[]
 for e in np.eye(3):rigid.append(float(np.sum(g*np.cross(e,p+u))*.001+e@np.cross(dy,RW[:3])-e@RW[3:]))
 finite=[]
 for theta,d in [(np.array([.0003,-.0002,.0004]),np.zeros(3)),(np.array([.3,-.2,.4]),np.array([1.2,-.4,3.1]))]:
  rr=expm(skew(theta));un=(p+u)@rr.T+d-p;R2,c2,B2=port.pose(un);error=float(np.max(abs(R2-rr@R)));centerr=float(np.max(abs(c2-(rr@c+d))));finite.append(dict(theta_rad=theta.tolist(),translation_mm=d.tolist(),rotation_matrix_error=error,center_error_mm=centerr))
 # Rigid motion covariance/FD corruption rejection, with deliberate wrong polar sign.
 bad=-g;sign_error=max(abs(np.sum((bad-g)*d/max(np.max(np.linalg.norm(d,axis=1)),1))) for d in D);unweighted=ObjectiveRootPort(p,np.ones(len(p)));Rg,cg,Bg=unweighted.pose(u);unweighted_delta=float(np.linalg.norm(cg-c)+np.linalg.norm(Rg-R))
 # Local linear FE's null rotations are reference, not current tangent. Quantify why
 # direct arbitrary Base rebalancing is prohibited even after objective port repair.
 linear_moment_defect=np.cross(p*.001,g).sum(0)+np.cross(dy,RW[:3])-RW[3:];current_moment_error=np.cross((p+u)*.001,g).sum(0)+np.cross(dy,RW[:3])-RW[3:]
 checks=dict(upstream=all(actual['checks'].values()),components=np.linalg.norm(W-RW)<1e-12,point_value=np.max(abs(pos(u)-Q))<1e-12,polar_FD=max(x['absolute_error_N'][-1] for x in fd)<1e-8,force=np.linalg.norm(g.sum(0)-RW[:3])<1e-8,current_moment=np.linalg.norm(current_moment_error)<1e-10,rigid_virtual_work=max(abs(np.array(rigid)))<1e-10,finite_covariance=max(x['rotation_matrix_error'] for x in finite)<1e-12 and max(x['center_error_mm'] for x in finite)<1e-10,negative_sign=sign_error>1e-3,weight_control=unweighted_delta>1e-10,polar_positive=np.linalg.eigvalsh((B+B.T)/2).min()>0)
 np.savez_compressed(out/'port.npz',root_nodes=np.flatnonzero(sel),root_force_N=g,root_R=R,root_center_mm=c,polar_B=B,freeY_increment_m=dy)
 result=dict(status='ACTUAL_P1_OBJECTIVE_PORT_AND_NEW_UPSTREAM_PASS_SUPPORT_NOT_RECLOSED' if all(checks.values()) else 'ACTUAL_P1_OBJECTIVE_PORT_FAIL',candidate=s['candidate'],source=ref(src),producer=ref(out/'producer.py'),implementation=ref(ROOT/'scripts/primary_finite_port.py'),seed=ref(seedpath),mass=ref(masspath),field=s['field'],state=ref(out/'state.json'),curves=ref(out/'curves.json'),port=ref(out/'port.npz'),checks={k:bool(v) for k,v in checks.items()},root_nodes=len(p),root_FD=fd,finite_covariance=finite,polar_B_eigenvalues=np.linalg.eigvalsh((B+B.T)/2).tolist(),root_force_error_N=(g.sum(0)-RW[:3]).tolist(),root_current_moment_error_Nm=current_moment_error.tolist(),root_reference_FE_null_rotation_moment_defect_Nm=linear_moment_defect.tolist(),root_rigid_virtual_work_error_Nm=rigid,normal_N=actual['normal_N'],normal_change_from_old_N=actual['normal_N']-old['normal_N'],Root_wrench_change_N_Nm=(RW-old['Root_origin_wrench_N_Nm']).tolist(),freeY_increment_mm=dy[1]*1000,unweighted_fit_control_delta=unweighted_delta,sign_control_work_error_N=sign_error,point_count=len(Q),load_component_labels=labels,support_field_resolved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['NEW upstream spatial string/planar Finger equilibrium uses objective Root pose of same actual saved78part support field. FreeY increment explicit, not physical retention. No new support equilibrium or full3D rod.','Objective polar differential passes actual point-work, common finite rotation/translation and current moment tests. Local linear FE retains reference null rotations; mapped current loads therefore cannot be inserted while silently canceling reference moment at Base. Need a consistent corotated support/load formulation or derive a bounded small-displacement truncation.','Conditional materials, finite-wire bending/source play/diameter, 2.55046416% bearing-face/Frame/Rail/GroundBase mesh failures, thread/case/bearings/preload/physical anchor/friction/protector/globalenergy/full3Finger remain unqualified.'])
 dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('root_FD','limitations','load_component_labels')}));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
