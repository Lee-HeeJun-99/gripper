"""Independent setting/registration audit on actual clocked product STEP solids."""
import sys,json,shutil,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,bounds,volume
from build_stage1 import rotate
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_clocked62a/summary.json';d=json.loads(cp.read_text());parent=json.loads((REPO/d['parent']['path']).read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};settings=json.loads((REPO/d['settings']['path']).read_text())['settings'];rows=[]
def spin(s,x,y,a):return translate(rotate(translate(s,-x,-y,0),a),x,y,0)
for q in settings:
 b=parts[q['bolt']];k=parts[q['keeper']];oldk=read(REPO/parent['part_references'][q['keeper']]['path']);x,y=q['x'],q['y'];baseline=read(REPO/parent['part_references'][q['bolt']]['path']);br=[]
 for sign in [-1,1]:
  def pose(a):return translate(spin(b,x,y,sign*a),0,0,sign*.5*a/360)
  lo=0.;hi=10.;assert common(k,pose(0))<=1e-8 and common(k,pose(hi))>1e-8
  for _ in range(20):
   assert not(ROOT/'runtime/STOP').exists();m=(lo+hi)/2
   if common(k,pose(m))>1e-8:hi=m
   else:lo=m
  br.append(dict(sign=sign,first_contact_deg=[lo,hi],free_screw_lead_mm=[lo*.5/360,hi*.5/360]))
 # Pure nominal custom registration has no axial shift, but finite free mode remains.
 rows.append(dict(**q,original_indexed_keeper_intersection_mm3=common(oldk,b),new_clocked_intersection_mm3=common(k,b),bolt_volume_relative_change=abs(volume(b)/volume(baseline)-1),bolt_z_bounds_change_mm=[bounds(b)[i]-bounds(baseline)[i] for i in [2,5]],helical_contact_brackets=br,measured_installed_preload_N=None))
checks=dict(six_actual_bolt_keeper_pairs=len(rows)==6,original_common_index_rejects_nonindexed_poses=all(r['original_indexed_keeper_intersection_mm3']>1e-8 for r in rows),individually_clocked_pairs_clear=all(r['new_clocked_intersection_mm3']<=1e-8 for r in rows),zero_axial_reset=all(max(map(abs,r['bolt_z_bounds_change_mm']))<1e-9 for r in rows),bolt_material_unchanged=all(r['bolt_volume_relative_change']<1e-9 for r in rows),positive_clearance_both_screw_directions=all(b['first_contact_deg'][0]>0 for r in rows for b in r['helical_contact_brackets']))
# Angular input/process uncertainty is evaluated against actual contact brackets,
# never treated as a material/measurement tolerance certificate.
margin=min(b['first_contact_deg'][0] for r in rows for b in r['helical_contact_brackets']);uncertainty=[dict(total_angular_error_deg=a,nominal_geometric_registration_bound=a<margin,axial_screw_lead_equivalent_mm=.5*a/360) for a in [1,2,4,5]]
dump(out/'summary.json',dict(status='ACTUAL_P1_INDIVIDUAL_CLOCKING_REGISTRATION_LOCAL_CHECK_NOT_PRELOAD' if all(checks.values()) else 'ACTUAL_P1_CLOCKING_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),settings=d['settings'],checks=checks,rows=rows,angular_uncertainty_contrasts=uncertainty,min_free_angle_deg=margin,manufacturing_proposal='Measure six final installed angles/heights, individually machine monolithic keepers, install without changing bolt setting. These synthetic poses demonstrate nominal geometry only. Supplier/tool/process and actual preload unresolved.',accepted_physical_product_equilibria=0,whole_system_release=False,newly_qualified_system_gate_ids=[],next_mechanism='Quantify6DOF keeper/tongue/pin compliance and actual helical head/nut/cagecontacts; qualify measure-to-machine angular/height process and source-minima. Do not use zero nominal axial reset as preload certification.'))
print(json.dumps(dict(checks=checks,margin=margin,rows=rows)));raise SystemExit(0 if all(checks.values()) else 2)
