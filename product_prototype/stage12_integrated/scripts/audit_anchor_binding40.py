"""Independent actual bolt CAD-to-column geometry and finite-stack dimensional audit.
No producer, FE assembler or optimizer import. Does not qualify threaded joints.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from primary_motor_bearing_wrenches import faces
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def props(s):
 g=GProp_GProps();BRepGProp.SurfaceProperties_s(s,g);q=g.CentreOfMass();return g.Mass(),np.array([q.X(),q.Y(),q.Z()])
def common(a,b,z):
 areas=[];points=[]
 for x in faces(a,2,z):
  for y in faces(b,2,z):
   ar,q=props(BRepAlgoAPI_Common(x,y).Shape())
   if ar>1e-8:areas.append(ar);points.append(q)
 return sum(areas),sum((a*q for a,q in zip(areas,points)),np.zeros(3))/sum(areas)
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated'/sys.argv[2];doc=json.loads((src/'summary.json').read_text());cad=json.loads((REPO/doc['candidate']['path']).read_text());geo=json.loads((REPO/doc['geometry']['path']).read_text());ops=np.load(REPO/doc['operators']['path']);arrays=[np.load(REPO/r['path']) for r in doc['fields']];nc=doc['contact_variables'];shapes={n:read(REPO/r['path']) for n,r in cad['part_references'].items() if n in ('TEST_BASE','BENCH_ANCHOR_RAIL') or n.startswith('ANCHOR_')};reports=[]
 for i in range(3):
  label='bolt'+str(i);j=next(j for j,p in enumerate(geo['patches']) if p['label']==label);bolt=shapes['ANCHOR_BOLT_'+str(i)];nut=shapes['ANCHOR_NUT_'+str(i)];bb=bounds(bolt);nb=bounds(nut);ar0,q0=common(shapes['TEST_BASE'],bolt,60);ar1,q1=common(shapes['BENCH_ANCHOR_RAIL'],nut,74);errors=[];wrenches=[]
  for k,(area,q,d) in enumerate([(ar0,q0,np.array([0,0,1.])),(ar1,q1,np.array([0,0,-1.]))]):
   a=arrays[k];f=np.zeros_like(a['F'][:,j]);journal=geo['body_quadrature'][k][j];total=sum(v['area_mm2'] for v in journal['quadrature']);center=np.zeros(3)
   for v in journal['quadrature']:
    center+=v['area_mm2']*np.array(v['point_mm'])/total
    for node,bary in zip(v['nodes'],v['barycentric']):f[3*node:3*node+3]+=d*bary*v['area_mm2']/total
   actual=a['F'][:,j];ff=actual.reshape(-1,3);w=np.r_[ff.sum(0),np.cross(a['points_mm'],ff).sum(0)];wrenches.append(w.tolist());errors.append(dict(column_N=float(abs(f-actual).max()),actual_face_area_mm2=area,mapped_area_mm2=total,area_difference_mm2=abs(total-area),centroid_difference_mm=float(np.linalg.norm(q-center)),direction_N=float(np.linalg.norm(w[:3]-d))))
  grip=q1[2]-q0[2];pitch=.8;major=5.;basic_minor=major-1.226869*pitch;stress_d=major-.9382*pitch;E=200000.;nominal=grip/(E*np.pi*major**2/4);core=grip/(E*np.pi*basic_minor**2/4);stress=grip/(E*np.pi*stress_d**2/4);forces=[r['contact_forces_N'][j] for r in doc['rows'] if 'contact_forces_N' in r]
  reports.append(dict(actual_bolt_ID='ANCHOR_BOLT_'+str(i),actual_nut_ID='ANCHOR_NUT_'+str(i),variable_index=j,bolt_bounds_mm=bb,nut_bounds_mm=nb,actual_head_seat_mm=q0.tolist(),actual_nut_seat_mm=q1.tolist(),actual_grip_mm=grip,head_height_mm=60-bb[2],nut_envelope_height_mm=nb[5]-nb[2],thread_envelope_projection_mm=bb[5]-nb[5],nominal_full_nut_overlap_mm=min(bb[5],nb[5])-max(60.,nb[2]),force_columns=errors,wrenches_N_Nmm=wrenches,conditional_nominal_shank_compliance_mm_N=nominal,stored_spring_mm_N=float(ops['spring_mm_N'][j]),basic_profile_NOT_tolerance_core_diameter_mm=basic_minor,conditional_core_only_compliance_mm_N=core,conditional_stress_area_compliance_mm_N=stress,core_to_major_compliance_ratio=core/nominal,maximum_trial_tension_N=max(forces),conditional_basic_core_axial_stress_MPa=max(forces)/(np.pi*basic_minor**2/4),physical_stack_qualified=False,unresolved=['Actual thread tolerance/root/helix geometry and source minimum core','Finite head socket bending/contact, nut flank engagement/load distribution','Installed rest length/preload/locking and source-backed material minima','Receiver to external-support attachment and physical operating sourcefield']))
 checks=dict(all85STEP_hashes=all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values()),bolt_columns_geometry_bound=all(e['column_N']<1e-12 and e['direction_N']<1e-10 and e['centroid_difference_mm']<1e-7 and e['area_difference_mm2']<1e-7 for r in reports for e in r['force_columns']),actual_grip_matches_conditional_spring=all(abs(r['stored_spring_mm_N']-r['conditional_nominal_shank_compliance_mm_N'])<1e-18 for r in reports),all_actual_bolt_indices_last3=[r['variable_index'] for r in reports]==list(range(nc-3,nc)))
 dump(out/'summary.json',dict(status='ACTUAL_P1_GEOMETRY_COLUMN_BINDING_PASS_PHYSICAL_STACK_BLOCKED' if all(checks.values()) else 'ACTUAL_P1_GEOMETRY_COLUMN_BINDING_FAIL',candidate=doc['candidate'],source=ref(src/'summary.json'),verifier=ref(out/'verifier.py'),checks=checks,bolts=reports,core_formula_status='Explicit basic metric-profile geometric sensitivity only;not tolerance-minimum or source-qualified connector law. Pitch from existing reviewed dimensional source.',dimensional_source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),physical_stack_qualified=False,newly_qualified_system_gate_ids=[],whole_system_release=False));print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
