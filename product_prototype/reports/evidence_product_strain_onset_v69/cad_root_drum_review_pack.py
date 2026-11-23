"""Actual 13-part Root/drum review pack and saved-STL sections,not STEP release."""
import argparse,csv,json,os,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;dest=BASE/'meshes'/a.name;draw=BASE/'drawings'/a.name;dest.mkdir(exist_ok=False);draw.mkdir(exist_ok=False);src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);lookup={p['name']:p for p in parts};rootnames=['f0_root_clamp','f0_carrier',*[f'f0_retaining_{kind}_{y}' for kind in ('bolt','nut') for y in (-14,14)]];drumnames=['f0_two_channel_drum',*[f'f0_c{c}_drum_{s}' for c in (0,1) for s in ('pressure_pad','adjuster_M1p6','nut_M1p6')]];records=[];saved={}
 for name in rootnames+drumnames:
  body=evaluate(lookup[name]['shape']);file=dest/(name+'.stl');file.write_text(body.export(file_type='stl_ascii'));m=trimesh.load_mesh(file)
  if not m.is_volume or m.body_count!=1:raise ValueError('actual saved part invalid:'+name)
  saved[name]=m;records.append(dict(part=name,STL_SHA256=sha(file),CAD_volume_mm3=float(m.volume),actual_material='NULL',actual_mass_kg='NULL',supplier_and_thread_fit_qualified=False))
 with (dest/'review_parts.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 (dest/'subassembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=[lookup[n] for n in rootnames+drumnames],source_case=a.case,scope='13partreviewonly,NOTwholeassemblyorqualifiedBOM'),indent=2))
 os.environ['MPLCONFIGDIR']=str(out/'mplconfig');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,3,figsize=(18,6));G=np.asarray(lookup['f0_carrier']['shape']['matrix'])
 for name in rootnames:
  m=saved[name].copy();m.apply_transform(np.linalg.inv(G));section=m.section(plane_origin=[0,14,0],plane_normal=[0,1,0])
  if section is None:continue
  for i,line in enumerate(section.discrete):axes[0].plot(line[:,0],line[:,2],label=name.replace('f0_','') if i==0 else None)
 axes[0].set(xlabel='Root longitudinal X [mm]',ylabel='Root normal Z [mm]',title='Actual STL section:Root Y14mm')
 for ax,y in zip(axes[1:],(-3,3)):
  for name in drumnames:
   section=saved[name].section(plane_origin=[0,y,0],plane_normal=[0,1,0])
   if section is None:continue
   for i,line in enumerate(section.discrete):ax.plot(line[:,0],line[:,2],label=name.replace('f0_','') if i==0 else None)
  ax.set(xlim=(48.8,58.5),xlabel='World X [mm]',ylabel='World Z [mm]',title=f'Actual STL section:drum Y{y:g}mm')
 for ax in axes:ax.set_aspect('equal');ax.grid();ax.legend(fontsize=6)
 fig.suptitle(f'REST CAD {a.case} — not Native state / not fabrication release');fig.tight_layout();fig.savefig(draw/'sections.png',dpi=150);fig.savefig(draw/'sections.svg');plt.close(fig)
 for f in (Path(__file__),BASE/'cad/manufacturing_assembly.py',BASE/'cad/assembly_recipe_io.py',BASE/'config/root_nut_hood_v57.json',BASE/'config/termination_drum_clamp_v59.json',BASE/'config/termination_drum_clamp_v60.json'):hashes[str(f.relative_to(BASE))]=sha(f)
 catalog=lookup['f0_retaining_bolt_14'].get('group')=='CATALOG_DIMENSIONAL_SOCKET_ENVELOPE'
 if catalog:hashes['config/root_retaining_screw_v61.json']=sha(BASE/'config/root_retaining_screw_v61.json')
 result=dict(status='THIRTEEN_ACTUAL_ROOT_DRUM_STLS_AND_SECTIONS_CREATED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,saved_STL_count=len(records),source_case=a.case,assembly_part_count=len(parts),root_retaining_catalog_drive_present=catalog,STEP_generated=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Actual saved-STL sections and13instance review CSV/subassembly only. NOT300part full Assembly STEP/BOM release,Native Accepted States or physical material/mass/thread/retention/strength. Axis/closure/mating artifacts and oldFAILs not altered. Socket presence recorded separately:catalog dimensional cavities are NOT purchased drive/thread/physical fit qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'])))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--case',default='product_drum_second_channel1041');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.name,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--name',a.name,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_ROOT_DRUM_PACK_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
