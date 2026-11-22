"""Actual terminal/seat STL review pack and local sections,not fabrication approval."""
import argparse,csv,json,os,subprocess
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.name)):p.error('local names required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);mesh=BASE/'meshes'/a.name;mesh.mkdir(exist_ok=False);draw=BASE/'drawings'/a.name;draw.mkdir(exist_ok=False);src=BASE/'results/product_distal_seat992/assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);lookup={p['name']:p for p in parts};chosen=[p for p in parts if '_distal_NI000001' in p['name'] or '_s5_support' in p['name'] or '_s5_eyelet' in p['name']];records=[]
 if len(chosen)!=18:raise ValueError('18actual solids expected')
 for p0 in chosen:
  body=evaluate(p0['shape']);f=mesh/(p0['name']+'.stl');f.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(f)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('invalid actual exported solid')
  records.append(dict(instance=p0['name'],STL_SHA256=sha(f),CAD_volume_mm3=float(saved.volume),actual_material='UNSELECTED_OR_UNVERIFIED',actual_mass_g='NULL',status='REVIEW_NOT_QUALIFIED'))
 with (mesh/'REVIEW_BOM.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 (mesh/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=chosen),indent=2))
 (mesh/'qualification.json').write_text(json.dumps(dict(scope='18partSUBASSEMBLYONLY,notfull3Fingerassembly;992physicalrelief/seatcandidate,unselectedjoint/retention',STEP_generated=False,fabrication_ready=False),indent=2))
 os.environ['MPLCONFIGDIR']=str(out/'mplconfig');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 prefix='f0_c0';G=np.eye(4);op=lookup[prefix+'_s5_eyelet']['shape']
 while op['op']=='transform':G=G@np.asarray(op['matrix']);op=op['shape']
 fig,ax=plt.subplots(figsize=(10,5))
 for suffix,color in [('_s5_support','tab:green'),('_s5_eyelet','tab:orange'),('_distal_NI000001_MAX_ENVELOPE','tab:blue')]:
  body=evaluate(lookup[prefix+suffix]['shape']);body.apply_transform(np.linalg.inv(G));section=body.section(plane_origin=[0,0,0],plane_normal=[0,0,1])
  if section is None:raise ValueError('actual section absent')
  for i,line in enumerate(section.discrete):ax.plot(line[:,0],line[:,1],color=color,label=suffix[1:] if i==0 else None)
 ax.set(xlabel='Eyelet-local axial X [mm]',ylabel='Eyelet-local Y [mm]',xlim=(-3,7),ylim=(-4,4));ax.set_aspect('equal');ax.legend(fontsize=8);ax.grid();fig.suptitle('ACTUAL REST CAD section f0/c0, local Z=0 (cropped)\nNI000001 MAX D2.8/L5; machined seat R1.55 / .05mm nominal radial gap\nNo bond/keeper, preload or physical load path qualified',fontsize=10);fig.tight_layout()
 for ext in ('svg','png'):fig.savefig(draw/('distal_section.'+ext),dpi=160)
 plt.close(fig)
 for f in [Path(__file__),BASE/'cad/assembly_recipe_io.py',BASE/'cad/manufacturing_assembly.py']:hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='ACTUAL_TERMINAL_SUBASSEMBLY_REVIEW_PACK_CREATED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,outputs={str(f.relative_to(BASE)):sha(f) for folder in (mesh,draw) for f in folder.iterdir() if f.is_file()},STEP_generated=False,fabrication_ready=False,scope='Actual18savedclosedSTLs+subassemblyrecipe/BOM/section. NO fullassembly,contact/holding/jointstrength/material/tolerance/service/STEPapproval;old989/990/992REVIEWs retained.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],STLs=len(records)),indent=2))
if __name__=='__main__':main()
