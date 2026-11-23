"""Actual candidate CAD rendering/BOM/envelope;not simulation or fabrication approval."""
import argparse,csv,json,os,subprocess
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-bridge-mpl')
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from release_pack import render

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'meshes/b3_thrust_shims_v29/full_assembly_recipe.json';parent=BASE/'meshes/b3_manufacturing_bore_v21/assembly_recipe.json';assembly=json.loads(src.read_text());parts=assembly['parts'];shapes=[evaluate(p['shape']) for p in parts];vertices=np.vstack([s.vertices for s in shapes]);old=[evaluate(p['shape']) for p in json.loads(parent.read_text())['parts']];baseline_radius=max(float(np.linalg.norm(s.vertices[:,:2],axis=1).max()) for s in old)
 render(parts,shapes,out/'bridge_full_design.png',title='ReGrip finite Palm bridges and axle-retention CAD candidate\n280parts/proxies;REST design,NOT actual SOFA result',footer='Nominal geometry only:thread/preload/material/tolerance/strength/mass/inertia/STEP and full moving clearance NOT qualified.')
 indices=[i for i,p in enumerate(parts) if p['group'] not in ('finger','eyelet','support','mount','cartridge','clamp')];render([parts[i] for i in indices],[shapes[i] for i in indices],out/'bridge_drive_design.png',title='Conditional drive support topology:outer towers and integral forks\nEngineering review only;unverified motor horn / root redirect',footer='280part full recipe;view omits finger/cartridge bodies for visibility ONLY,not a collision-test exclusion.')
 with (out/'REGRIP_BRIDGE_BOM.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['group','quantity','material','supplier','mass_kg','cost_KRW','status'])
  for group in sorted(set(p['group'] for p in parts)):w.writerow([group,sum(p['group']==group for p in parts),'UNSELECTED','UNSELECTED','NULL','NULL','DESIGN_ONLY_NOT_QUALIFIED'])
 result=dict(status='CAD_REVIEW_PACK_NOT_ASSEMBLY_OR_FABRICATION_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),input_hashes={str(p.relative_to(BASE.parent)):sha(p) for p in (src,parent,BASE/'cad/release_pack.py')},part_instances=len(parts),AABB_mm=[vertices.min(axis=0).tolist(),vertices.max(axis=0).tolist()],baseline_maximum_radial_extent_mm=baseline_radius,new_maximum_radial_extent_mm=float(np.linalg.norm(vertices[:,:2],axis=1).max()),footprint_scope='Manufactured referenceCAD only;root-centre radius50mm unchanged butouterhardware enlarged. No deformed sweep or physicalframe fit.',files={p.name:sha(p) for p in out.iterdir() if p.is_file()},STEP_generated=False,fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('part_instances','baseline_maximum_radial_extent_mm','new_maximum_radial_extent_mm','AABB_mm')},indent=2))
if __name__=='__main__':main()
