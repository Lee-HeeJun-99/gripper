"""Actual keeper axial-stop overlap probes and CAD review;not joint strength."""
import argparse,json,os,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'results/product_eyelet_keeper894/full_assembly_recipe.json';frame=src.parent/'keeper_frame.json';parts=json.loads(src.read_text())['parts'];H=np.array(json.loads(frame.read_text()));ring=evaluate(next(p['shape'] for p in parts if p['name']=='f0_c1_s0_eyelet'));keepers=[(p['name'],evaluate(p['shape'])) for p in parts if p['name'] in ('f0_c1_s0_support','f0_c1_s0_keeper_cover')];records=[]
 for distance in (0,.05,-.05,.1,-.1,.15,-.15):
  moved=ring.copy();moved.apply_translation(H[:3,2]*distance);hits=[]
  for name,body in keepers:
   h=trimesh.boolean.intersection([moved,body],engine='manifold');hits.append(dict(part=name,volume_mm3=float(h.volume) if len(h.faces) else 0.,faces=len(h.faces)))
  records.append(dict(axial_displacement_mm=distance,intersections=hits))
 os.environ['MPLCONFIGDIR']=str(out/'mplconfig');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(9,7))
 for label,body,color in [('Eyelet',ring,'tab:blue'),*[(name,body,'tab:orange' if 'cover' in name else 'tab:green') for name,body in keepers]]:
  local=body.copy();local.apply_transform(np.linalg.inv(H));section=local.section(plane_origin=[0,0,0],plane_normal=[0,1,0])
  if section is not None:
   for i,line in enumerate(section.discrete):ax.plot(line[:,2],line[:,0],color=color,lw=1.3,label=label if i==0 else None)
 ax.set(xlabel='local axial z [mm]',ylabel='local radial x [mm]',title='ACTUAL CAD centre section (y=0): axial shoulders and wire bore\nNot SOFA state or material/retention qualification');ax.set_aspect('equal');ax.legend(fontsize=7);fig.tight_layout()
 for ext in ('png','svg'):fig.savefig(out/('keeper_axial_section.'+ext),dpi=160)
 plt.close(fig)
 result=dict(status='GEOMETRIC_AXIAL_STOP_REFERENCE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,frame)},records=records,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Actual finite Eyelet translated relative to unchanged support/cover;positive volumes at±.15mm verify geometric axial obstruction only. At±.1mm numerical face fragments retained. No force/materialstrength,pressfit,preload,motion/retention proof or Native result. Sectiony0 lies INsplitgap:cap/body edges may not appear;not a complete assembly depiction.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
