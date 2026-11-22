"""Actual mesh sections/BOM for root assembly review;not fabrication approval."""
import argparse,csv,json,os,subprocess
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-root-review-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from release_pack import render

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'meshes'/a.candidate/'full_assembly_recipe.json';parts=json.loads(src.read_text())['parts'];shapes=[evaluate(p['shape']) for p in parts]
 render(parts,shapes,out/'root_full_CAD.png',title=f'ReGrip root boss candidate / {len(parts)} parts and proxies\nREFERENCE CAD ONLY, NOT SOFA',footer='No STEP/thread form/strength/moving clearance/tolerance/product qualification. Prior seam contacts remain.')
 fig,ax=plt.subplots(figsize=(10,9));sections=[]
 for part,shape in zip(parts,shapes):
  name=part['name']
  if not(name.startswith('f0_c0_root') or name in ('palm_bridge_bores','f0_mount','f0_cartridge','f0_clamp')):continue
  section=shape.section(plane_origin=[0,36,0],plane_normal=[0,1,0])
  if section is None:continue
  sections.append(name);color=plt.get_cmap('tab10')((len(sections)-1)%10)
  for k,line in enumerate(section.discrete):ax.plot(line[:,0],line[:,2],color=color,label=name if k==0 else None,linewidth=1.)
 routefile=BASE/'results/product_root_fork780/summary.json';r=json.loads(routefile.read_text())['records'][0];route=np.array(r['route_mm']);ax.plot(route[:,0],route[:,2],'k--',label='Conditional designed wire centreline (not SOFA)')
 ax.set(xlim=(35,67),ylim=(-16,24),xlabel='sector radial x [mm]',ylabel='global z [mm]',title='Actual mesh section at global y=36mm / finger0,cable0\nRoot pitchR2, wheelOD6, wireD0.5;thread geometry NOT modeled');ax.set_aspect('equal',adjustable='box');ax.grid();ax.legend(fontsize=7,loc='upper left');fig.tight_layout()
 for suffix in ('png','svg'):fig.savefig(out/('root_section.'+suffix),dpi=160)
 plt.close(fig)
 with (out/'ROOT_ASSEMBLY_BOM.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['group','qty','material','mass_kg','supplier','status'])
  for group in sorted(set(p['group'] for p in parts)):w.writerow([group,sum(p['group']==group for p in parts),'UNSELECTED','NULL','UNSELECTED','RESEARCH_CAD_NOT_QUALIFIED'])
 vertices=np.vstack([s.vertices for s in shapes]);result=dict(status='ACTUAL_MESH_REVIEW_PACK_NOT_FABRICATION_READY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x.relative_to(BASE)):sha(x) for x in (Path(__file__),src,routefile,BASE/'cad/release_pack.py')},parts=len(parts),section_parts=sections,maximum_radial_extent_mm=float(np.linalg.norm(vertices[:,:2],axis=1).max()),files={p.name:sha(p) for p in out.iterdir() if p.is_file()},STEP_generated=False,fabrication_ready=False,scope='Actual generated mesh fullassembly andplanarsections,not prescribeddeformation/SOFA. Referencegeometry unchangednominalB3 Skin/Rails;newrootmechanism not simulated. Materials/thread/tolerances/completejointstrength unselected. Zero-volumePalm andoldermatingseams notoverridden.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(parts=len(parts),section_parts=sections,maximum_radial_extent_mm=result['maximum_radial_extent_mm']),indent=2))
if __name__=='__main__':main()
