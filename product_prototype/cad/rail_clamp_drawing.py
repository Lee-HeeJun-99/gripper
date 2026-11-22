"""Actual root-frame clip/Rail/Skin sections,not dynamic or preload results."""
import argparse,json,os,shutil,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=2,default=['product_rail_clamp906','product_rail_clamp908']);p.add_argument('--name',default='b3_rail_edge_clamp_v45');a=p.parse_args()
 if any(Path(n).name!=n for n in [a.tag,a.name,*a.cases]):p.error('local names required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);draw=BASE/'drawings'/a.name;os.environ['MPLCONFIGDIR']=str(out/'mplconfig');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 sources=[BASE/'results'/case/'full_assembly_recipe.json' for case in a.cases];frame=sources[0].parent/'root_frame.json';M=np.array(json.loads(frame.read_text()));fig,axes=plt.subplots(1,2,figsize=(12,6));names=['f0_skin','f0_rail_right','f0_c1_s0_support','f0_c1_s0_rail_clamp_screw_PROXY','f0_c1_s0_rail_pressure_pad_RESEARCH'];colors=['tab:blue','.45','tab:green','tab:purple','tab:orange']
 for ax,src,title in zip(axes,sources,a.cases):
  other=np.array(json.loads((src.parent/'root_frame.json').read_text()))
  if not np.array_equal(M,other):raise ValueError('different Root frames require explicit comparison transform')
  parts=json.loads(src.read_text())['parts']
  for name,color in zip(names,colors):
   body=evaluate(next(p['shape'] for p in parts if p['name']==name));body.apply_transform(np.linalg.inv(M));section=body.section(plane_origin=[12,0,0],plane_normal=[1,0,0])
   if section is None:continue
   for i,line in enumerate(section.discrete):ax.plot(line[:,1],line[:,2],lw=1.3,color=color,label=name.replace('f0_c1_s0_','') if i==0 else None)
  ax.set(title=title,xlabel='finger width y [mm]',ylabel='normal z [mm]',xlim=(9,14),ylim=(-1.5,3));ax.set_aspect('equal');ax.legend(fontsize=7)
 fig.suptitle('ACTUAL CAD sections at manufactured longitudinal x=12mm\nUNLOADED .5mm Rail / .1mm Skin; gaps/pad are design inputs,NOT preload or force-transfer qualification',fontsize=10);fig.tight_layout();outputs=[]
 for ext in ('png','svg'):
  file=out/('rail_clamp_detail.'+ext);fig.savefig(file,dpi=170);target=draw/file.name
  if target.exists():raise ValueError('do not overwrite prior drawing')
  shutil.copy2(file,target);outputs.append(target)
 plt.close(fig);result=dict(status='ACTUAL_CLAMP_SECTION_DRAWING_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in [Path(__file__),frame,*sources]},output_hashes={str(p.relative_to(BASE)):sha(p) for p in outputs},fabrication_ready=False,scope='Actual Skin/Rail/support/pad/screw centresections at rootstation12mm;not entire3Dassembly,materialstress or Native states. Candidate names identify geometry only,NOT service or physical qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(outputs[0])
if __name__=='__main__':main()
