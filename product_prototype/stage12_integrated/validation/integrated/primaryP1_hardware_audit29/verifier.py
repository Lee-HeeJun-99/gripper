"""Independent wrench LP and actual CAD transverse-clearance audit of P1 hardware.
Own gravity in tilted product poses cannot be hidden in an axial-only connector.
"""
import sys,json,time,shutil
import numpy as np
from scipy.optimize import linprog
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_gamma_attachment29 import cylinders
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

def cross(q):
 x,y,z=q;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
def block(q,f):return np.r_[f,np.cross(q*.001,f)]
def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py')
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());sp=ROOT/'validation/integrated/primaryP1_hardware_transfer29/summary.json';source=json.loads(sp.read_text());inp=json.loads((REPO/source['inputs']['path']).read_text());hp=REPO/inp['own_body_hardware_gravity']['path'];hardware={r['part_ID']:r for r in json.loads(hp.read_text())};qp=REPO/inp['actual_28patches']['path'];patches=json.loads(qp.read_text());bp=REPO/source['own_body_results']['path'];branches=json.loads(bp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
 dump(out/'inputs.json',dict(candidate=ref(cp),source=ref(sp),hardware=ref(hp),patches=ref(qp),branches=ref(bp),verifier=ref(out/'verifier.py'),dependencies=[ref(ROOT/'scripts/primary_gamma_attachment29.py')],policy='Independent full12row own-body wrench equations and HiGHS LP; fixed-world gravity, normals/centroids transform with common product pose. Sensitivity angles are not operating duty or capacity.'))
 inventory={};cases=[];geometries=[]
 for b in branches:
  assert not(ROOT/'runtime/STOP').exists();a=hardware[b['hardware_a']];bb=hardware[b['hardware_b']];pa=next(p for p in patches if p['branch']==b['branch'] and p['side']=='a');pb=next(p for p in patches if p['branch']==b['branch'] and p['side']=='b');bolt=a if 'BOLT' in a['part_ID'] else bb;bc=cylinders(read(REPO/bolt['STEP']['path']));shaft,sd=min(bc,key=lambda fd:fd[1]['radius_mm']);r=sd['radius_mm']
  for side,body in [('a',b['body_a']),('b',b['body_b'])]:
   if body not in inventory:inventory[body]=cylinders(read(REPO/cad['part_references'][body]['path']))
   candidates=[(f,d) for f,d in inventory[body] if abs(abs(d['axis'][2])-1)<1e-10 and np.linalg.norm(np.array(d['axis_point_mm'][:2])-b['thread_action_point_mm'][:2])<1e-8 and d['radius_mm']>=r-1e-9 and min(sd['bounds_mm'][5],d['bounds_mm'][5])-max(sd['bounds_mm'][2],d['bounds_mm'][2])>1e-8]
   assert candidates,(b['branch'],side,body);hole,hd=min(candidates,key=lambda fd:fd[1]['radius_mm']);clear=hd['radius_mm']-r;controls=[]
   for shift in [0.,clear*.5,clear,clear+.001]:
    ds=BRepExtrema_DistShapeShape(translate(shaft,0,shift,0),hole);ds.Perform();assert ds.IsDone();controls.append(dict(relative_shank_Y_mm=shift,analytic_signed_radial_gap_mm=clear-abs(shift),finite_surface_distance_mm=ds.Value()))
   geometries.append(dict(branch=b['branch'],side=side,body=body,bolt=bolt['part_ID'],shaft=sd,bore=hd,actual_radial_clearance_mm=clear,finite_axial_overlap_mm=min(sd['bounds_mm'][5],hd['bounds_mm'][5])-max(sd['bounds_mm'][2],hd['bounds_mm'][2]),controls=controls,friction_or_tie_assigned=False))
  for angle in [0.,.003,-.003]:
   R=Rotation.from_rotvec([angle,0,0]).as_matrix();axis=R[:,2];qa=np.array(pa['material_points_mm'])@R.T;qb=np.array(pb['material_points_mm'])@R.T;qt=R@b['thread_action_point_mm'];na=len(qa);nb=len(qb);A=np.zeros((12,na+nb+1))
   A[:3,:na]=axis[:,None];A[3:6,:na]=np.cross(qa*.001,axis).T;A[6:9,na:na+nb]=-axis[:,None];A[9:12,na:na+nb]=-np.cross(qb*.001,axis).T;A[:6,-1]=-block(qt,axis);A[6:,-1]=block(qt,axis)
   ga=block(R@a['centroid_mm'],[0,0,-a['conditional_mass_kg']*9.80665]);gb=block(R@bb['centroid_mm'],[0,0,-bb['conditional_mass_kg']*9.80665]);g=np.r_[ga,gb];sol=linprog(np.ones(A.shape[1]),A_eq=A,b_eq=-g,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});l=np.r_[R[:,1],np.zeros(3),R[:,1],np.zeros(3)];null=float(np.max(abs(l@A)));impossible=abs(float(l@g));res=float(np.max(abs(A@sol.x+g))) if sol.success else None
   cases.append(dict(branch=b['branch'],common_X_rotation_rad=angle,LP_success=bool(sol.success),LP_status=int(sol.status),LP_message=str(sol.message),max12row_residual_N_Nm=res,independent_left_null_error=float(null),independent_transverse_resultant_N=impossible,minimum12row_infinity_residual_N=impossible/float(np.linalg.norm(l,1)),expected_feasible=angle==0,pose_is_operating_demand=False,actual_failure_preserved=not sol.success if angle else False))
 dump(out/'actual_shank_bore_clearance.json',geometries);dump(out/'independent_12row_LP.json',cases)
 checks=dict(all28_finite_CAD_bores=len(geometries)==28 and all(g['finite_axial_overlap_mm']>0 and g['actual_radial_clearance_mm']>0 for g in geometries),all_CAD_surface_distance_controls=all(abs(c['finite_surface_distance_mm']-max(c['analytic_signed_radial_gap_mm'],0))<1e-7 for g in geometries for c in g['controls']),vertical_own_body_LP=all(c['LP_success'] and c['max12row_residual_N_Nm']<1e-8 for c in cases if c['expected_feasible']),tilted_own_body_FAIL_with_independent_witness=all(not c['LP_success'] and c['LP_status']==2 and c['independent_left_null_error']<1e-12 and c['independent_transverse_resultant_N']>1e-5 for c in cases if not c['expected_feasible']))
 dump(out/'summary.json',dict(status='ACTUAL_P1_VERTICAL_HARDWARE_LP_VERIFIED_TILTED_AXIAL_MODEL_REJECTED' if all(checks.values()) else 'ACTUAL_P1_HARDWARE_INDEPENDENT_AUDIT_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),checks=checks,results=cases,actual_geometry=ref(out/'actual_shank_bore_clearance.json'),raw_LP=ref(out/'independent_12row_LP.json'),elapsed_s=time.monotonic()-start,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,failures_preserved=sum(not c['LP_success'] for c in cases),limitations=['Independent reference-pose own28hardware gravity audit, no assembly equilibrium or product release. Nonzero gravity transverse to actual bolt axis cannot be balanced by any axial pressure distribution/thread tension.','All28actual adjacent holes have finite radial clearance; bore/shear contact may arise only after clearance closes. Next model must give bolt/nut their own translations/rotations, objective finite cylindrical contact, axial/flank/shear/tilt law and exact own gravity.','Cylindrical surface gaps are finite CAD checks, not complete all78part continuous surface transaction or deformable thread/strength certification. No assigned operating tilt/preload/friction/minimum.']))
 print(json.dumps(dict(checks=checks,failed_tilt_cases=sum(not c['LP_success'] for c in cases),clearance_mm=sorted(set(round(g['actual_radial_clearance_mm'],9) for g in geometries)))));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
