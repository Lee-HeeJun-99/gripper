"""Actual P1 pin/Root-local gamma geometry and conditional source virtual work.
No global fixation or sourcefield. Backlash/clearance is measured from exact CAD.
"""
import sys,json,time,shutil
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_local_gamma29 import LocalGammaString
from primary_local_finger29 import solve
from primary_finite_port import ObjectiveRootPort
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

def cylinders(s):
 out=[];it=TopExp_Explorer(s,TopAbs_FACE)
 while it.More():
  f=TopoDS.Face_s(it.Current());a=BRepAdaptor_Surface(f)
  if a.GetType()==GeomAbs_Cylinder:
   c=a.Cylinder();q=c.Location();d=c.Axis().Direction()
   out.append((f,dict(radius_mm=c.Radius(),axis_point_mm=[q.X(),q.Y(),q.Z()],axis=[d.X(),d.Y(),d.Z()],bounds_mm=bounds(f))))
  it.Next()
 return out

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==78 and all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
 src=ROOT/'validation/integrated/primaryP1_fresh_sources28/summary.json';old=json.loads(src.read_text());mass=ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json';points=json.loads(mass.read_text());seedpath=ROOT/'validation/finger/primaryP1_gravity_cat_demand32_2/cases.json';seed=json.loads(seedpath.read_text())[0]
 ms=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(ms.read_text());shapes={n:read(REPO/cad['part_references'][n]['path']) for n in ['F0_ROOT_BACK','F0_ROOT_FRONT','F0_RAIL_L','F0_RAIL_R']};pinfaces=cylinders(shapes['F0_ROOT_BACK']);geometry=[]
 for n,y in [('F0_ROOT_FRONT',-10),('F0_ROOT_FRONT',10),('F0_RAIL_L',-10),('F0_RAIL_R',10)]:
  pin,pd=next((f,d) for f,d in pinfaces if abs(d['radius_mm']-1)<1e-10 and abs(d['axis_point_mm'][1]-y)<1e-10 and abs(d['axis_point_mm'][2]-1)<1e-10 and abs(d['axis'][0]-1)<1e-10)
  hole,hd=next((f,d) for f,d in cylinders(shapes[n]) if abs(d['radius_mm']-1.05)<1e-10 and abs(d['axis_point_mm'][1]-y)<1e-10 and abs(d['axis_point_mm'][2]-1)<1e-10)
  rows=[]
  for gamma in [0,.025,.049,.05,.051,-.051]:
   moved=translate(hole,0,gamma,0);distance=BRepExtrema_DistShapeShape(pin,moved);distance.Perform();assert distance.IsDone()
   signed=hd['radius_mm']-pd['radius_mm']-abs(gamma)
   rows.append(dict(gamma_mm=gamma,analytic_signed_radial_gap_mm=signed,finite_CAD_face_distance_mm=distance.Value(),actual_part_overlap_mm3=common(shapes['F0_ROOT_BACK'],translate(shapes[n],0,gamma,0))))
  geometry.append(dict(part=n,pin=pd,hole=hd,clearance_mm=hd['radius_mm']-pd['radius_mm'],finite_axial_overlap_mm=min(pd['bounds_mm'][3],hd['bounds_mm'][3])-max(pd['bounds_mm'][0],hd['bounds_mm'][0]),samples=rows))
 dump(out/'pin_hole_geometry.json',geometry)
 deps=['primary_local_gamma29','primary_local_finger29','primary_prescribed_string28','primary_prescribed_finger28','primary_seated_string','primary_spatial_string','primary_support_feedback','primary_terminal_corner_v2','primary_finger_tangent_v5','primary_gravity_pullback','primary_gravity_swivel','primary_finite_port','primary_finger_equilibrium_v5','rod_point_jacobian']
 dump(out/'inputs.json',dict(candidate=ref(cp),prior_source=ref(src),mass_points=ref(mass),seed=ref(seedpath),fivebody=ref(ms),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/f'scripts/{n}.py') for n in deps],actual_attachment_geometry=ref(out/'pin_hole_geometry.json'),scope='Conditional frictionless Root-local Y backlash only; not a complete 3D clamp or an accepted support state. Original criteria unchanged.'))
 cases=[];states={};pullbacks={};work=[]
 for name,angle,gamma in [('reference',0,0),('reference_plus',0,.00001),('tilt_minus',.003,-.05),('tilt_zero',.003,0),('tilt_plus',.003,.05),('tilt_work',.003,.025)]:
  assert not(ROOT/'runtime/STOP').exists();R=Rotation.from_rotvec([angle,0,0]).as_matrix();C=R@np.array([0,0,.020]);E=R@np.array([seed['cable_end_m'][0],0,seed['cable_end_m'][1]])
  initial=LocalGammaString(points,R,C,E,.01125,gamma,16,axis=R[:,1]).solve(seed);parent=dict(root_R=R.tolist(),root_translation_m=[0,0,0],motor_R=R.tolist(),motor_C_m=C.tolist(),actual_wire_center_radius_m=.01125,actual=initial)
  r=solve(parent,seed,points,gamma);q=r['upstream_gamma_generalized_force_N'];axis=R[:,1];F=np.array(r['string']['Fe_N']);objectF=np.array([r['normal_N'],0,0]);mg=sum(p['mass_kg'] for p in r['moving_mass_points']+r['fixed_mass_points']);gravity=np.array([0,0,-mg*9.80665]);independent=float(axis@(F+objectF+gravity));dy=axis*gamma*.001
  position_error=float(np.linalg.norm(np.array(r['string']['E_m'])-(R@np.array([*(R.T@(np.array(r['string']['E_m'])-dy))[:1],0.,(R.T@(np.array(r['string']['E_m'])-dy))[2]])+dy)))
  # Same underlying forces independently paired with finite Root-port positions.
  if name=='tilt_work':
   positions=np.array([r['string']['E_m'],r['tip_world_m']]+[p['position_m'] for p in r['moving_mass_points']+r['fixed_mass_points']]);forces=np.array([F,objectF]+[[0,0,-p['mass_kg']*9.80665] for p in r['moving_mass_points']+r['fixed_mass_points']]);gamma0=gamma
   local=(positions-dy)@R
   for mr in model['results']:
    a=np.load(REPO/mr['reference_model']['path']);p=a['F0_ROOT_BACK_points_mm'];w=a['Root_port_weights_mm2'];ids=np.flatnonzero(w);port=ObjectiveRootPort(p[ids],w[ids]);u=p[ids]@R.T-p[ids];W=np.array(r['Root_origin_wrench_N_Nm']);ff=port.pullback(u,W);v=np.tile([.002,-.001,.003],(len(ids),1))+np.cross(np.tile([.0002,-.0003,.0001],(len(ids),1)),p[ids]);dg=.002;eps=1e-3
    def world(uu,gg):return port.positions(uu,local+np.array([0,gg*.001,0]))
    # Procrustes reference center maps rotate around origin, so local is the CAD frame.
    numerical=(world(u+eps*v,gamma0+eps*dg)-world(u-eps*v,gamma0-eps*dg))/(2*eps)*1000
    expected=float(np.sum(forces*numerical));actual=float(np.sum(ff*v)+q*dg)
    # Reconstruct pose and each actual transformed upstream point before work test.
    pose_error=float(np.max(abs(world(u,gamma0)-positions)))
    work.append(dict(mesh_level=mr['mesh_level'],position_error_m=pose_error,analytical_work_Nmm=actual,finite_difference_work_Nmm=expected,error_Nmm=abs(actual-expected),Root_nodes=len(ids),Root_modes_not_fixed=True,gamma_not_eliminated=True))
    f=np.zeros(len(a['reference_coordinates_mm']));off=int(a['F0_ROOT_BACK_offset']);f[off+3*ids[:,None]+np.arange(3)]=ff;f[int(a['upstream_freeY_offset'])]=q;pullbacks[f'h{mr["mesh_level"]}_root_gamma_source_N']=f
  curves={k:r['string'].pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')};dump(out/f'{name}_curves.json',curves);dump(out/f'{name}_source.json',r)
  cases.append(dict(case=name,root_motor_common_X_rotation_rad=angle,gamma_local_mm=gamma,root_local_axis=axis.tolist(),gamma_force_N=q,string_gamma_force_N=float(axis@F),gravity_gamma_force_N=float(axis@gravity),object_gamma_force_N=float(axis@objectF),independent_Q_error_N=abs(q-independent),legacy_worldY_force_N=float(F[1]),legacy_Q_error_N=abs(float(F[1])-q),conditional_normal_N=r['normal_N'],source_checks=r['checks'],signed_pin_gap_mm=.05-abs(gamma),source=ref(out/f'{name}_source.json'),full_support_equilibrium=False));states[name]=r
 np.savez_compressed(out/'root_local_gamma_pullbacks.npz',**pullbacks)
 checks=dict(actual_four_pin_hole_pairs=len(geometry)==4 and all(g['finite_axial_overlap_mm']>0 and abs(g['clearance_mm']-.05)<1e-10 for g in geometry),finite_CAD_gap_controls=all(abs(r['finite_CAD_face_distance_mm']-max(0,r['analytic_signed_radial_gap_mm']))<1e-7 for g in geometry for r in g['samples']),physical_overlap_beyond_clearance=all(r['actual_part_overlap_mm3']>1e-9 for g in geometry for r in g['samples'] if abs(r['gamma_mm'])>.05),all_fresh_conditional_source_checks=all(all(c['source_checks'].values()) for c in cases),local_generalized_force=all(c['independent_Q_error_N']<1e-12 for c in cases),old_worldY_error_exposed=max(c['legacy_Q_error_N'] for c in cases)>1e-5,finite_Root_gamma_virtual_work=all(w['error_Nmm']<1e-8 and w['position_error_m']<1e-12 for w in work),zero_pose_original_normal=abs(cases[0]['conditional_normal_N']-old['results'][0]['normal_N'])<1e-8)
 dump(out/'summary.json',dict(status='ACTUAL_P1_LOCAL_GAMMA_PIN_CLEARANCE_AND_SOURCE_WORK_VERIFIED_NOT_ATTACHMENT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_LOCAL_GAMMA_ATTACHMENT_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),checks=checks,geometry=ref(out/'pin_hole_geometry.json'),results=cases,finite_work=work,pullbacks=ref(out/'root_local_gamma_pullbacks.npz'),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,limitations=['0.05mm clearance is exact nominal CAD geometry, not a relaxed force/gap criterion or manufactured fit certificate. Existing source ideal XZ clamp remains conditional; radial Z, relative rotations, axial preload/friction and finite pin elasticity/material strength absent.','Local Y is a relative upstream-group mode, not an artificial grounded support. Pin reaction can arise only at closed radial gap; open gap pressure remains zero. No actual full support equilibrium or pin reaction certified.','Fresh source gravity/generalized force and virtual work verified; full3DFinger, global energy, operating demand, mesh/time/strength/anchor/all22 gates remain unqualified.','Historical world-Y sources and manifests preserved; no global Y elimination, hidden spring, old field transfer or Base cancellation.']))
 print(json.dumps(dict(checks=checks,results=cases,work=work)));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
