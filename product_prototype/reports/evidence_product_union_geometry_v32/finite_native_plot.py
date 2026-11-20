"""Actual Native mapped eyelet/support geometry,not frozen motion or concept art."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_finite_mapped552';root=ET.parse(src/'5/scene.scn').getroot();fig,axes=plt.subplots(2,2,figsize=(10,8));inputs={}
 for i in (0,1):
  for part,node_name in [('eyelet','collision'),('support','supportCollision')]:
   file=src/'5'/f'mapped{i}_{part}.csv';rr=list(csv.DictReader(file.open()));inputs[str(file.relative_to(BASE.parent))]=sha(file);node=root.find(f"./Node[@name='guide{i}']/Node[@name='{node_name}']");edges=np.fromstring(node.find('MeshTopology').get('edges'),sep=' ',dtype=int).reshape(-1,2)
   for row,k in enumerate((0,3)):
    vertices=np.fromstring(rr[k]['q'],sep=' ').reshape(-1,3)*1000
    for col,xy in enumerate(((0,1),(0,2))):
     lines=vertices[edges][:,:,xy];axes[row,col].add_collection(LineCollection(lines,colors=('#1f77b4','#d2691e')[i],linewidths=.5 if part=='eyelet' else .8,alpha=.65));axes[row,col].autoscale();axes[row,col].set_aspect('equal');axes[row,col].set(xlabel='x [mm]',ylabel=('y' if col==0 else 'z')+' [mm]',title=f"Actual accepted t={float(rr[k]['time_s'])*1000:g}ms");axes[row,col].grid(alpha=.2)
 fig.suptitle('Actual Native552 mapped geometry;two FREE eyelet+support bodies,NOT B3/grasp\nSOFA26.06;dt2.5ms;LMD alarm5mm;10mg/body,assumed inertia;binary332+512',fontsize=10);fig.tight_layout();fig.savefig(out/'actual_finite_hardware.png',dpi=160);plt.close(fig);result=dict(status='ACTUAL_NATIVE_MAPPED_GEOMETRY_PLOT_ONLY',scope='Actual NativePointJournal coordinates,no amplified displacement,prescribed deformation or relocated objects. Surface tessellation is the explicit research candidate;not hardware fabrication/holding evidence.',source_sha256=sha(Path(__file__)),inputs=inputs)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
if __name__=='__main__':main()
