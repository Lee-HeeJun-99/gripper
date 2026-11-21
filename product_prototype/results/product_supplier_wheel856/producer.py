"""Real mesh CAD for a supplier-sized Root wheel;no automatic assembly approval."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,poly,transform,sha

def dimensions(wire_d=.45,ratio=25):
 if min(wire_d,ratio)<=0:raise ValueError('positive wire diameter and recommendation required')
 root=wire_d*ratio/2;groove=.53*wire_d
 return dict(wire_diameter_mm=wire_d,groove_root_radius_mm=root,groove_cross_section_radius_mm=groove,wire_centre_pitch_radius_mm=root+wire_d/2,flange_outer_radius_mm=root+1.25,bore_radius_mm=.6,width_mm=1.8,scope='Manufacturer-sized bend/root and groove cross-section;flange/bore/width are independent research CAD inputs,NOT catalog product dimensions')

def wheel_mesh(d):
 r=d['groove_root_radius_mm'];g=d['groove_cross_section_radius_mm'];outer=d['flange_outer_radius_mm'];half=d['width_mm']/2;bore=d['bore_radius_mm']
 if not r>bore or not half>g or not outer>r+g:raise ValueError('invalid pulley section')
 profile=[[bore,-half],[outer,-half],[outer,-g],[r+g,-g]]
 profile += [[r+g-g*math.cos(t),g*math.sin(t)] for t in np.linspace(-math.pi/2,math.pi/2,97)[1:]]
 profile += [[outer,g],[outer,half],[bore,half],[bore,-half]]
 body=trimesh.creation.revolve(np.array(profile),sections=128)
 if not body.is_volume or body.body_count!=1:raise ValueError('invalid revolved wheel')
 return body,np.array(profile)

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();cfgfile=BASE/'config/wire_bend_supplier_v40.json';src=BASE/'meshes/b3_root_thrust_v39/full_assembly_recipe.json';cfg=json.loads(cfgfile.read_text());parent=json.loads(src.read_text());wheel=next(x for x in parent['parts'] if x['name']=='f0_c0_root_redirect');d=dimensions();mesh,profile=wheel_mesh(d);M=np.array(wheel['shape']['matrix']);op=transform(poly(mesh),M);world=evaluate(op);target=out/'geometry';target.mkdir(exist_ok=False);file=target/'f0_c0_supplier_wheel.stl';file.write_text(world.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
 if not saved.is_volume or saved.body_count!=1:raise ValueError('saved wheel STL failed readback')
 hits=[]
 for other in parent['parts']:
  if other['name']==wheel['name']:continue
  solid=evaluate(other['shape'])
  if np.any(np.minimum(world.bounds[1],solid.bounds[1])-np.maximum(world.bounds[0],solid.bounds[0])<=0):continue
  intersection=trimesh.boolean.intersection([world,solid],engine='manifold')
  if len(intersection.faces):hits.append(dict(part=other['name'],volume_mm3=float(intersection.volume),faces=len(intersection.faces)))
 (target/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=[dict(wheel,shape=op)],parent_recipe_sha256=sha(src)),indent=2));(target/'profile_mm.json').write_text(json.dumps(profile.tolist()))
 result=dict(status='FAIL_DROP_IN_RETROFIT_INTERFERENCE' if any(h['volume_mm3']>0 for h in hits) else 'REFERENCE_CAD_REQUIRES_REVIEW_NOT_ASSEMBLY_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),BASE/'cad/manufacturing_assembly.py',cfgfile,src)},candidate='SE000022_recommendation_sized_wheel_AT_OLD_ROOT_CENTRE',dimensions=d,STL_sha256=sha(file),volume_mm3=float(saved.volume),watertight_single_body=True,intersections=hits,runtime_s=time.monotonic()-start,STEP_generated=False,fabrication_ready=False,scope='Only ONE f0_c0 wheel changed,old centre/orientation held to isolate drop-in compatibility. Actual CSG against all other291 original parts;no obstacle removed. Same1.8mm width/bore1.2,ASSUMED flange projection1.25. New0.45mm candidate wire vs old0.5mm are different designs. New U-groove/root recommendation doesNOT certify fatigue or fit. Old wire route stillR2 and is NOT compatible with new wheel:no dynamics execution of invalid assembly.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('status','runtime_s','intersections')},indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 command=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(command,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=command,process=proc),indent=2))
 if not (out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CAD_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
