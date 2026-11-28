"""Fresh actual six socket helical clearances and necessary screw demands on final P1.
No preload/finite-contact stiffness or actual pin reaction is invented.
"""
import sys,json,math,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,translate,common,box,volume
from build_stage1 import rotate
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_splitpin61g/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()};groups=json.loads((REPO/cad['anchors']['path']).read_text())['groups'];rows=[]
for g in groups:
 keeper=parts[g['name']]
 for y in g['ys']:
  bn=next(n for n in parts if (n.startswith('F0_RF') and 'BOLT' in n if g['name'].startswith('ROOT') else n.startswith('MOTOR_CAP_BOLT')) and abs((bounds(parts[n])[0]+bounds(parts[n])[3])/2-g['x'])<1e-6 and abs((bounds(parts[n])[1]+bounds(parts[n])[4])/2-y)<1e-6)
  def pose(a):return translate(rotate(translate(parts[bn],-g['x'],-y,0),a),g['x'],y,.5*a/360)
  lo=0.;hi=10.;assert common(keeper,pose(lo))<=1e-8 and common(keeper,pose(hi))>1e-8
  for _ in range(20):
   assert not(ROOT/'runtime/STOP').exists();m=(lo+hi)/2
   if common(keeper,pose(m))>1e-8:hi=m
   else:lo=m
  rows.append(dict(bolt=bn,keeper=g['name'],socket_first_contact_deg=[lo,hi],clearance_screw_lead_mm=[.5*lo/360,.5*hi/360],nearest_index_max_abs_setting_error_mm=.5/12,backoff_only_max_setting_error_mm=.5/6,actual_installed_preload_N=None))
# Actual new tool window leaves 4x1.5mm bridge at Y4.25, not an ideal coupon.
root=parts['ROOT_SOCKET_KEEPER'];slicearea=common(root,box(58,4.2,1.9,10,.1,2))/.1
oldroot=read(REPO/json.loads((REPO/cad['parent']['path']).read_text())['part_references']['ROOT_SOCKET_KEEPER']['path']);removed=volume(oldroot)-volume(root)
cutp=ROOT/'validation/integrated/primaryP1_contacts61g/summary.json';cut=json.loads(cutp.read_text());cases=json.loads((cutp.parent/'rows.json').read_text());ports=json.loads((cutp.parent/'connector_ports.json').read_text())['ports'];demands=[]
for c in cases:
 if not(c['feasible'] and c['explicit_unknown_host_resultant_port']):continue
 for p in ports:
  if p['label'].startswith('through'):continue
  F=sum(q['coefficient_N'] for q in c['reactions'] if q['label']==p['label']);torque=F*.5/(2*math.pi);demands.append(dict(assumed_contact_mu=c['mu_ASSUMED'],port=p['label'],bolt=p['part_IDs'][0],required_axial_cut_N=F,required_head_torque_Nmm=torque,necessary_total_hex_normal_lower_bound_N=torque/(2.4/(2*math.sqrt(3))),actual_pin_reaction_N=None,actual_compliant_equilibrium=False))
checks=dict(actual83source_hashes=True,six_real_helical_brackets=len(rows)==6 and all(q['socket_first_contact_deg'][0]>0 for q in rows),actual_keeper_window_removed12_15mm3=abs(removed-12.15)<1e-6,actual_remaining_bridge_section6mm2=abs(slicearea-6)<1e-6,finite_nonnegative_necessary_demands=bool(demands) and all(q['required_axial_cut_N']>=0 and math.isfinite(q['required_head_torque_Nmm']) for q in demands))
dump(out/'summary.json',dict(status='ACTUAL_P1_WINDOW_SECTION_AND_HELICAL_SETTING_DEMAND_LOCAL_CHECK_NOT_INSTALLED_PRELOAD' if all(checks.values()) else 'ACTUAL_P1_WINDOW_OR_SETTING_CHECK_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),conditional_load_source=ref(cutp),checks=checks,helical_clearances=rows,new_root_window_removed_mm3=removed,remaining_actual_bridge_section_mm2=slicearea,necessary_cut_demands=demands,setting_qualified=False,pin_strength_qualified=False,installed_preload_N=None,finite_compliant_product_equilibria=0,whole_system_release=False,newly_qualified_system_gate_ids=[],next_mechanism='Resolve installed length/pretension with real axial adjustment and arbitrary-angle positive head restraint if60deg index cannot preserve it. Quantify source-compatible forming/pliers/clearances, keeper-window stress, split-pin contact/bending/axial stop and fullfinitehost before release. No headspin tie or axial spring substitute.'))
print(json.dumps(dict(checks=checks,helical_clearances=rows,actual_window_removed_mm3=removed,actual_bridge_section_mm2=slicearea,cut_demands=demands)));raise SystemExit(0 if all(checks.values()) else 2)
