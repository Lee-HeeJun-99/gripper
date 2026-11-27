"""New numerical cotangent validation on actual P1 seated22 support field.
Independent expm point derivatives; all moving/fixed Root weights retained.
No new equilibrium, CAD adoption, strength or global energy certificate.
"""
import sys,json,shutil
import numpy as np
from scipy.linalg import expm
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_port import RootPort,motor_pullback,motor_positions,skew,left_jacobian

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'validation/integrated/primaryP1_reclosure3/summary.json';s=json.loads(src.read_text());assert sha(REPO/s['field']['path'])==s['field']['SHA256'];a=np.load(REPO/s['field']['path']);state=json.loads((REPO/s['state']['path']).read_text());cad=json.loads((REPO/s['candidate']['path']).read_text());assert len(cad['part_references'])==78
 for v in cad['part_references'].values():assert sha(REPO/v['path'])==v['SHA256']
 n='F0_ROOT_BACK';p=a[n+'_points_mm'];off=int(a[n+'_offset']);sel=abs(p[:,0]-50.5)<1e-5;p=p[sel];u=a['u_mm'][off:off+3*len(sel)].reshape(-1,3)[sel];w=a['Root_port_weights_mm2'][sel];port=RootPort(p,w);z,R,b=port.pose(u);mo=int(a['motor_offset']);um=a['u_mm'][mo:mo+6];C=np.array([0,0,.020])+um[:3]*.001
 # Explicit forces, not equivalent ideal coupons: actual saved cable/object/weights.
 rows=[dict(name='cable',q=state['string']['E_m'],f=state['string']['Fe_N']),dict(name='object',q=state['tip_world_m'],f=[state['normal_N'],0,0])]
 for kind in ('moving_mass_points','fixed_mass_points'):
  rows += [dict(name=kind+':'+x['part_ID'],q=x['position_m'],f=[0,0,-9.80665*x['mass_kg']]) for x in state[kind]]
 q=np.array([r['q'] for r in rows]);f=np.array([r['f'] for r in rows]);W=np.r_[f.sum(0),np.cross(q,f).sum(0)];RW=np.array(state['Root_origin_wrench_N_Nm']);MW=np.array(state['Motor_origin_wrench_N_Nm']);qref=(q-b)@R+port.anchor*.001
 # Independent weighted fit via sqrt-area lstsq and exponential matrix.
 A=np.concatenate([np.column_stack((np.eye(3),-skew(v-p.mean(0)))) for v in p]);sw=np.sqrt(np.repeat(w,3))
 def positions(v):
  zz=np.linalg.lstsq(A*sw[:,None],v.ravel()*sw,rcond=None)[0];RR=expm(skew(zz[3:]));bb=(port.anchor+zz[:3]+np.cross(zz[3:],port.anchor-p.mean(0)))*.001
  return (qref-port.anchor*.001)@RR.T+bb
 def potential(v):return float(np.sum(positions(v)*f)) # instantaneous frozen world forces, not global stored energy
 g=port.pullback(u,RW);rng=np.random.default_rng(1307);directions=[]
 for j in range(6):directions.append((A@np.eye(6)[j]).reshape(-1,3))
 directions += [rng.normal(size=u.shape) for j in range(12)]
 errors=[]
 for i,d in enumerate(directions):
  d=d/max(np.linalg.norm(d,axis=1).max(),1);analytic=float(np.sum(g*d));errs=[]
  for h in (2e-4,1e-4,5e-5):errs.append(float(abs((potential(u+h*d)-potential(u-h*d))/(2*h)*1000-analytic)))
  errors.append(dict(direction=i,analytic_Nmm_per_mm=analytic,absolute_errors_N=errs))
 # Motor: exact equivalent point forces realize full actual saved downstream+housing wrench.
 tau=MW[3:]-np.cross(C,MW[:3]);qm=[C];fm=[MW[:3]]
 for j in range(3):
  e=np.eye(3)[(j+1)%3];fj=np.cross(tau[j]*np.eye(3)[j],e)/.02;qm.extend([C+.01*e,C-.01*e]);fm.extend([fj,-fj])
 qm=np.array(qm);fm=np.array(fm);Rm=expm(skew(um[3:]));mr=(qm-C)@Rm+[0,0,.020]
 def mp(v):return (mr-[0,0,.020])@expm(skew(v[3:])).T+np.array([0,0,.020])+v[:3]*.001
 mg=motor_pullback(um,MW);me=[]
 for d in np.eye(6):
  h=1e-5;fd=float(np.sum((mp(um+h*d)-mp(um-h*d))*fm)/(2*h)*1000);me.append(abs(fd-mg@d))
 # Generalized forces vs old reference wrench transfer at ACTUAL field.
 old=port.L.T@np.r_[RW[:3],1000*(RW[3:]-np.cross(port.center*.001,RW[:3]))];delta=g.ravel()-old
 oldm=np.r_[MW[:3],1000*(MW[3:]-np.cross([0,0,.020],MW[:3]))]
 controls={}
 for name,gg in [('wrong_sign',-g),('wrong_transpose', (port.L.T@np.r_[RW[:3],skew(port.anchor-port.center)@RW[:3]+1000*left_jacobian(z[3:])@(RW[3:]-np.cross(b,RW[:3]))]).reshape(-1,3)),('missing_anchor_transport',(port.L.T@np.r_[RW[:3],1000*left_jacobian(z[3:]).T@RW[3:]]).reshape(-1,3)),('double_fixed_weight',port.pullback(u,RW+np.array(state['fixed_Root_wrench_N_Nm']))),('legacy_reference',old.reshape(-1,3))]:
  controls[name]=float(max(abs(np.sum((gg-g)*d/max(np.linalg.norm(d,axis=1).max(),1))) for d in directions))
 # Current nodal rigid virtual rotation vs actual nonlinear port. This is an eligibility
 # check, not silently corrected by a compensating Base force.
 rigid=[]
 for axis in np.eye(3):
  d=np.cross(axis,p+u);nodal=float(np.sum(g*d))*.001;physical=float(axis@RW[3:]);rigid.append(nodal-physical)
 # Direct finite common rotation of deformed face: linear fit is not an objective fit.
 finite=[]
 for angle in (.001,.01):
  rot=expm(skew(np.array([.3,-.2,.4])*angle));up=(p+u)@rot.T-p;err=np.max(np.linalg.norm(positions(up)-q@rot.T,axis=1));finite.append(dict(rotation_scale_rad=angle,maximum_covariance_error_m=float(err)))
 checks=dict(actual78part_identity=len(cad['part_references'])==78,all_root_components=np.linalg.norm(W-RW)<1e-12,root_point_value=np.max(abs(positions(u)-q))<1e-12,root_independent_FD=max(r['absolute_errors_N'][-1] for r in errors)<1e-8,motor_independent_FD=max(me)<1e-8,negative_controls=all(v>1e-10 for v in controls.values()),finite_values=bool(np.all(np.isfinite(g)) and np.all(np.isfinite(mg))))
 np.savez_compressed(out/'pullback.npz',root_selected_nodes=np.flatnonzero(sel),root_generalized_force_N=g,motor_generalized_force_N=mg,root_legacy_force_N=old.reshape(-1,3),motor_legacy_force_N=oldm,root_fit_z=z,root_fit_L=port.L)
 eligible=max(abs(np.array(rigid)))<1e-10
 result=dict(status='ACTUAL_P1_FINITE_PORT_DIFFERENTIAL_PASS_OBJECTIVITY_BLOCKED' if all(checks.values()) and not eligible else 'ACTUAL_P1_FINITE_PORT_AUDIT_OTHER',candidate=s['candidate'],source=ref(src),producer=ref(out/'producer.py'),implementation=ref(ROOT/'scripts/primary_finite_port.py'),field=s['field'],state=s['state'],pullback=ref(out/'pullback.npz'),checks={k:bool(v) for k,v in checks.items()},root_nodes=len(p),root_components=rows,root_fit_z=z.tolist(),root_FD=errors,motor_FD_absolute_error_N=me,negative_control_max_work_error_N=controls,root_force_change_norm_N=float(np.linalg.norm(delta)),motor_generalized_change_N_Nmm=(mg-oldm).tolist(),root_current_rigid_rotation_work_error_Nm=rigid,finite_objectivity_controls=finite,coupling_update_eligible=bool(eligible),new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Analytic cotangent lift differentiates the existing linear weighted fit plus anchor transport and exponential rotation. Independent actual frozen load point work is verified; this is not global stored energy.','Linear Root fit is not finite objective. A common current nodal rotation does not induce the same physical port rotation/translation: do not balance that defect by arbitrary Base cancellation or certify spatial moment closure. No new contact solve until objective pose fit/derivative is independently checked.','All78 original CAD parts retained. Full3D lateral Finger, finite wire bending, contact/mesh/time, case/bearing/thread/preload/minima/physical anchor/protector/friction/global energy/full3Finger remain unqualified.'])
 dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('root_components','root_FD','limitations')}));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
