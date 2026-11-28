"""Independent actual BRep cage/assembly audit; screw spin is retained, no lock claim."""
import sys,json,math,shutil,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds,common,overlap,volume
from build_stage1 import rotate
from primary_anchor_contact38 import common_faces,surface_moment
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_captive59c/summary.json';d=json.loads(cp.read_text());old=json.loads((ROOT/'cad/exports/primaryP1_integral55e/summary.json').read_text());refs=d['part_references'];parts={n:read(REPO/r['path']) for n,r in refs.items()};spec=json.loads((REPO/d['cages']['path']).read_text())['specifications'];support=parts['BENCH_SUPPORT'];journal=[]
def query(label,a,b):
 assert not(ROOT/'runtime/STOP').exists();v=common(a,b) if overlap(bounds(a),bounds(b)) else 0.;journal.append(dict(label=label,intersection_mm3=v));return v
seats=[];backlash=[]
for q in spec:
 x,y,z=q['x'],q['y'],q['seat'];nut=parts[q['nut']];seat=sum(surface_moment(f)[0] for f in common_faces(nut,support,2,z));seats.append(dict(nut=q['nut'],area_mm2=seat))
 def posed(angle):return translate(rotate(translate(nut,-x,-y,0),angle),x,y,0)
 # Measured nonpenetrating/penetrating bracket, not arbitrary solid angle restraint.
 lo,hi=0.,30.
 v0=query(q['nut']+'_nominal',posed(0),support);vhi=query(q['nut']+'_30deg',posed(hi),support)
 for i in range(20):
  m=(lo+hi)/2;v=query(q['nut']+'_bisect_'+str(i),posed(m),support)
  if v>1e-8:hi=m
  else:lo=m
 opposite=query(q['nut']+'_negative_hi',posed(-hi-.001),support)
 backlash.append(dict(nut=q['nut'],positive_nonpenetration_deg=lo,positive_penetration_deg=hi,angle_bracket_deg=hi-lo,nominal_intersection_mm3=v0,high_intersection_mm3=vhi,opposite_intersection_mm3=opposite,meaning='First collision bracket at original1e-8mm3 threshold; no finite contact area/stiffness/strength at onset. Bolt screw rotation remains an independent DOF.'))
# Continuous AABB separation ONLY against new six cage material envelopes.
product=ROOT/'validation/integrated/primaryP1_product59c';assembly=json.loads((product/'assembly.json').read_text());finger=assembly['partition']['finger'];stages=[q for q in assembly['stages'] if q['stage']=='finger_lift_slide_lower'];continuous=[]
for k,(a,b) in enumerate(zip(stages,stages[1:])):
 aa=np.array(a['shift_mm']);bb=np.array(b['shift_mm'])
 for n in finger:
  boxn=np.array(bounds(parts[n]));lo=boxn[:3]+np.minimum(aa,bb);hi=boxn[3:]+np.maximum(aa,bb)
  for cage in spec:
   cl=np.array([cage['x']-5,cage['y']-5,cage['seat']-2.9]);ch=np.array([cage['x']+5,cage['y']+5,cage['seat']+.2]);sep=np.maximum(cl-hi,lo-ch);gap=float(sep.max());continuous.append(dict(segment=k,part=n,cage=cage['nut'],separation_bound_mm=gap,axis=int(sep.argmax()),clear=gap>=-1e-8))
# Added/removed support material is measured, all parent motor/root/key datums remain.
olds=read(REPO/old['part_references']['BENCH_SUPPORT']['path']);removed=volume(olds)-common(olds,support);added=volume(support)-common(olds,support)
checks=dict(actual77=len(refs)==77 and all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),d['assembly'],d['BOM']]),exactly11changed=sum(refs[n]!=old['part_references'][n] for n in refs)==11,six_positive_actual_axial_seats=len(seats)==6 and all(q['area_mm2']>0 for q in seats),all_cages_have_clearance_and_limit_rotation=all(q['nominal_intersection_mm3']<1e-8 and q['high_intersection_mm3']>1e-8 and q['opposite_intersection_mm3']>1e-8 for q in backlash),first_contact_brackets_refined=all(q['angle_bracket_deg']<.0001 for q in backlash),all_new_cage_continuous_finger_path_bounds=all(q['clear'] for q in continuous),fresh_full_product_checks=all(json.loads((product/'summary.json').read_text())['checks'].values()))
dump(out/'journal.json',journal);dump(out/'backlash.json',backlash);dump(out/'continuous_added_cage_separation.json',continuous);dump(out/'summary.json',dict(status='ACTUAL77_CAPTIVE_NUT_BACKLASH_AND_NEW_CAGE_PATH_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL77_CAPTIVE_NUT_CAGE_PATH_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),sources=[ref(ROOT/'models/standard_drive/primary_captive_sources59/reviewed.json')],checks={k:bool(v) for k,v in checks.items()},seats=seats,backlash=ref(out/'backlash.json'),continuous_added_cage_separation=ref(out/'continuous_added_cage_separation.json'),minimum_continuous_new_cage_gap_mm=min(q['separation_bound_mm'] for q in continuous),measured_added_support_volume_mm3=added,measured_removed_parent_material_mm3=removed,wholeassembly_finite_samples=ref(product/'summary.json'),bolt_head_rotation_fixed=False,thread_preload_or_friction_qualified=False,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Only added-cage envelopes versus actual piecewise-linear Finger assembly path have continuous separation proof. Original solids/wholeassembly remain finite samples, not fullCCD.','Nominal major-diameter thread envelopes do not model actual helical flanks; no supplier tolerance, friction/preload/strength or actualclamp certificate.','Cage rotational clearance and contact onset are not finite-area pressure/capacity. All original22system criteria unchanged.']))
print((out/'summary.json').read_text());raise SystemExit(0 if all(checks.values()) else 2)
