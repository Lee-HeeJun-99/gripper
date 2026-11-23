"""Catalog-sized Root retaining drive cavities and indexed shank screen only."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,cyl,cut,transform
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';spec=BASE/'config/root_retaining_screw_v61.json';cfg=json.loads(spec.read_text());parts,hashes=resolve_recipe(src);names=[f'f{f}_retaining_bolt_{y}' for f in (0,1,2) for y in (-14,14)];byname={p['name']:p for p in parts};new=[];tools=[];records=[]
 for name in names:
  op=byname[name]['shape'];G=np.eye(4)
  while op['op']=='transform':G=G@np.asarray(op['matrix']);op=op['shape']
  if op['op']!='union' or len(op['items'])!=2:raise ValueError('original two-cylinder proxy required')
  shaft,head=op['items']
  if shaft['op']!='cylinder' or head['op']!='cylinder':raise ValueError('unsupported original head')
  if shaft['xy']!=head['xy'] or shaft['z'][1]!=head['z'][0]:raise ValueError('inconsistent head datum')
  if (shaft['radius']*2,shaft['z'][1]-shaft['z'][0],head['radius']*2,head['z'][1]-head['z'][0])!=(cfg['nominal_thread_diameter_mm'],cfg['nominal_length_mm'],max(cfg['head_diameter_mm']),max(cfg['head_height_mm'])):raise ValueError('catalog maximum envelope differs;do not force fit')
  top=head['z'][1];floor=top-cfg['catalog_drive_depth_mm'];r=cfg['nominal_socket_AF_mm']/math.sqrt(3);xy=head['xy'];socket=cyl(r,floor,top+.2,xy,6);shape=transform(cut(op,socket),G);p=dict(byname[name],shape=shape,group='CATALOG_DIMENSIONAL_SOCKET_ENVELOPE',role='SSCF_M3_12_A2_CANDIDATE_NOT_PURCHASED_OR_THREAD_VERIFIED');m=evaluate(shape);file=out/(name+'.stl');file.write_text(m.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('saved socket bolt invalid')
  tools.append(evaluate(transform(cyl(r,floor,top+20,xy,6),G)));new.append(p);records.append(dict(part=name,STL_SHA256=sha(file),CAD_volume_mm3=float(saved.volume),catalog_nominal_AF_mm=cfg['nominal_socket_AF_mm'],nominal_depth_mm=cfg['catalog_drive_depth_mm'],actual_purchased_drive_fit=None))
 fixed=[p for p in parts if p['name'] not in names];allparts=fixed+new;solids={p['name']:evaluate(p['shape']) for p in allparts};solid_hits=[]
 for p in new:
  for h in intersections(solids[p['name']],[(n,b) for n,b in solids.items() if n!=p['name']]):solid_hits.append(dict(changed_part=p['name'],**h))
 for p,tool,r in zip(new,tools,records):
  r['indexed_shank_vs_own_drive']=intersections(tool,[(p['name'],solids[p['name']])]);r['indexed_shank_vs_other_hardware']=intersections(tool,[(n,b) for n,b in solids.items() if n!=p['name']])
 (out/'assembly_delta_recipe.json').write_text(json.dumps(dict(units='mm',parent_recipe=str(src.relative_to(BASE)),parent_SHA256=sha(src),remove_names=names,add_parts=new),indent=2))
 for f in (Path(__file__),spec,BASE/'cad/manufacturing_assembly.py',BASE/'cad/assembly_recipe_io.py',BASE/'cad/distal_keeper_service.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='CATALOG_ROOT_DRIVE_GEOMETRY_REVIEW' if solid_hits or any(r['indexed_shank_vs_own_drive'] or r['indexed_shank_vs_other_hardware'] for r in records) else 'SIX_CATALOG_DIMENSIONAL_DRIVES_AND_INDEXED_SHANKS_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,solid_intersections=solid_hits,candidate_part_count=len(allparts),actual_thread_fit=None,actual_preload_N=None,physical_service_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Six original nominal retaining bolt outer maximum envelopes crosschecked against primary supplier,then dimensioned hex recess added. Nominal indexed AF2.5shank reaches20mm above head;not all-roll circular approximation inside hex cavity,and own drive NOT excluded. Touch/CSG artifacts retained. No actual purchased key/hand/fastener tolerance/thread/chamfer/grade/nut compatibility/torque/preload approved;no helical thread mesh or Native mass adoption. Actual catalog source page stock UNKNOWN. Scope is dimensional CAD,not physical product acceptance.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],external_key_hits=[len(r['indexed_shank_vs_other_hardware']) for r in records])))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_drum_second_channel1041');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CATALOG_ROOT_DRIVE_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
