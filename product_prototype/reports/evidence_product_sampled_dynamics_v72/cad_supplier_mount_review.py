"""Actual CAD sections of failed and improved branch,not SOFA visualization."""
import argparse,csv,json,os,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);os.environ['MPLCONFIGDIR']=str(out/'mplconfig')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 files=[BASE/'results'/f'product_supplier_mount{k}'/'full_assembly_recipe.json' for k in (873,875)];fig,axes=plt.subplots(1,2,figsize=(12,7));names=['f0_c0_root_mounted_bridge','f0_c0_turn1','f0_c0_turn2','f0_c0_turn3'];colors=['tab:green','tab:blue','tab:orange','tab:red'];last=None
 for ax,file,title in zip(axes,files,('873 FAILED: cross-member intersects turn2','875: support raised12mm; NOT qualified assembly')):
  parts=json.loads(file.read_text())['parts'];last=parts
  for name,color in zip(names,colors):
   section=evaluate(next(p['shape'] for p in parts if p['name']==name)).section(plane_origin=[0,36,0],plane_normal=[0,1,0])
   if section:
    for i,line in enumerate(section.discrete):ax.plot(line[:,0],line[:,2],lw=1,color=color,label=name.replace('f0_c0_','') if i==0 else None)
  ax.set(title=title,xlabel='world x [mm]',ylabel='world z [mm]',xlim=(40,80),ylim=(-15,75));ax.set_aspect('equal');ax.legend(fontsize=7)
 fig.suptitle('ACTUAL CAD plane sections y=36mm — NOT Native SOFA states\nOne f0/c0 branch only; material,threads,wire motion and fabrication remain unqualified');fig.tight_layout()
 for ext in ('png','svg'):fig.savefig(out/('turn_mount_sections.'+ext),dpi=160)
 plt.close(fig)
 with (out/'instance_BOM.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['part','quantity','status'])
  for p in last:w.writerow([p['name'],1,'DESIGN_ONLY_NOT_APPROVED'])
 result=dict(status='ACTUAL_CAD_REVIEW_SECTIONS_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in [Path(__file__),*files]},BOM_instances=len(last),fabrication_ready=False,STEP_generated=False,scope='Two plane sections only,not complete3Dclearance/fabrication approval or physical result')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(out/'turn_mount_sections.png')
if __name__=='__main__':main()
