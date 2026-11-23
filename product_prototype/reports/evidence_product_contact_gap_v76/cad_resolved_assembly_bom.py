"""Instance-level BOM from actual resolved CAD;no invented purchased properties."""
import argparse,csv,json,subprocess,sys,time,hashlib
from pathlib import Path
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);rows=[];invalid=[]
 for p in parts:
  body=evaluate(p['shape']);valid=bool(body.is_volume and body.body_count==1)
  if not valid:invalid.append(p['name'])
  rows.append(dict(instance=p['name'],quantity=1,group=p.get('group','UNCLASSIFIED'),role=p.get('role','NOT SPECIFIED'),shape_SHA256=hashlib.sha256(json.dumps(p['shape'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),nominal_CAD_volume_mm3=float(body.volume),single_closed_body=valid,actual_material=None,actual_density_kg_m3=None,actual_mass_g=None,selected_vendor_part=None,manufacturing_method=None,procurement_status='UNSELECTED_OR_UNVERIFIED'))
 with (out/'assembly_instance_BOM.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:'NULL' if v is None else v for k,v in r.items()} for r in rows)
 hashes['cad/assembly_recipe_io.py']=sha(BASE/'cad/assembly_recipe_io.py');hashes['cad/manufacturing_assembly.py']=sha(BASE/'cad/manufacturing_assembly.py');hashes['cad/resolved_assembly_bom.py']=sha(__file__)
 result=dict(status='RESOLVED_INSTANCE_BOM_REVIEW_REQUIRED' if invalid else 'RESOLVED_INSTANCE_BOM_CREATED_NOT_FABRICATION_APPROVAL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,instances=len(rows),invalid_solids=invalid,group_counts={g:sum(r['group']==g for r in rows) for g in sorted({r['group'] for r in rows})},BOM_SHA256=sha(out/'assembly_instance_BOM.csv'),runtime_s=time.monotonic()-start,STEP_generated=False,fabrication_ready=False,actual_assembly_mass_g=None,scope='Actual resolved REST CAD instance inventory,one row perpart,no part omitted or small collision erased. Geometric volume isNOT actual mass or purchasedmaterial. Group/role are source metadata,not manufacturing approval. Vendor/material/process/cost/stock unspecified. No new wholeassemblyintersection,moving/contact/strength/Native/holding/STEPGate.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],instances=len(rows),invalid_solids=invalid,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_remaining_f2lead975');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_RESOLVED_BOM_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','instances','runtime_s') if k in d},indent=2))
if __name__=='__main__':main()
