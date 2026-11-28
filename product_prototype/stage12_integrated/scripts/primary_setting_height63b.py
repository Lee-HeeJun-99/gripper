"""Actual P1 STEP headheight process envelope. No measured setting or preload.
Pure axial contrasts deliberately isolate height uncertainty from screw lead.
"""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate
from build_stage1 import rotate
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
cp=ROOT/'cad/exports/primaryP1_clocked62a/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());settings=json.loads((REPO/cad['settings']['path']).read_text())['settings'];rows=[]
def spin(s,x,y,a):return translate(rotate(translate(s,-x,-y,0),a),x,y,0)
for q in settings:
 b=read(REPO/refs[q['bolt']]['path']);k=read(REPO/refs[q['keeper']]['path']);br=[]
 for sign in [-1,1]:
  lo=0.;hi=3.;assert common(k,b)<=1e-8 and common(k,translate(b,0,0,sign*hi))>1e-8
  for _ in range(22):
   assert not(ROOT/'runtime/STOP').exists();m=(lo+hi)/2
   if common(k,translate(b,0,0,sign*m))>1e-8:hi=m
   else:lo=m
  br.append(dict(direction=sign,first_interference_height_mm=[lo,hi]))
 tests=[]
 for a,z in [(0,-.04),(0,-.06),(0,1.9),(0,2.1),(4,-.04),(4,1.9),(5,0)]:
  v=common(k,translate(spin(b,q['x'],q['y'],a),0,0,z));tests.append(dict(angular_error_deg=a,height_error_mm=z,intersection_mm3=v,clear=v<=1e-8))
 rows.append(dict(bolt=q['bolt'],keeper=q['keeper'],brackets=br,contrasts=tests,measured_height_mm=None,measured_preload_N=None))
checks=dict(six_pairs=len(rows)==6,all_nominal_pairs_clear=all(common(read(REPO/refs[q['bolt']]['path']),read(REPO/refs[q['keeper']]['path']))<=1e-8 for q in settings),all_signed_brackets_resolved=all(b['first_interference_height_mm'][1]-b['first_interference_height_mm'][0]<2e-7 for r in rows for b in r['brackets']),negative_height_control_rejected=all(not r['contrasts'][1]['clear'] for r in rows),positive_height_control_rejected=all(not r['contrasts'][3]['clear'] for r in rows),angular_control_rejected=all(not r['contrasts'][-1]['clear'] for r in rows))
dump(out/'summary.json',dict(status='ACTUAL_P1_AXIAL_SETTING_PROCESS_ENVELOPE_NOT_PRELOAD' if all(checks.values()) else 'ACTUAL_P1_AXIAL_PROCESS_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),settings=cad['settings'],checks=checks,rows=rows,minimum_negative_height_margin_mm=min(b['first_interference_height_mm'][0] for r in rows for b in r['brackets'] if b['direction']==-1),minimum_positive_height_margin_mm=min(b['first_interference_height_mm'][0] for r in rows for b in r['brackets'] if b['direction']==1),actual_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Actual reimported bolt/keeper geometry; each bolt translated independently as a manufacturing uncertainty contrast, not a solved screw/preload state','Nominal hard interference budget excludes real cutter radius, shape/angular error, finish, tolerance, elastic deflection, nut and pin play','Synthetic angles remain unmeasured; no hardware or supplier/process qualification; physical DOFs retained']))
print(json.dumps(dict(checks=checks,rows=rows)));raise SystemExit(0 if all(checks.values()) else 2)
