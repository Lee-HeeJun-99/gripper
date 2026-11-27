"""Independent integration of saved finite constant-traction fields and CAD contacts."""
import json,sys,shutil,copy
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt

def main():
 out=ROOT/'validation/transmission/primaryP1_transfer_verify2';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();audits=[];datasets=[]
 for tag in ('primaryP1_contact_transfer2','primaryP1_contact_transfer3'):
  path=ROOT/'validation/transmission'/tag/'summary.json';d=json.loads(path.read_text());p=json.loads((REPO/d['patches']['path']).read_text());b=json.loads((REPO/d['bearing_patches']['path']).read_text());inputs=json.loads((REPO/d['inputs']['path']).read_text());cad=json.loads((REPO/d['candidate']['path']).read_text());datasets.append(d)
  refs=[d['candidate'],d['producer'],d['inputs'],d['patches'],d['bearing_patches']]+list(inputs['parts'].values())+[inputs['loads']]+inputs['dependencies'];hashok=all(sha(REPO/r['path'])==r['SHA256'] for r in refs)
  areas=all(abs(v['cell_area_sum_mm2']/v['area_mm2']-1)<1e-9 for v in p.values());bearing=all(x['area_mm2']>0 for x in b)
  for row in d['rows']:
   if not row['success']:
    audits.append(dict(source=ref(path),interface=row['interface'],mu=row['mu_assumed'],failed_equilibrium_preserved=True,analytical_frictionless_rejection=bool(row['mu_assumed']==0 and abs(row['external_wrench_N_Nm'][0])>1e-8)));continue
   m=row['interface'];ext=np.array(row['external_wrench_N_Nm']);balance=ext.copy();cap=np.zeros(6);press={};points=True;cone=True;forces=[];moments=[]
   for ray in row['rays']:
    q=np.array(ray['point_mm'])*.001;direction=np.array(ray['direction']);coef=ray['coefficient_N'];f=direction*coef;w=np.r_[f,np.cross(q,f)];cone &= coef>=0
    if m=='motor_lands_and_cap_bolts':
     side=ray['side']
     if side=='cap_bolt':cap+=w;continue
     if side=='motor_top':cap-=w;cone &= bool(abs(f[0])+abs(f[1])<1e-12)
     patch=p[side];normal=1 if side=='motor_bottom' else -1
    else:
     side=m;normal=row['normal_sign']
     if ray['kind']=='bolt_axial':
      cone &= bool(np.linalg.norm(direction-[0,0,-normal])<1e-12);balance+=w;continue
     patch=p[m]
    balance+=w;force_n=f[2]*normal;cone &= bool(force_n>=-1e-12 and np.linalg.norm(f[:2])<=row['mu_assumed']*force_n+1e-10)
    distances=[np.linalg.norm(np.array(c['point_mm'])-np.array(ray['point_mm'])) for c in patch['cells']];index=int(np.argmin(distances));points &= distances[index]<1e-7
    key=(side,index);press[key]=press.get(key,0)+force_n/patch['cells'][index]['area_mm2'] # N/mm2 = MPa
    forces.append(f);moments.append(np.cross(q,f))
   forceerr=max(np.linalg.norm(balance[:3]),np.linalg.norm(cap[:3]));momenterr=max(np.linalg.norm(balance[3:]),np.linalg.norm(cap[3:]));negative=copy.deepcopy(row['rays'][0]);f=np.array(negative['direction'])*negative['coefficient_N']*.01;corrupt=balance+np.r_[f,np.cross(np.array(negative['point_mm'])*.001,f)]
   checks=dict(hashes=hashok,finite_partition_area=areas,all20_actual_bearing_patches_nonzero=bearing,finite_cell_centers=bool(points),physical_cone=bool(cone),force=bool(forceerr<1e-8),moment=bool(momenterr<1e-10),perturbed_ray_rejected=bool(np.linalg.norm(corrupt[:3])>1e-8 or np.linalg.norm(corrupt[3:])>1e-10))
   audits.append(dict(source=ref(path),interface=m,mu=row['mu_assumed'],checks=checks,passed=all(checks.values()),independent_force_error_N=float(forceerr),independent_moment_error_Nm=float(momenterr),max_uniform_cell_normal_pressure_MPa=float(max(press.values())),pressure_scope='Piecewise-constant assumed rigid-equilibrium traction,NOT elastic peak pressure or allowable'))
 # Independent numerical mesh comparison of the necessary bound. Existing1% unchanged.
 convergence=[]
 for a,b in zip(datasets[0]['rows'],datasets[1]['rows']):
  if not a['success'] or not b['success']:continue
  key='total_compression_N' if a['interface'].startswith('motor') else 'minimum_total_bolt_axial_N';err=abs(a[key]/b[key]-1)
  convergence.append(dict(interface=a['interface'],mu=a['mu_assumed'],metric=key,coarse=a[key],fine=b[key],relative_error=err,criterion=.01,passed=err<.01))
 # Reconstruct action/reaction through actual head/nut bearing planes.
 # No ground reaction is supplied here; its free-body residual is explicitly retained.
 networks=[]
 fine=datasets[-1]
 for mu in (.1,.2,.4,.8):
  rr={r['interface']:r for r in fine['rows'] if r['mu_assumed']==mu};frame=np.zeros(6);cap=np.zeros(6);ground=np.zeros(6);root=np.array(rr['root_frame']['external_wrench_N_Nm']);motor=np.array(rr['motor_lands_and_cap_bolts']['external_wrench_N_Nm']);bearing_pressure=[]
  def w(q,f):return np.r_[f,np.cross(np.array(q)*.001,f)]
  for ray in rr['root_frame']['rays']:
   f=np.array(ray['direction'])*ray['coefficient_N'];q=ray['point_mm'];root+=w(q,f)
   if ray['kind']=='bolt_axial':
    q=[q[0],q[1],-12];bearing_pressure.append(dict(interface='RF',axial_N=float(np.linalg.norm(f)),minimum_head_nut_area_mm2=min(x['area_mm2'] for x in b if x['first'].startswith('F0_RF'))))
   frame+=w(q,-f)
  for ray in rr['motor_lands_and_cap_bolts']['rays']:
   f=np.array(ray['direction'])*ray['coefficient_N'];q=ray['point_mm'];side=ray['side']
   if side=='cap_bolt':
    cap+=w(q,f);frame+=w([q[0],q[1],11],-f);bearing_pressure.append(dict(interface='MOTOR_CAP',axial_N=float(np.linalg.norm(f)),minimum_head_nut_area_mm2=min(x['area_mm2'] for x in b if x['first'].startswith('MOTOR_CAP'))))
   else:
    motor+=w(q,f)
    if side=='motor_top':cap+=w(q,-f)
    else:frame+=w(q,-f)
  for ray in rr['frame_ground']['rays']:
   f=np.array(ray['direction'])*ray['coefficient_N'];q=ray['point_mm'];frame+=w(q,f)
   if ray['kind']=='bolt_axial':
    q=[q[0],q[1],46];bearing_pressure.append(dict(interface='GROUND',axial_N=float(np.linalg.norm(f)),minimum_head_nut_area_mm2=min(x['area_mm2'] for x in b if x['first'].startswith('GROUND_'))))
   ground+=w(q,-f)
  expected=np.array(fine['paired_external_wrench_N_Nm']);checks_net=dict(root=bool(np.linalg.norm(root[:3])<1e-8 and np.linalg.norm(root[3:])<1e-10),motor=bool(np.linalg.norm(motor[:3])<1e-8 and np.linalg.norm(motor[3:])<1e-10),cap=bool(np.linalg.norm(cap[:3])<1e-8 and np.linalg.norm(cap[3:])<1e-10),frame=bool(np.linalg.norm(frame[:3])<1e-8 and np.linalg.norm(frame[3:])<1e-10),ground_port_action_reaction=bool(np.linalg.norm(ground-expected)<1e-10),free_ground_is_NOT_in_equilibrium=bool(np.linalg.norm(ground[:3])>1e-8))
  for r in bearing_pressure:r['uniform_bearing_pressure_MPa']=r['axial_N']/r['minimum_head_nut_area_mm2']
  networks.append(dict(mu_assumed=mu,checks=checks_net,root_residual_N_Nm=root.tolist(),motor_residual_N_Nm=motor.tolist(),cap_residual_N_Nm=cap.tolist(),frame_residual_N_Nm=frame.tolist(),actual_free_ground_residual_N_Nm=ground.tolist(),required_external_ground_wrench_NOT_applied=(-ground).tolist(),bearing_pressure=bearing_pressure,scope='Finite bearing axial resultants with equal/opposite bolt tension only; nominal smooth envelopes do not certify thread flank/core strength or elastic distribution'))
 checks=dict(all_saved_traction_fields_verified=all(r.get('passed',r.get('analytical_frictionless_rejection',False)) for r in audits),all_bound_mesh_pairs_pass_1pct=all(r['passed'] for r in convergence),full_network_action_reaction_verified=all(all(r['checks'].values()) for r in networks))
 result=dict(status='PRIMARY_FINITE_TRACTION_RECONSTRUCTION_PASS_MESH_FAIL' if checks['all_saved_traction_fields_verified'] and not checks['all_bound_mesh_pairs_pass_1pct'] else 'PRIMARY_FINITE_TRACTION_VERIFY_PASS' if all(checks.values()) else 'PRIMARY_FINITE_TRACTION_VERIFY_FAIL',candidate=datasets[0]['candidate'],producer=ref(out/'producer.py'),audits=audits,mesh=convergence,networks=networks,checks=checks,whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['No equilibrium solver called by verifier; force/moment reconstructed from actual finite-cell centroid integrals','Mesh1% failures preserved; contact compliance/preload/source minima and finite bench attachment absent','No structural strength,physical preload,full dynamics/energy or3Finger release'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,mesh=convergence)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
