"""Independent physicalsourcewrench proof of actual P1 ONEincrement loads.
No producer load/port/support helper imported. Includes current allfivebody
weights, moving+fixedRoot, Motorhousing, wire/rotors/object and Basehardware.
"""
import sys,json,shutil,time
import numpy as np
from scipy.spatial.transform import Rotation
from skfem import MeshTet
from baseline_registry import ROOT,REPO,ref,dump

def W(q,f):return np.r_[f,np.cross(q,f)]
def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['source_field']['path']);mo=int(a['motor_offset']);local=json.loads((REPO/s['source']['path']).read_text());old=json.loads((ROOT/'validation/integrated/primaryP1_front_h5_2/summary.json').read_text());mass=json.loads((ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json').read_text());tests=[];states=[('initial',a['u_mm'],json.loads((src.parent/'initial_loads.json').read_text()))]
 if (src.parent/'trial_loads.json').exists():states.append(('trial',np.load(src.parent/'trial_field.npz')['u_mm'],json.loads((src.parent/'trial_loads.json').read_text())))
 for tag,u,detail in states:
  st=detail['upstream'];elastic=np.zeros(6);bodyrows=[];total_mass=0
  for name in local['elastic_bodies']:
   X=a[name+'_points_mm'];t=a[name+'_tetra'];o=int(a[name+'_offset']);x=X+u[o:o+3*len(X)].reshape(-1,3);vol=abs(np.linalg.det(X[t[:,1:]]-X[t[:,0,None]]))/6;w=np.zeros(len(X))
   for j in range(4):np.add.at(w,t[:,j],vol/4)
   massnode=w*float(a[name+'_rho_kg_m3'])*1e-9;forces=np.zeros_like(X);forces[:,2]=-massnode*9.80665;bw=np.r_[forces.sum(0),np.cross(x*.001,forces).sum(0)];elastic+=bw;total_mass+=massnode.sum();bodyrows.append(dict(part=name,mass_kg=float(massnode.sum()),wrench_N_Nm=bw.tolist()))
  upstream=np.zeros(6)
  for kind in ['moving_mass_points','fixed_mass_points']:
   for point in st[kind]:
    m=point['mass_kg'];upstream+=W(np.array(point['position_m']),np.array([0,0,-m*9.80665]));total_mass+=m
  z=u[mo:mo+6];Rm=Rotation.from_rotvec(z[3:]).as_matrix();C=np.array([0,0,.020])+z[:3]*.001;motor=next(p for p in mass if p['part_ID']=='F0_MICRO_MOTOR');m=motor['mass_kg'];q=Rm@(np.array(motor['rest_centroid_m'])-[0,0,.020])+C;upstream+=W(q,np.array([0,0,-m*9.80665]));total_mass+=m
  upstream+=W(np.array(st['tip_world_m']),np.array([st['normal_N'],0,0]));upstream+=np.array(st['string']['wire_gravity_wrench_N_Nm']);total_mass-=st['string']['wire_gravity_wrench_N_Nm'][2]/9.80665
  for rotor in st['string']['rotors']:
   m=rotor['mass_kg'];upstream+=W(np.array(rotor['position_m']),np.array([0,0,-m*9.80665]));total_mass+=m
  p=a['TEST_BASE_points_mm'];t=a['TEST_BASE_tetra'];o=int(a['TEST_BASE_offset']);x=p+u[o:o+3*len(p)].reshape(-1,3);mesh=MeshTet(p.T,t.T);tri=mesh.facets[:,mesh.boundary_facets()].T;tri=tri[np.all(abs(p[tri,2]-66)<1e-5,axis=1)];xy=p[tri].mean(1)[:,:2];centers=np.array([[-44,-30],[-44,10],[86,-30],[86,10]]);tri=tri[np.min(np.linalg.norm(xy[:,None,:]-centers[None,:,:],axis=2),axis=1)>4.7];area=np.linalg.norm(np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]),axis=1)/2;weights=np.zeros(len(p))
  for j in range(3):np.add.at(weights,tri[:,j],area/3)
  ids=weights>0;w=weights[ids];c0=np.average(p[ids],axis=0,weights=w);c1=np.average(x[ids],axis=0,weights=w);R,_=Rotation.align_vectors(x[ids]-c1,p[ids]-c0,weights=w);R=R.as_matrix();hardware=np.zeros(6)
  for name,hp in old['hardware_actual_mass_geometry'].items():
   m=hp['volume_mm3']*7900e-9;q=(R@(np.array(hp['centroid_mm'])-c0)+c1)*.001;hardware+=W(q,np.array([0,0,-m*9.80665]));total_mass+=m
  pair=upstream-np.array(st['Root_origin_wrench_N_Nm'])-np.array(st['Motor_origin_wrench_N_Nm']);expected_base=-(upstream+elastic+hardware);base_error=expected_base-np.array(detail['physical_Base_wrench_N_Nm']);hw_error=hardware-np.array(detail['hardware_current_wrench_N_Nm']);duplicate_error=motor['mass_kg']*9.80665
  checks=dict(allfivebody=len(bodyrows)==5,pairedcable_force=np.linalg.norm(pair[:3])<1e-8,pairedcable_moment=np.linalg.norm(pair[3:])<1e-10,sourceBase_force=np.linalg.norm(base_error[:3])<1e-8,sourceBase_moment=np.linalg.norm(base_error[3:])<1e-10,current_hardware=np.linalg.norm(hw_error)<1e-10,duplicateMotor_rejected=duplicate_error>1e-2)
  tests.append(dict(state=tag,checks={k:bool(v) for k,v in checks.items()},physical_source_Base_wrench_N_Nm=expected_base.tolist(),Base_source_error_N_Nm=base_error.tolist(),hardware_error_N_Nm=hw_error.tolist(),paired_upstream_error_N_Nm=pair.tolist(),hybrid_CAD_FE_mass_kg=float(total_mass),body_gravity=bodyrows,duplicateMotor_force_defect_N=duplicate_error,root_freeY_remaining_increment_mm=detail['root_freeY_increment_mm']))
 checks={z['state']:all(z['checks'].values()) for z in tests};result=dict(status='ACTUAL_P1_INCREMENT_PHYSICAL_SOURCE_LOAD_PASS' if all(checks.values()) else 'ACTUAL_P1_INCREMENT_PHYSICAL_SOURCE_LOAD_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],verifier=ref(out/'verifier.py'),checks=checks,physical_states=tests,states_verified=len(tests),actual_support_equilibrium_certified=False,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Sourcephysicalgravity/object/cablewrenches independently enumerated atactualsavedsource/trialpositions. PhysicalBase reaction derives fromthese,not elastic/contact/reference residualcancellation.','Hybridcoarsetetra/CADmass andnonlocalhardware transport stillunqualified as78CADmass/inertia,localhardwarebearings or physicalBaseanchor. A remainingfreeYincrement means upstream/supportgeometryisnotclosed; physicalsourceaccountingdoesnotacceptthepredictor. All22systemgatesremainunqualified.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
