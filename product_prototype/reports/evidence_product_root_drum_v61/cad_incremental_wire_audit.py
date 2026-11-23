"""Reuse unchanged CSG descriptions;screen all saved REST paths vs changed parts.

Not an exact computational geometry or physical wire/dynamics certificate.
"""
import argparse,hashlib,json,re,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe
from current_wire_audit import candidate_indices
from deformed_wire_screen import probes

def shape_hash(part):return hashlib.sha256(json.dumps(part['shape'],sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def changed_shapes(old,current):
 a={p['name']:shape_hash(p) for p in old};b={p['name']:shape_hash(p) for p in current}
 if a.keys()!=b.keys():raise ValueError('part added/removed:full audit required')
 changed=[name for name in b if a[name]!=b[name]]
 if not changed:raise ValueError('unchanged geometry is not a new incremental study')
 if any(n.endswith('_eyelet') or n.endswith('_root_redirect') or re.search(r'_turn[123]$',n) or n.endswith('_two_channel_drum') for n in changed):raise ValueError('reference path defining geometry changed:regenerate full paths')
 return changed,[dict(part=n,baseline_shape_SHA256=a[n],current_shape_SHA256=b[n],unchanged=a[n]==b[n]) for n in b]

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';base=BASE/'results'/a.baseline_assembly/'assembly_delta_recipe.json';prior=BASE/'results'/a.baseline_audit/'summary.json';d=json.loads(prior.read_text())
 if d['status']!='SIX_CURRENT_REST_REFERENCE_PATHS_OBSTACLE_CLEAR_ONLY' or any(r['unresolved'] for r in d['records']):raise ValueError('clear prior audit required')
 if d['input_hashes'].get(str(base.relative_to(BASE)))!=sha(base):raise ValueError('prior assembly identity mismatch')
 parts,hashes=resolve_recipe(src);old,bhash=resolve_recipe(base);hashes.update(bhash);changed,identities=changed_shapes(old,parts);lookup={p['name']:p for p in parts};solids=[evaluate(lookup[n]['shape']) for n in changed];bounds=np.asarray([s.bounds for s in solids]);radius=d['wire_envelope_radius_mm'];records=[]
 for module in ('cad/manufacturing_assembly.py','cad/deformed_wire_screen.py','cad/current_wire_audit.py'):
  if d['input_hashes'].get(module)!=sha(BASE/module):raise ValueError('shared geometry/probe helper changed:full audit required')
 for finger in (0,1,2):
  for cable in (0,1):
   path=prior.parent/f'wire_f{finger}_c{cable}.json';r=json.loads(path.read_text());route=np.asarray(r['route_mm']);hits=[];count=0
   if (r['finger'],r['cable'],r['unresolved'])!=(finger,cable,0):raise ValueError('prior path identity/status mismatch')
   for sample,probe in probes(route,radius):
    count+=1
    for j in candidate_indices(bounds,probe.bounds):
     h=trimesh.boolean.intersection([probe,solids[j]],engine='manifold')
     if len(h.faces):hits.append(dict(sample=sample,part=changed[j],faces=len(h.faces),signed_volume_mm3=float(h.volume)))
   records.append(dict(finger=finger,cable=cable,probe_count=count,intersections=hits));hashes[str(path.relative_to(BASE))]=sha(path)
 for f in (Path(__file__),prior,BASE/'cad/current_wire_audit.py',BASE/'cad/manufacturing_assembly.py',BASE/'cad/deformed_wire_screen.py',BASE/'cad/assembly_recipe_io.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 (out/'part_shape_identity.json').write_text(json.dumps(identities,indent=2))
 result=dict(status='INCREMENTAL_CURRENT_REST_WIRE_REVIEW' if any(r['intersections'] for r in records) else 'INCREMENTAL_CURRENT_REST_REFERENCE_PATHS_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,changed_geometry_names=changed,unchanged_geometry_count=len(parts)-len(changed),assembly_part_count=len(parts),records=records,runtime_s=time.monotonic()-start,physical_wire_model_qualified=False,physical_dynamic_clearance_qualified=False,fabrication_ready=False,scope='Exact canonical CSG-description comparison,no numerical tolerance floor. SamepartIDs andunchanged reference-defining Eyelet/Root/Turn/drum geometry required;helperSHAguard. All six previously clear savedREST paths tested against every changed part;all old unchanged CSG screens reused from exact priorassembly. This is composed floating static screen,NOT exact/interval proof or true wireequilibrium/loaded contact/dynamic/Native/holding certificate. No guide/drum exemption for changed parts. Priorcase output bytes unchanged. Shape-identity doesnot qualify material,thread,force or newlibrary versions.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],changed=changed,runtime_s=result['runtime_s'])))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_all_hood_drive1055');p.add_argument('--baseline-assembly',default='product_root_catalog_drive1045');p.add_argument('--baseline-audit',default='product_current_wire1050');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case,a.baseline_assembly,a.baseline_audit)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--baseline-assembly',a.baseline_assembly,'--baseline-audit',a.baseline_audit,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_INCREMENTAL_WIRE_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
