"""Actual Frame/Ground positive-path witness, assembly and mass delta; not capacity."""
import json,sys,shutil,itertools
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds,overlap,common,volume,solid_count
from primary_motor_bearing_wrenches import patches,gravity
from primary_contact_transfer_v3 import wrench
from OCP.BRepCheck import BRepCheck_Analyzer

def solve(cells,W):
 cols=[wrench(c['point_mm'],c['direction']) for c in cells]
 for x,y in [(-25,-28),(-25,14),(60,-28),(60,0)]:cols.append(wrench([x,y,34],[0,0,1]))
 A=np.array(cols).T;sc=np.array([1,1,1,100,100,100]);r=linprog(np.ones(len(cols)),A_eq=sc[:,None]*A,b_eq=-sc*W,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});row=dict(success=bool(r.success),message=r.message)
 if r.success:row.update(forces_N=r.x.tolist(),force_error_N=float(np.linalg.norm((A@r.x+W)[:3])),moment_error_Nm=float(np.linalg.norm((A@r.x+W)[3:])))
 return row

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'cad/exports/primaryP1_framekey19/summary.json';d=json.loads(src.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/r['path']) for n,r in refs.items()};oldsrc=ROOT/'cad/exports/primaryP1_interfaces18/summary.json';old=json.loads(oldsrc.read_text());frame0=read(REPO/old['part_references']['OPEN_FRAME']['path']);ground0=read(REPO/old['part_references']['GROUND_PLATE']['path']);cells=[]
 for ax,v,n,label in [(2,40,[0,0,-1],'seat'),(0,56,[1,0,0],'key_xmin'),(0,64,[-1,0,0],'key_xmax'),(1,5,[0,1,0],'key_ymin'),(1,11,[0,-1,0],'key_ymax')]:cells+=patches(s['OPEN_FRAME'],s['GROUND_PLATE'],ax,v,n,label)
 masssrc=ROOT/'validation/integrated/primaryP1_gravity_cat_massload1/summary.json';m=json.loads(masssrc.read_text());parts={r['part_ID']:r for r in m['parts']};W=np.array(m['operating_external_port_N_Nm'])+np.array(m['nonBase_gravity_wrench_N_Nm'])-np.array(parts['GROUND_PLATE']['gravity_wrench_N_Nm'])
 for n in parts:
  if n.startswith('FIXTURE_'):W-=parts[n]['gravity_wrench_N_Nm']
 oldframe=read(REPO/json.loads((ROOT/'cad/exports/primaryP1_fixture15/summary.json').read_text())['part_references']['OPEN_FRAME']['path']);W+=gravity(s['OPEN_FRAME'],2700)-gravity(oldframe,2700)
 rows=dict(new_key=solve(cells,W),without_key=solve([c for c in cells if c['label']=='seat'],W));stages=[];hits=[];comparisons=0
 # FIRST assemble actual Frame upward into Ground; Ground/Basefixture held separate.
 for dz in (-80,-20,-6,-3,-1,0):
  q=translate(s['OPEN_FRAME'],0,0,dz);local=[]
  for n in ['GROUND_PLATE','TEST_BASE']+[n for n in s if n.startswith('FIXTURE_')]:
   if overlap(bounds(q),bounds(s[n])):
    comparisons+=1;v=common(q,s[n])
    if v>1e-8:local.append(dict(part=n,common_mm3=v))
  stages.append(dict(shift_mm=[0,0,dz],hits=local));hits+=local
 # Independent finite-volume overlap derivative on actual key faces.
 derivatives=[]
 for axis,sign,label in [(0,1,'key_xmax'),(0,-1,'key_xmin'),(1,1,'key_ymax'),(1,-1,'key_ymin')]:
  vals=[]
  for h in (.001,.002):
   dv=np.zeros(3);dv[axis]=h*sign;vals.append(common(translate(s['OPEN_FRAME'],*dv),s['GROUND_PLATE'])/h)
  area=sum(c['area_mm2'] for c in cells if c['label']==label);derivatives.append(dict(label=label,exact_area_mm2=area,overlap_derivatives_mm2=vals,relative_error=max(abs(v/area-1) for v in vals)))
 delta=gravity(s['OPEN_FRAME'],2700)-gravity(oldframe,2700)+gravity(s['GROUND_PLATE'],7900)-gravity(read(REPO/json.loads((ROOT/'cad/exports/primaryP1_fixture15/summary.json').read_text())['part_references']['GROUND_PLATE']['path']),7900)
 required=np.array(m['required_external_base_grip_full_wrench_N_Nm'])-delta
 checks=dict(valid_changed_solids=all(BRepCheck_Analyzer(s[n]).IsValid() and solid_count(s[n])==1 for n in ['OPEN_FRAME','GROUND_PLATE']),new_key_equilibrium=rows['new_key']['success'],omitted_key_rejected=not rows['without_key']['success'],frame_to_ground_insertion_clear=not hits,key_overlap_derivatives=max(r['relative_error'] for r in derivatives)<1e-6)
 dump(out/'patches.json',cells);dump(out/'inputs.json',dict(candidate=ref(src),previous_candidate=ref(oldsrc),mass=ref(masssrc),producer=ref(out/'producer.py'),parts=refs,upstream_wrench_N_Nm=W.tolist(),criteria=dict(force_N=1e-8,moment_Nm=1e-10,derivative_relative=1e-6,intersection_mm3=1e-8)))
 result=dict(status='ACTUAL_P1_FRAMEKEY_WITNESS_PASS' if all(checks.values()) else 'ACTUAL_P1_FRAMEKEY_WITNESS_FAIL',candidate=ref(src),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},rows=rows,derivatives=derivatives,assembly_stages=stages,assembly_comparisons=comparisons,patches=ref(out/'patches.json'),areas_mm2={label:sum(c['area_mm2'] for c in cells if c['label']==label) for label in set(c['label'] for c in cells)},updated_required_Base_wrench_N_Nm=required.tolist(),conditional_mass_change_from15_kg=float(-delta[2]/9.80665),conditional_mass_kg=float(m['total_conditional_mass_kg']-delta[2]/9.80665),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Actual finite nominalkey equilibrium,not elastic distribution/capacity or guaranteedfit. Oldplanarfrictionless shear failure retained.','Finite insertion samples,not CCD/tolerance/tool/thread/process or actual hardware certification.','Nominal conditionaldensity/COM; baseline15mass updated for actual18motorlands+19key/pocket. Upstream gravityfrozen not fullycoupled.'])
 dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('rows','assembly_stages')}));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
