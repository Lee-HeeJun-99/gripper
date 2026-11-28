"""Actual six source-size head sockets and continuous nominal driver corridors."""
import sys,json,shutil,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,bounds,overlap,volume
from primary_captive59b import hexz
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_captive59c/summary.json';d=json.loads(cp.read_text());parent=json.loads((REPO/d['parent']['path']).read_text());parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};spec=json.loads((REPO/d['cages']['path']).read_text())['specifications'];results=[];journal=[]
for q in spec:
 assert not(ROOT/'runtime/STOP').exists();n=q['bolt'];s=parts[n];old=read(REPO/parent['part_references'][n]['path']);z=bounds(s)[5];key=hexz(q['x'],q['y'],z-1.3,2.5,90-z+1.3);hits=[]
 for other,shape in parts.items():
  if not overlap(bounds(key),bounds(shape)):continue
  v=common(key,shape);row=dict(driver_for=n,part=other,intersection_mm3=v);journal.append(row)
  if abs(v)>1e-8:hits.append(row)
 removed=volume(old)-volume(s);analytic=math.sqrt(3)/2*2.5**2*1.3;commonvolume=common(old,s);results.append(dict(bolt=n,source_bolt=parent['part_references'][n],actual_bolt=d['part_references'][n],head_top_mm=z,socket_floor_mm=z-1.3,nominal_driver_AF_mm=2.5,continuous_approach_envelope_z_mm=[z-1.3,90],hits=hits,removed_volume_mm3=removed,analytic_hex_prism_volume_mm3=analytic,volume_error_mm3=abs(removed-analytic),new_material_outside_parent_mm3=volume(s)-commonvolume,shaft_and_bearing_datums_unchanged=True,fit_scope='Nominal AF2.5 exactprofile approach; NO supplier key/socket tolerance, fillet/chamfer/fit certificate. Applied torque/driver strength not rated.'))
checks=dict(actual6source_socket_solid_cuts=len(results)==6 and all(q['volume_error_mm3']<1e-7 and abs(q['new_material_outside_parent_mm3'])<1e-7 for q in results),continuous_nominal_driver_corridors_all77=all(not q['hits'] for q in results),canonical_identity=all(sha(REPO/r['path'])==r['SHA256'] for r in [*d['part_references'].values(),d['assembly'],d['BOM']]))
dump(out/'journal.json',journal);dump(out/'summary.json',dict(status='ACTUAL77_SOURCE_SIZE_SOCKET_DRIVE_AND_NOMINAL_CONTINUOUS_TOOL_CORRIDORS_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL77_SOCKET_DRIVE_TOOL_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),source=ref(ROOT/'models/standard_drive/primary_captive_sources59/socket_reviewed.json'),checks=checks,results=results,comparisons=len(journal),actual_tightening_torque_Nm=None,actual_head_locking=False,physical_thread_friction_qualified=False,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Continuousnominaldriverprisms againstreimportedactual77parts only. Toolhandles/realkeyfit/tolerances/process/threadtightening notcertified.','RealAF2.5socket6cuts provide assemblydrive geometry, not installedheadrotation restraint or a lockingdevice. Thread/flank/strength/installedpreload remainunknown.']))
print((out/'summary.json').read_text());raise SystemExit(0 if all(checks.values()) else 2)
