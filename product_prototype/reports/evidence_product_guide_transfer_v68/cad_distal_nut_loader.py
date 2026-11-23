"""Finite hollow nut loader and actual sampled insertion,not a fabricated tool."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha,cyl,cut,union,transform
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections

def tool_shape(x,y,top,cfg):
 bottom=top-cfg['shaft_length_mm'];gb=bottom-cfg['grip_length_mm']+cfg['grip_overlap_mm']
 return cut(union(cyl(cfg['shaft_outer_radius_mm'],bottom,top,(x,y)),cyl(cfg['grip_outer_radius_mm'],gb,bottom+cfg['grip_overlap_mm'],(x,y))),cyl(cfg['shaft_bore_radius_mm'],gb-1,top+1,(x,y)))

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);meta=json.loads((src.parent/'summary.json').read_text());cfgpath=BASE/meta['configuration'];cfg=json.loads(cfgpath.read_text());toolpath=BASE/'config/distal_nut_loader_v55.json';tcfg=json.loads(toolpath.read_text());G=np.asarray(json.loads((src.parent/'keeper_frame.json').read_text()));solids={p['name']:evaluate(p['shape']) for p in parts};prefix='f0_c0_s5_';screws={prefix+'keeper_screw0',prefix+'keeper_screw1'};records=[];tools=[];saved=[]
 for bolt,(x,y) in enumerate(cfg['design']['bolt_centres_XY_mm']):
  nutname=prefix+f'keeper_nut{bolt}';local=tool_shape(x,y,cfg['design']['nut_bottom_Z_mm'],tcfg);tool=evaluate(transform(local,G));tools.append(tool);file=out/f'nut_loader_position{bolt}.stl';file.write_text(tool.export(file_type='stl_ascii'))
  if not tool.is_volume or tool.body_count!=1:raise ValueError('invalid finite hollow tool')
  saved.append(dict(position=bolt,STL_SHA256=sha(file),CAD_volume_mm3=float(tool.volume)))
  obstacles=[(n,b) for n,b in solids.items() if n not in {nutname,*screws}]
  for dz in tcfg['insertion_offsets_Z_mm']:
   delta=dz*G[:3,2];nut=solids[nutname].copy();nut.apply_translation(delta);shifted=tool.copy();shifted.apply_translation(delta)
   records.append(dict(bolt=bolt,translation_local_Z_mm=dz,nut_intersections=intersections(nut,obstacles),tool_intersections=intersections(shifted,obstacles)))
  screw=solids[prefix+f'keeper_screw{bolt}'];records.append(dict(bolt=bolt,operation='NOMINAL_FINAL_SCREW_VS_LOADER',intersections=intersections(screw,[('loader',tool)])))
 pair=intersections(tools[0],[('second_loader',tools[1])])
 for f in (Path(__file__),cfgpath,toolpath,src.parent/'keeper_frame.json',BASE/'cad/manufacturing_assembly.py',BASE/'cad/distal_keeper_service.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='TEMPORARY_NUT_LOADER_GEOMETRY_REVIEW',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,saved_tool_positions=saved,simultaneous_tool_intersections=pair,required_operation=tcfg['operation'],actual_material=None,actual_hand_force_N=None,actual_strength_N=None,fabrication_ready=False,physical_service_qualified=False,runtime_s=time.monotonic()-start,scope='New finite hollow loader nominal design;two positional copies of ONE sequential tool,not added to operating BOM. Both screws absent during nut+tool insertion;all other hardware retained. Eight actual nut+loader positions per bolt including0.05mm nominal roof-gap closure. Contact/bearing faces retained,not discarded. Nominal final screw/tool overlap checked,not full screw insertion/key/hand path. Pair test records why simultaneous tools may be invalid. No actual fabricated tool,material/load/preload/physical thread engagement,Native or gripper qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],pair_hits=len(pair))))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_bottom1018');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_NUT_LOADER_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
