"""Saved parent19 motor-front unilateral geometry audit; no gauge is physical retention."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from primary_motor_bearing_wrenches import faces
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.TopAbs import TopAbs_IN,TopAbs_ON
from OCP.gp import gp_Pnt

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_chain0_h5_point1/summary.json';s=json.loads(src.read_text());f=np.load(REPO/s['field']['path']);cad=json.loads((REPO/s['candidate']['path']).read_text());motor=read(REPO/cad['part_references']['F0_MICRO_MOTOR']['path']);mf=faces(motor,1,-9.5);um=np.array(s['motor_rigid_translation_mm']);w=np.array(s['motor_rigid_rotation_rad']);C=np.array([0.,0,20.]);rows=[]
 for n in ['OPEN_FRAME','MOTOR_CAP']:
  p=f[n+'_points_mm'];o=int(f[n+'_offset']);u=f['u_mm'][o:o+3*len(p)].reshape(-1,3);ids=[]
  for i in np.flatnonzero(abs(p[:,1]+9.5)<1e-6):
   inside=False
   for face in mf:
    test=BRepClass_FaceClassifier(face,gp_Pnt(*map(float,p[i])),1e-6)
    if test.State() in (TopAbs_IN,TopAbs_ON):inside=True;break
   if inside:ids.append(int(i))
  assert ids,n
  ids=np.array(ids);pm=p[ids];disp=um+np.cross(np.broadcast_to(w,pm.shape),pm-C);gap=u[ids,1]-disp[:,1];rows.append(dict(part=n,samples=len(ids),gap_min_mm=float(gap.min()),gap_max_mm=float(gap.max()),negative_selected_gauge_nodes=int(sum(gap < -1e-9)),motor_backshift_to_remove_sampled_penetration_mm=max(0,float(-gap.min())),normal_on_motor=[0,-1,0]))
 # Adding a common infinitesimalrigidmotion to BOTHdisplacements cancels gap.
 common=np.cross(np.broadcast_to([.0001,-.0002,.0003],pm.shape),pm)+[.01,.02,.03];gauge=float(np.max(abs(((u[ids]+common)[:,1]-(disp+common)[:,1])-gap)))
 result=dict(status='ACTUAL_P1_OMITTED_FRONT_CONTACT_GAP_AUDIT_NOT_RELEASE',candidate=ref(ROOT/'cad/exports/primaryP1_retention20/summary.json'),parent_candidate=s['candidate'],source=ref(src),field=s['field'],producer=ref(out/'producer.py'),actual_front_plane_Y_mm=-9.5,rows=rows,common_gauge_gap_error_mm=gauge,solver_omitted_front_contacts=True,full_contact_validity=False,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Parent19savedsolveromittedactualMotorfrontYfaces; new20hardwaredoesnotchangethosefaces. Selectedgaugeconfigurationhasfrontpenetrationwhereindicated; this isNOTnewFEMsolve.','MotorfreeYmodecanbackshifttoopenunilateralfrontcontact; backshiftisundeterminedwithoutactualaxialload/retention/fullstringequilibrium. Negativegapsalone doNOTprove needfornewCADstop orcapacityfailure.','Sourceactualmotorcase/gearboxlandvalidity andcontactpressure stillunknown. Completeactualfrontcontactsetbeforeclaimingcoupled3Dequilibrium.','Nodalfinitegeometry audit,notsurfaceCCD,tolerance ormaterialapproval.'])
 dump(out/'summary.json',result);print(result)
if __name__=='__main__':main()
