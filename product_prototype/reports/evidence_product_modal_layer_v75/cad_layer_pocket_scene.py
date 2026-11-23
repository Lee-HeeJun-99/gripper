"""Preserve separate CAD components;combined STL is NOT a boolean solid."""
import argparse,json
from pathlib import Path
import trimesh
from manufacturing_assembly import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_cartridge_pocket1198';scene=trimesh.Scene();parts={}
 for f in src.glob('*.stl'):
  if f.name=='assembly.stl':continue
  mesh=trimesh.load(f,force='mesh');parts[f.stem]=dict(watertight=bool(mesh.is_watertight),source_sha256=sha(f));scene.add_geometry(mesh,geom_name=f.stem,node_name=f.stem)
 scene.export(out/'component_assembly.glb');reloaded=trimesh.load(out/'component_assembly.glb',force='scene');d=dict(status='COMPONENT_SCENE_ONLY_NOT_BOOLEAN_ASSEMBLY',components=parts,reloaded_components=len(reloaded.geometry),all_reloaded_components_watertight=all(m.is_watertight for m in reloaded.geometry.values()),combined_STL='Known nonmanifold after coincident interface welding;visualization ONLY,not manufacturing solid',source_nominal_audit='layer_pocket_audit1200',seal='NOT VALIDATED',STEP='NOT GENERATED',fabrication_ready=False);(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
