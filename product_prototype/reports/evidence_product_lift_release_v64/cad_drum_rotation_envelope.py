"""Conservative nominal drum full-turn hardware envelope,NOT actual motion data."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha,cyl
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections

def rotation_bound(meshes,centre,sections=128):
 centre=np.asarray(centre,dtype=float)
 if centre.shape!=(2,) or not np.all(np.isfinite(centre)) or sections<8:raise ValueError('finite centre and adequate polygon required')
 points=np.vstack([m.vertices for m in meshes]);radius=float(np.linalg.norm(points[:,:2]-centre,axis=1).max());zmin=float(points[:,2].min());zmax=float(points[:,2].max());circ=radius/math.cos(math.pi/sections)
 return cyl(circ,zmin,zmax,centre,sections),dict(nominal_axis_centre_XY_mm=centre.tolist(),maximum_source_vertex_radius_mm=radius,polygon_circumradius_mm=circ,envelope_Z_mm=[zmin,zmax],sections=sections,scope='Convexity of radial norm bounds each source triangle by its vertex maxima;circumscribed XY polygon contains the full circle,including all rotation angles. Floating arithmetic/CSG,not exact interval/no-touch certificate.')

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);names=['f0_two_channel_drum',*[f'f0_c{c}_drum_{s}' for c in (0,1) for s in ('pressure_pad','adjuster_M1p6','nut_M1p6')]];lookup={p['name']:p for p in parts}
 if not set(names)<=lookup.keys():raise ValueError('both finite channel clamps required')
 moving=[evaluate(lookup[n]['shape']) for n in names];spec=BASE/'config/termination_drum_clamp_v60.json';cfg=json.loads(spec.read_text());shape,bound=rotation_bound(moving,cfg['drum_centre_XY_mm']);envelope=evaluate(shape);file=out/'full_turn_outer_envelope.stl';file.write_text(envelope.export(file_type='stl_ascii'));fixed=[p for p in parts if p['name'] not in names];hits=intersections(envelope,[(p['name'],evaluate(p['shape'])) for p in fixed])
 for f in (Path(__file__),spec,BASE/'cad/manufacturing_assembly.py',BASE/'cad/assembly_recipe_io.py',BASE/'cad/distal_keeper_service.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='DRUM_FULL_TURN_CONSERVATIVE_ENVELOPE_REVIEW' if hits else 'NOMINAL_DRUM_FULL_TURN_HARDWARE_ENVELOPE_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,moving_names=names,fixed_names=[p['name'] for p in fixed],bounding_reference=bound,solid_intersections=hits,assembly_part_count=len(parts),envelope_STL_SHA256=sha(file),actual_motor_axis_qualified=False,physical_dynamic_clearance_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Seven nominal rigid co-rotating CAD parts,full360degree conservative outer cylinder against ALL remaining actual CAD hardware. No fixed parts removed and no prescribed Skin deformation. Radius/Zbound uses actual mesh vertices. Cylinder fills internal voids:hit unresolved,not true collision;clear only certifies floating static-envelope screen for declared axis. This is kinematic bound,NOT measured/Native motor/Finger/Wire motion. Loose pad/nut retention,shaft/horn axis/materials,wire winding/free-tail path,loaded slip,whole-gripper dynamic interference and Native/holding/STEP remain unqualified.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],hits=hits)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_drum_second_channel1041');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_DRUM_ROTATION_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
