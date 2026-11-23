"""Current assembly vs six REST reference paths;not dynamic wire equilibrium."""
import argparse,json,re,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,sector
from assembly_recipe_io import resolve_recipe
from deformed_wire_screen import probes

def candidate_indices(bounds,probe_bounds):
 return np.flatnonzero(np.all(np.minimum(bounds[:,1],probe_bounds[1])>np.maximum(bounds[:,0],probe_bounds[0]),axis=1))

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);solids=[evaluate(p['shape']) for p in parts];bounds=np.asarray([s.bounds for s in solids]);sources=[BASE/'results'/s/'summary.json' for s in ('product_supplier_first_recheck890','product_supplier_second_full_wire887')];leads=[np.asarray(json.loads(s.read_text())['route_mm']) for s in sources];radius=.22522275007459786;records=[]
 for finger in (0,1,2):
  S=sector(120*finger)
  for cable in (0,1):
   prefix=f'f{finger}_c{cable}';lead=leads[cable]@S[:3,:3].T+S[:3,3];eyes=[]
   for p,body in zip(parts,solids):
    m=re.fullmatch(prefix+r'_s(\d+)_eyelet',p['name'])
    if m:eyes.append((int(m[1]),body.center_mass))
   eyes.sort()
   if [i for i,_ in eyes]!=list(range(6)):raise ValueError('six actual Eyelet station identities required')
   chain=np.asarray([point for _,point in eyes])
   if np.linalg.norm(chain[0]-lead[0])>1e-10:raise ValueError('same-time REST reference identity mismatch')
   route=np.vstack([chain[::-1],lead[1:]]);intended={prefix+'_root_redirect',*[prefix+f'_turn{k}' for k in (1,2,3)]};contacts=[];count=0;boolean_tests=0;t=time.monotonic()
   for index,probe in probes(route,radius):
    count+=1
    for j in candidate_indices(bounds,probe.bounds):
     boolean_tests+=1;hit=trimesh.boolean.intersection([probe,solids[j]],engine='manifold')
     if len(hit.faces):contacts.append(dict(sample=index,part=parts[j]['name'],faces=len(hit.faces),signed_volume_mm3=float(hit.volume),classification='PLANNED_WHEEL_PROXIMITY_NOT_CONTACT_LAW_PASS' if parts[j]['name'] in intended else 'UNRESOLVED_CURRENT_HARDWARE'))
   r=dict(finger=finger,cable=cable,route_mm=route.tolist(),probe_count=count,boolean_tests=boolean_tests,intersections=contacts,unresolved=sum(h['classification']=='UNRESOLVED_CURRENT_HARDWARE' for h in contacts),runtime_s=time.monotonic()-t);records.append(r);(out/f'wire_f{finger}_c{cable}.json').write_text(json.dumps(r,indent=2));print(json.dumps(dict(finger=finger,cable=cable,probes=count,unresolved=r['unresolved'],runtime_s=r['runtime_s'])),flush=True)
 baseline=BASE/'results/product_completed_leads982/summary.json';old=json.loads(baseline.read_text());estimated=float(old['runtime_s'])*(len(parts)/old['assembly_part_count'])*(4296/4230)
 for f in (Path(__file__),baseline,*sources,BASE/'cad/deformed_wire_screen.py',BASE/'cad/manufacturing_assembly.py',BASE/'cad/assembly_recipe_io.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='CURRENT_REST_WIRE_HARDWARE_REVIEW' if any(r['unresolved'] for r in records) else 'SIX_CURRENT_REST_REFERENCE_PATHS_OBSTACLE_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,assembly_part_count=len(parts),records=[{k:v for k,v in r.items() if k not in ('route_mm','intersections')} for r in records],wire_envelope_radius_mm=radius,pre_run_budget_basis=dict(old_case='product_completed_leads982',old_runtime_s=old['runtime_s'],old_parts=old['assembly_part_count'],projected_unoptimized_runtime_s=estimated,child_limit_s=420,memory_limit_GiB=4),physical_wire_model_qualified=False,physical_dynamic_clearance_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='All six CURRENT REST distalguide-centre→guidechain→Root→turns→drum reference polylines against all actual resolved CAD parts,including new hood/cages/drum clamps/socket bolts. No frame/part omitted. Only named Root/Turn wheel proximities classified planned;ENTIRE DRUM isNOT exempt because added clamp material must be checked. Eyelet/Support/Drum/cage intersections allunresolved,not rounded away. Reuses finite probe construction,vectorizes identical strict AABB test,no new tolerance. Static centre reference isNOT actual flexible/frayed/loaded wire or Native trajectory;distalstop and drumtail beyond endpoints separate scopes. No friction/fatigue/capacity/dynamic/holding qualification;no old result overwritten or reclassified.')
 (out/'summary.json').write_text(json.dumps(result,indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_root_catalog_drive1045');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());baseline=BASE/'results/product_completed_leads982/summary.json';b=json.loads(baseline.read_text());parts,_=resolve_recipe(BASE/'results'/a.case/'assembly_delta_recipe.json');estimate=float(b['runtime_s'])*(len(parts)/b['assembly_part_count'])*(4296/4230);(out/'budget_preflight.json').write_text(json.dumps(dict(basis_SHA256=sha(baseline),estimated_unoptimized_s=estimate,limit_s=420,memory_GiB=4,scope='Changedgeometryconservativeprojection,notasamebinaryperformanceclaim'),indent=2));sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 if estimate>420:raise ValueError('projected child runtime policy exceeded')
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CURRENT_WIRE_AUDIT_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
