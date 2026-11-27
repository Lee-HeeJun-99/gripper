"""Render exact referenced product STL surfaces; illustration,not CAD evidence."""
import json,sys,shutil
# System matplotlib was compiled against systemNumPy1. Existing FEM overlay
# NumPy2 is unnecessary for this illustration. No package/SDK is changed.
sys.path=[p for p in sys.path if p!='/tmp/regrip_stage2_fem']
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from baseline_registry import ROOT,REPO,ref,dump
def main():
 out=ROOT/'validation/integrated/primaryP1_anchor36b_views';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_anchor36b/summary.json';cad=json.loads(cp.read_text());meshes={};sources=[]
 for n,r in cad['part_references'].items():
  path=(REPO/r['path']).with_suffix('.stl');points=[]
  for line in path.read_text().splitlines():
   if line.lstrip().startswith('vertex '):points.append([float(x) for x in line.split()[1:]])
  meshes[n]=np.array(points).reshape(-1,3,3);sources.append(ref(path))
 fig=plt.figure(figsize=(14,7))
 for index,detail in enumerate((False,True)):
  ax=fig.add_subplot(1,2,index+1,projection='3d')
  for n,t in meshes.items():
   if detail and n not in ('TEST_BASE','BENCH_ANCHOR_RAIL') and not n.startswith('ANCHOR_'):continue
   color='#e58b35' if n=='BENCH_ANCHOR_RAIL' else '#4279a8' if n=='TEST_BASE' else '#d9af38' if n.startswith('ANCHOR_') else '#adb5bd'
   ax.add_collection3d(Poly3DCollection(t,facecolor=color,edgecolor='none',alpha=.95))
  if detail:ax.set(xlim=(-70,110),ylim=(-68,48),zlim=(50,86),title='Actual external anchor: 3 axial stations / 2 keys');ax.set_box_aspect((180,116,65))
  else:ax.set(xlim=(-70,110),ylim=(-68,48),zlim=(-105,86),title='ONE P1: Motor -> Drum -> Tendon -> Finger -> Base');ax.set_box_aspect((180,116,191))
  ax.view_init(elev=26,azim=-56);ax.set_xlabel('X [mm]');ax.set_ylabel('Y [mm]');ax.set_zlabel('Z [mm]')
 fig.suptitle('primaryP1_anchor36b | 85 actual part references | NOT RELEASED / external bench attachment unqualified');fig.tight_layout();fig.savefig(out/'actual_product.png',dpi=140);plt.close(fig)
 dump(out/'summary.json',dict(status='ACTUAL_P1_REFERENCED_STL_REVIEW_VIEWS_NOT_VALIDATION',candidate=ref(cp),producer=ref(out/'producer.py'),source_STLs=sources,parts=len(meshes),triangles=sum(len(t) for t in meshes.values()),view=ref(out/'actual_product.png'),whole_system_release=False))
 print(json.dumps(dict(parts=len(meshes),triangles=sum(len(t) for t in meshes.values()))))
if __name__=='__main__':main()
