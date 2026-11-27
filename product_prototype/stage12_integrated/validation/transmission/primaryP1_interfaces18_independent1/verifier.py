"""Independent reimported contact derivative, saved forces and virtual-work audit."""
import json,sys,shutil,copy
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def props(s):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);c=p.CentreOfMass();return p.Mass(),np.array([c.X(),c.Y(),c.Z()])
def W(p,f):return np.r_[f,np.cross(np.array(p)*.001,f)]
def gw(s,rho):
 v,c=props(s);return W(c,[0,0,-v*1e-9*rho*9.80665])
def residual(row,rays):
 external=np.array(row['external_wrench_N_Nm']);total=np.zeros_like(external)
 for ray in rays:
  f=np.array(ray['direction'])*ray['force_N'];w=W(ray['point_mm'],f)
  if len(total)==6:total+=w
  elif ray['label']=='bolt_axial':total[6:]+=w
  else:
   total[:6]+=w
   if ray['label']=='motor_top':total[6:]-=w
 return (total+external).reshape(-1,6)
def main():
 out=ROOT/'validation/transmission'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'cad/exports/primaryP1_interfaces18/summary.json';c=json.loads(src.read_text());vsrc=ROOT/'validation/transmission/primaryP1_interfaces18_wrench1/summary.json';v=json.loads(vsrc.read_text());rows=json.loads((REPO/v['tractions']['path']).read_text());patch=json.loads((REPO/v['patches']['path']).read_text());s={n:read(REPO/c['part_references'][n]['path']) for n in ['F0_ROOT_BACK','OPEN_FRAME','F0_MICRO_MOTOR','MOTOR_CAP']}
 areas=[]
 for label,a,b,d in [('root_seat','F0_ROOT_BACK','OPEN_FRAME',[0,0,-1]),('existing_wall','F0_ROOT_BACK','OPEN_FRAME',[1,0,0]),('motor_xmin','F0_MICRO_MOTOR','OPEN_FRAME',[-1,0,0]),('motor_xmax','F0_MICRO_MOTOR','OPEN_FRAME',[1,0,0]),('motor_bottom','F0_MICRO_MOTOR','OPEN_FRAME',[0,0,-1]),('motor_top','F0_MICRO_MOTOR','MOTOR_CAP',[0,0,1])]:
  expected=v['areas_mm2'][label];est=[]
  for h in (.001,.002):est.append(common(s[b],translate(s[a],*(np.array(d)*h)))/h)
  areas.append(dict(label=label,finite_face_area_mm2=expected,independent_overlap_derivative_mm2=est,relative_error=max(abs(x/expected-1) for x in est)))
 load=ROOT/'validation/transmission/primaryP1_gravity_cat_demand_ports2/summary.json';l=json.loads(load.read_text())['rows'][0];rw=np.array(l['Root_force_couple_XYZ_N_Nm']);rw[3:]+=np.cross(l['Root_reference_m'],rw[:3]);rw+=gw(s['F0_ROOT_BACK'],7900);mw=np.array(l['Motor_force_couple_XYZ_N_Nm']);mw[3:]+=np.cross(l['Motor_reference_m'],mw[:3]);cw=gw(s['MOTOR_CAP'],2700)
 expected={'root':rw,'motor_and_cap':np.r_[mw,cw]};audit=[]
 for name in expected:
  row=rows[name];err=residual(row,row['rays']);rays=copy.deepcopy(row['rays']);rays[0]['force_N']+=.01;bad=residual(row,rays);rng=np.random.default_rng(20261127);vw=[]
  for k in range(12):
   # Direct rigid point velocity dx + omega cross r, independently of wrench matrices.
   twists=rng.normal(size=(len(expected[name])//6,6));work=0
   for ray in row['rays']:
    force=np.array(ray['direction'])*ray['force_N'];p=np.array(ray['point_mm'])*.001
    def velocity(t):return t[:3]+np.cross(t[3:],p)
    if name=='root':work+=force@velocity(twists[0])
    elif ray['label']=='bolt_axial':work+=force@velocity(twists[1])
    else:
     work+=force@velocity(twists[0])
     if ray['label']=='motor_top':work-=force@velocity(twists[1])
   work+=float(np.sum(expected[name].reshape(-1,6)*twists));vw.append(abs(work))
  audit.append(dict(name=name,external_reconstruction_error=float(np.max(abs(expected[name]-np.array(row['external_wrench_N_Nm'])))),force_error_N=float(np.linalg.norm(err[:,:3],axis=1).max()),moment_error_Nm=float(np.linalg.norm(err[:,3:],axis=1).max()),virtual_work_error_max=float(max(vw)),corrupt_10mN_rejected=bool(np.linalg.norm(bad[:,:3],axis=1).max()>1e-8),nonnegative_forces=all(r['force_N']>=0 for r in row['rays']),actual_pressure_force=all(r['pressure_MPa'] is None or abs(r['pressure_MPa']*r['area_mm2']-r['force_N'])<1e-12 for r in row['rays'])))
 oldsrc=ROOT/'cad/exports/primaryP1_fixture15/summary.json';old=json.loads(oldsrc.read_text());oldframe=read(REPO/old['part_references']['OPEN_FRAME']['path']);delta=gw(s['OPEN_FRAME'],2700)-gw(oldframe,2700);dv=props(s['OPEN_FRAME'])[0]-props(oldframe)[0];mass_delta=dv*2700e-9;oldtotal=l['total_mass_kg'];required=np.array(l['required_Base_external_wrench_N_Nm'])-delta
 unchanged=[n for n,r in c['part_references'].items() if r==old['part_references'][n]]
 checks=dict(areas=max(a['relative_error'] for a in areas)<1e-6,force=all(a['force_error_N']<1e-8 for a in audit),moment=all(a['moment_error_Nm']<1e-10 for a in audit),external_reconstructed=all(a['external_reconstruction_error']<1e-12 for a in audit),rigid_virtual_work=all(a['virtual_work_error_max']<1e-10 for a in audit),negative_control=all(a['corrupt_10mN_rejected'] for a in audit),positive_pressure=all(a['nonnegative_forces'] and a['actual_pressure_force'] for a in audit),only_frame_changed=len(unchanged)==77,source_hashes=all(sha(REPO/r['path'])==r['SHA256'] for r in c['part_references'].values()))
 result=dict(status='ACTUAL_P1_MOTOR_BEARING_INDEPENDENT_VERIFY_PASS' if all(checks.values()) else 'ACTUAL_P1_MOTOR_BEARING_INDEPENDENT_VERIFY_FAIL',candidate=ref(src),source=ref(vsrc),verifier=ref(out/'verifier.py'),checks=checks,areas=areas,saved_field_audit=audit,unchanged_parts=unchanged,frame_added_volume_mm3=dv,conditional_mass_delta_kg=mass_delta,new_total_conditional_mass_kg=oldtotal+mass_delta,frame_delta_gravity_wrench_N_Nm=delta.tolist(),updated_required_Base_external_wrench_N_Nm=required.tolist(),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Exact nominal finite-face necessary equilibrium,not elastic pressure distribution,capacity or manufacturing fit','Final18onlyFramechanged: previousgravity-loadedFinger/freeSwivel/stringstate remains conditionalsameundeformedboundary; upstreamcoupledFramecompliance unresolved','RequiredBasewrench updated for exact changedFramevolume/centroid at rho2700 only; not physicalbenchanchor or completeequilibrium','KeylessRoot wall handles thispositiveFx; reverse/shearYloadcases and offnominalgap require separatephysicalcontactvalidation','Initial17wrench omitted160mm2existingwall: itsrootkeynecessityclaim invalidated by wallaudit. Allbytespreserved'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
