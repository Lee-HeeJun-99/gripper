"""Actual finite P1 shoulder/load checks. Conditional rigid necessary equilibrium only."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,volume,solid_count,bounds
from primary_motor_bearing_wrenches import patches,gravity,solve
from OCP.BRepCheck import BRepCheck_Analyzer

def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(src.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/r['path']) for n,r in refs.items()};load=ROOT/'validation/transmission/primaryP1_gravity_cat_demand_ports2/summary.json';l=json.loads(load.read_text())['rows'][0];rows=[];data={};samples=[]
 # All original operating force/couple components retained. Lateral unit cases are
 # explicit mechanism sensitivity, NOT a new demanded load or capacity criterion.
 for shift in [0,-.1,.1]:
  root=translate(s['F0_ROOT_BACK'],0,shift,0);cells=[]
  for ax,v,d,label in [(2,-7,[0,0,1],'root_seat'),(0,68,[-1,0,0],'root_wall')]:cells+=patches(root,s['OPEN_FRAME'],ax,v,d,label)
  if shift:
   v=np.sign(shift)*20.1;cells+=patches(root,s['OPEN_FRAME'],1,v,[0,-np.sign(shift),0],'Yshoulder')
  refpoint=np.array(l['Root_reference_m'])+[0,shift*.001,0];W=np.array(l['Root_force_couple_XYZ_N_Nm']);W[3:]+=np.cross(refpoint,W[:3]);W+=gravity(root,7900)
  for lateral in ([0] if shift==0 else [0,np.sign(shift)*.1,np.sign(shift)*1]):
   dW=np.r_[0,lateral,0,np.cross(refpoint,[0,lateral,0])];label=f'Y{shift}_lateral{lateral}';r=solve(cells,[[64,-16,-3],[64,16,-3]],W+dW);areas={label:sum(c['area_mm2'] for c in cells if c['label']==label) for label in set(c['label'] for c in cells)};row=dict(case=label,shift_mm=shift,added_lateral_N=lateral,kind='original_conditional_gravity_port' if lateral==0 else 'explicit_lateral_sensitivity_not_operating_requirement',areas_mm2=areas,solution=r);rows.append(row);data[label]=dict(cells=cells,solution=r)
 for dy in [0,.05,.099,.1,.101,.11,-.1,-.101,-.11,-99.536999856]:
  r=translate(s['F0_ROOT_BACK'],0,dy,0);samples.append(dict(root_shift_Y_mm=dy,root_frame_common_mm3=common(r,s['OPEN_FRAME']),root_fixed_RFbolt_common_mm3=[common(r,s[f'F0_RF{i}_BOLT']) for i in range(2)]))
 # Independent aggregate and unchanged standard hardware references, not source ratings.
 assembly=read(REPO/cad['assembly']['path']);bom=json.loads((REPO/cad['BOM']['path']).read_text());checks=dict(all78STEP_hashes=True,all78_single_valid=all(BRepCheck_Analyzer(x).IsValid() and solid_count(x)==1 for x in s.values()),aggregate78solids=solid_count(assembly)==78,aggregate_volume=sum(volume(x) for x in s.values())-volume(assembly)<1e-5,exactBOMreferences={r['part_ID']:r['STEP'] for r in bom['parts']}==refs,nominal_no_root_frame_interference=samples[0]['root_frame_common_mm3']<1e-8,both_01mm_closed_no_interference=all(r['root_frame_common_mm3']<1e-8 for r in samples if abs(r['root_shift_Y_mm'])==.1),both_011mm_penetration_detected=all(r['root_frame_common_mm3']>1e-8 for r in samples if abs(r['root_shift_Y_mm'])==.11),both_finite_positive_Yareas=all(r['areas_mm2'].get('Yshoulder',0)>20 for r in rows if r['shift_mm']),all_original_port_cases_rigid_feasible=all(r['solution']['success'] for r in rows if r['added_lateral_N']==0))
 dump(out/'patches_and_tractions.json',data);dump(out/'summary.json',dict(status='ACTUAL_P1_YCAPTURE_CONDITIONAL_LOAD_SCREEN' if all(checks.values()) else 'ACTUAL_P1_YCAPTURE_LOAD_SCREEN_FAIL',candidate=ref(src),loads=ref(load),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_motor_bearing_wrenches.py')],checks={k:bool(v) for k,v in checks.items()},conditional_load_cases=rows,translation_samples=samples,newly_qualified_system_gate_ids=[],whole_system_release=False,accepted_elastic_equilibria=0,hardware='HARDWARE_NOT_MEASURED',limitations=['Actual reimported product faces and original gravity Root port, frozen from prior model. New geometry needs remesh/coupled updated Finger loads; no transfer of old sourcefield equilibrium.','Rigid nonnegative pressure LP is necessary equilibrium only. Yfaces contribute ONLY at explicitly closed0.1mm gap; no force at nominal open gap. No fictitious tie or preload/friction.','UnitY sensitivity not an operating-load requirement. Infeasibility retained; no strength/capacity or sixDOF closure claim.','Existing RFbolt/nut axial retention conditional connector only; thread flank/core/engagement/material and elastic lateral shaft motion unqualified.','No material minimum/safety/tolerance/process/globalenergy/mesh/time/full3Finger/physicalBaseanchor qualification.']))
 print(json.dumps(dict(checks=checks,rows=[dict(case=r['case'],success=r['solution']['success'],areas=r['areas_mm2']) for r in rows],samples=samples)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
