"""Actual finite-mesh module views with nominal dimensions,not a fabrication release."""
import argparse,json,os,subprocess
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-wire-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);wheel_source=BASE/'meshes/b3_lead_pulley_modules_v22/assembly_recipe.json';fork_source=BASE/'meshes/b3_pulley_fork_modules_v23/assembly_recipe.json';wheel=json.loads(wheel_source.read_text())['parts'][0];parts=json.loads(fork_source.read_text())['parts'][:2];frame=np.asarray(parts[0]['shape']['matrix']);shapes=[evaluate(p['shape']) for p in [wheel,*parts]]
 for s in shapes:s.apply_transform(np.linalg.inv(frame))
 fig,axs=plt.subplots(1,3,figsize=(13,5));colors=['#d09b39','#5f98b0','#999999']
 for ax,(horizontal,vertical,depth,label) in zip(axs,[(0,1,2,'Front / shaft axis view'),(0,2,1,'Side'),(1,2,0,'End')]):
  tri=[];order=[];facecolors=[]
  for shape,color in zip(shapes,colors):
   tri.extend(shape.triangles[:,:,[horizontal,vertical]]);order.extend(shape.triangles[:,:,depth].mean(axis=1));facecolors.extend([color]*len(shape.faces))
  indices=np.argsort(order);ax.add_collection(PolyCollection(np.asarray(tri)[indices],facecolors=np.asarray(facecolors)[indices],edgecolors='none'));ax.autoscale_view();ax.set_aspect('equal');ax.margins(.15);ax.set_xlabel('XYZ'[horizontal]+' [mm]');ax.set_ylabel('XYZ'[vertical]+' [mm]');ax.set_title(label)
 fig.suptitle('Finite turn-pulley + fork + pin candidate / nominal geometry only');fig.text(.02,.02,'Pulley OD6 / pitchD4 / bore1.2 / width1.8;fork bore1.2 / pinD1;nominal axial gap0.5 per side.\nNO Palm mount,retention,bearing,material/tolerance/strength approval;NOT fabrication drawing release.',fontsize=9);fig.tight_layout(rect=(0,.12,1,.94))
 for ext in ('svg','png'):fig.savefig(out/('pulley_module_views.'+ext),dpi=160)
 plt.close(fig);result=dict(status='FINITE_MESH_ORTHOGRAPHIC_REVIEW_NOT_FABRICATION_DRAWING',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),input_hashes={str(p.relative_to(BASE.parent)):sha(p) for p in (wheel_source,fork_source)},files={p.name:sha(p) for p in out.glob('pulley_module_views.*')},fabrication_ready=False,STEP_generated=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(out)
if __name__=='__main__':main()
