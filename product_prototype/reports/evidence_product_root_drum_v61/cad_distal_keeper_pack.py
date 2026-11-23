"""Actual keeper STL sections and part list; no STEP or released drawing claim."""
import argparse,csv,json,shutil,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from manufacturing_assembly import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--case',default='product_distal_keeper1005');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.name,a.case)):p.error('local names required')
 start=time.monotonic();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meshdir=BASE/'meshes'/a.name;meshdir.mkdir(exist_ok=False);draw=BASE/'drawings'/a.name;draw.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());config=BASE/meta.get('configuration','config/distal_keeper_v52.json');G=np.asarray(json.loads((src/'keeper_frame.json').read_text()));records=[];bodies=[];hashes={}
 for f in sorted(src.glob('*.stl')):
  shutil.copy2(f,meshdir/f.name);m=trimesh.load_mesh(meshdir/f.name)
  if not m.is_volume or m.body_count!=1:raise ValueError('saved mesh invalid:'+f.name)
  m.apply_transform(np.linalg.inv(G));bodies.append((f.stem,m));records.append(dict(part=f.stem,CAD_volume_mm3=float(m.volume),actual_material='NULL',actual_mass_kg='NULL',qualification='UNQUALIFIED_DIMENSIONAL_CANDIDATE'));hashes[str(f.relative_to(BASE))]=sha(f)
 with (meshdir/'parts.csv').open('w') as stream:
  w=csv.DictWriter(stream,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 fig,axes=plt.subplots(1,2,figsize=(12,5))
 for ax,y in zip(axes,(0,3.5)):
  for (name,m),color in zip(bodies,plt.cm.tab10.colors):
   section=m.section(plane_origin=[0,y,0],plane_normal=[0,1,0])
   if section is None:continue
   for i,line in enumerate(section.discrete):ax.plot(line[:,0],line[:,2],color=color,label=name.replace('f0_c0_s5_','') if i==0 else None)
  ax.set_aspect('equal');ax.set_xlabel('distal local X [mm]');ax.set_ylabel('local Z [mm]');ax.set_title(f'Actual saved-STL section Y={y:g} mm');ax.grid();ax.legend(fontsize=7)
 if len(records)!=6:raise ValueError('exact six saved keeper STLs required')
 fig.suptitle(f'REST CAD {a.case} — NOT Native result / NOT fabrication release');fig.tight_layout();fig.savefig(draw/'sections.svg');fig.savefig(draw/'sections.png',dpi=150);plt.close(fig)
 for f in (Path(__file__),src/'summary.json',src/'keeper_frame.json',config):hashes[str(f.relative_to(BASE))]=sha(f)
 d=dict(status='SIX_ACTUAL_KEEPER_STLS_AND_SECTION_REVIEW_CREATED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,saved_STL_count=len(records),records=records,STEP_generated=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='One f0/c0 distal keeper only, not whole assembly. Actual saved STLs copied byte-identically and sectioned, dimensions mm. No measured material, mass, tolerance, preload, retention, physical fit, assembly service or Native qualification.1005/1006 unresolved original hits preserved.')
 d['source_case']=a.case;d['configuration']=str(config.relative_to(BASE))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(status=d['status'],runtime_s=d['runtime_s'])))
if __name__=='__main__':main()
