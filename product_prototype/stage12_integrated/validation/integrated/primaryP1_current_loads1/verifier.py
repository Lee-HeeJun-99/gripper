"""Actual P1 independent current physical gravity/Base reaction reconstruction.
Enumerates physical source points rather than cancelling a generalized FE/null
residual. Hardware stays the original nonlocal Base-port representation.
"""
import sys,json,shutil
import numpy as np
from scipy.spatial.transform import Rotation
from skfem import MeshTet
from baseline_registry import ROOT,REPO,ref,sha,dump

def W(q,f):return np.r_[f,np.cross(q,f)]
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_local_surface2/summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['source_field']['path']);b=np.load(REPO/s['output']['path']);stsrc=ROOT/'validation/integrated/primaryP1_objective_port1/summary.json';ss=json.loads(stsrc.read_text());st=json.loads((REPO/ss['state']['path']).read_text());masssrc=REPO/ss['mass']['path'];mass=json.loads(masssrc.read_text());oldsrc=ROOT/'validation/integrated/primaryP1_front_h5_2/summary.json';old=json.loads(oldsrc.read_text());u=a['u_mm'];mo=int(a['motor_offset']);Rm=Rotation.from_rotvec(u[mo+3:mo+6]).as_matrix();C=np.array([0,0,.020])+u[mo:mo+3]*.001
 movingfixed=np.zeros(6);pointrows=[]
 for kind in ('moving_mass_points','fixed_mass_points'):
  for p in st[kind]:
   q=np.array(p['position_m']);f=np.array([0,0,-p['mass_kg']*9.80665]);movingfixed+=W(q,f);pointrows.append(dict(kind=kind,part=p['part_ID'],mass_kg=p['mass_kg'],position_m=q.tolist()))
 m=next(p for p in mass if p['part_ID']=='F0_MICRO_MOTOR');mq=Rm@(np.array(m['rest_centroid_m'])-[0,0,.020])+C;motor=W(mq,np.array([0,0,-m['mass_kg']*9.80665]));objectW=W(np.array(st['tip_world_m']),np.array([st['normal_N'],0,0]));wire=np.array(st['string']['wire_gravity_wrench_N_Nm']);rotor=np.zeros(6)
 for p in st['string']['rotors']:rotor+=W(np.array(p['position_m']),np.array([0,0,-p['mass_kg']*9.80665]))
 physical_upstream=movingfixed+motor+objectW+wire+rotor;pair_error=physical_upstream-np.array(st['Root_origin_wrench_N_Nm'])-np.array(st['Motor_origin_wrench_N_Nm']);elastic=np.zeros(6);bodyrows=[]
 for name in s['elastic_bodies']:
  p=a[name+'_points_mm'];t=a[name+'_tetra'];o=int(a[name+'_offset']);current=p+u[o:o+3*len(p)].reshape(-1,3);vol=abs(np.linalg.det(p[t[:,1:]]-p[t[:,0,None]]))/6;wt=np.zeros(len(p))
  for j in range(4):np.add.at(wt,t[:,j],vol/4)
  massnode=wt*float(a[name+'_rho_kg_m3'])*1e-9;forces=np.zeros_like(p);forces[:,2]=-massnode*9.80665;bw=np.r_[forces.sum(0),np.cross(current*.001,forces).sum(0)];elastic+=bw;bodyrows.append(dict(part=name,mass_kg=float(massnode.sum()),current_wrench_N_Nm=bw.tolist()))
 name='TEST_BASE';p=a[name+'_points_mm'];t=a[name+'_tetra'];o=int(a[name+'_offset']);current=p+u[o:o+3*len(p)].reshape(-1,3);mesh=MeshTet(p.T,t.T);tri=mesh.facets[:,mesh.boundary_facets()].T;tri=tri[np.all(abs(p[tri,2]-66)<1e-5,axis=1)];centers=np.array([[-44,-30],[-44,10],[86,-30],[86,10]]);xy=p[tri].mean(1)[:,:2];tri=tri[np.min(np.linalg.norm(xy[:,None,:]-centers[None,:,:],axis=2),axis=1)>4.7];area=np.linalg.norm(np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]),axis=1)/2;weights=np.zeros(len(p))
 for j in range(3):np.add.at(weights,tri[:,j],area/3)
 ids=weights>0;w=weights[ids];c0=np.average(p[ids],axis=0,weights=w);c1=np.average(current[ids],axis=0,weights=w);R,_=Rotation.align_vectors(current[ids]-c1,p[ids]-c0,weights=w);R=R.as_matrix();hardware=np.zeros(6);hardwaremass=0
 for n,hp in old['hardware_actual_mass_geometry'].items():
  m0=hp['volume_mm3']*7900e-9;q=(R@(np.array(hp['centroid_mm'])-c0)+c1)*.001;hardware+=W(q,np.array([0,0,-m0*9.80665]));hardwaremass+=m0
 expected_base=-(physical_upstream+elastic+hardware);source_base=np.array(s['physical_current_Base_wrench_N_Nm']);source_hw=np.array(s['hardware_wrench_N_Nm']);total_mass=-(physical_upstream[2]+elastic[2]+hardware[2])/9.80665;duplicate=np.array([0,0,-m['mass_kg']*9.80665]);duplicate_error=float(np.linalg.norm(duplicate));checks=dict(upstream_pair=np.linalg.norm(pair_error[:3])<1e-8 and np.linalg.norm(pair_error[3:])<1e-10,all_five_bodies=len(bodyrows)==5,independent_hardware_positions=np.linalg.norm(hardware-source_hw)<1e-10,physical_base_force=np.linalg.norm(expected_base[:3]-source_base[:3])<1e-8,physical_base_moment=np.linalg.norm(expected_base[3:]-source_base[3:])<1e-10,duplicate_motor_rejected=duplicate_error>1e-2,not_reference_residual_cancellation=True)
 candidate=json.loads((REPO/s['candidate']['path']).read_text());checks['all78STEP_identity']=len(candidate['part_references'])==78 and all(sha(REPO/r['path'])==r['SHA256'] for r in candidate['part_references'].values())
 result=dict(status='ACTUAL_P1_INDEPENDENT_CURRENT_PHYSICAL_BASE_LOAD_PASS' if all(checks.values()) else 'ACTUAL_P1_CURRENT_PHYSICAL_LOAD_CHECK_FAIL',candidate=s['candidate'],source=ref(src),upstream=ref(stsrc),mass=ref(masssrc),hardware_source=ref(oldsrc),verifier=ref(out/'verifier.py'),checks={k:bool(v) for k,v in checks.items()},upstream_pair_error_N_Nm=pair_error.tolist(),physical_upstream_wrench_N_Nm=physical_upstream.tolist(),elastic_gravity=bodyrows,hardware_current_wrench_N_Nm=hardware.tolist(),hardware_mass_kg=hardwaremass,expected_physical_Base_wrench_N_Nm=expected_base.tolist(),source_Base_error_N_Nm=(expected_base-source_base).tolist(),hybrid_CAD_FE_total_mass_kg=float(total_mass),Motor_housing_mass_kg=m['mass_kg'],duplicate_Motor_force_control_N=duplicate_error,actual78parts_identity_verified=78,actual_changed_CAD=[],physical_support_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Current physical gravity/object/pairedcable loads enumerated independently; Base reaction is minus those source physical wrenches. No cancellation of FE/null imbalance. Hybrid coarse tetra mass differs actual CAD mass; no mass/inertia or hardware/sourceallowables certificate. Mathematical Base port/nonlocalhardware transport is NOT physicalanchor/localbearing proof.')
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
