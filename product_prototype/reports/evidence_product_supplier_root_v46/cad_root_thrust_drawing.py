"""Actual axial mesh sections,not thread or manufacturing qualification."""
import argparse,json,os,subprocess
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-thrust-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);files=[BASE/'meshes'/name/'full_assembly_recipe.json' for name in ('b3_compact_root_v36','b3_root_thrust_v39')];fig,axes=plt.subplots(1,2,figsize=(12,7));counts=[]
 for axis,src,label in zip(axes,files,('V36baseline / span2.8 groove0.8','V39lands +widegroove / span2.0 groove1.0')):
  parts=json.loads(src.read_text())['parts'];M=np.array(next(p for p in parts if p['name']=='f0_c0_root_redirect')['shape']['matrix']);chosen=[p for p in parts if p['name'] in ('f0_c0_root_redirect','f0_c0_root_mounted_bridge','f0_c0_root_headed_pin')];curves=0
  for i,part in enumerate(chosen):
   shape=evaluate(part['shape']);shape.apply_transform(np.linalg.inv(M));section=shape.section(plane_origin=[0,0,0],plane_normal=[0,1,0])
   if section is None:continue
   for k,line in enumerate(section.discrete):axis.plot(line[:,2],line[:,0],color=plt.get_cmap('tab10')(i),label=part['name'].replace('f0_c0_root_','') if k==0 else None);curves+=1
  axis.set(xlim=(-5,5),ylim=(-3.5,3.5),xlabel='axial coordinate [mm]',ylabel='radial coordinate [mm]',title=label);axis.set_aspect('equal',adjustable='box');axis.grid();axis.legend(fontsize=7);counts.append(curves)
 fig.suptitle('Actual mesh axial sections through Root wheel centre\nResearch CAD ONLY;unverified material/thread/friction/tolerance,not SOFA deformation');fig.tight_layout()
 for ext in ('png','svg'):fig.savefig(out/('root_axial_stack.'+ext),dpi=160)
 plt.close(fig);d=dict(status='ACTUAL_AXIAL_CAD_SECTIONS_NOT_FABRICATION_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x.relative_to(BASE)):sha(x) for x in files+[Path(__file__)]},section_loop_counts=counts,files={p.name:sha(p) for p in out.iterdir() if p.is_file()},fabrication_ready=False,scope='Actual3Dsectioncurves fromfiniteRootwheel/bridge/pin. Nominalspan/groove labels fromexplicitcandidateinputs,notmeasuredendplayorvalidatedtolerances. No geometry/stateprescription orSTEP execution.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
