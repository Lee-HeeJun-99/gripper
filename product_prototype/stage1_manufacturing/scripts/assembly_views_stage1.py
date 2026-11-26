"""Actual indexed mesh orthographic overview; explosion is illustrative only."""
import argparse,json,math,shutil
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from manufacturing_packet import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'cad/drawings'/a.tag;out.mkdir(exist_ok=False)
 shapes={n:trimesh.load((ROOT/v['path']).with_suffix('.stl'),force='mesh') for n,v in idx['parts'].items()};bounds=np.array([m.bounds for m in shapes.values()]);lo=bounds[:,0].min(0);hi=bounds[:,1].max(0)
 for exploded in (False,True):
  fig,axs=plt.subplots(1,3,figsize=(18,7));colours=plt.cm.tab10.colors
  for n,m in shapes.items():
   v=m.vertices.copy();sector=int(n[1]) if n.startswith(('F0_','F1_','F2_')) else 0
   if exploded and n!='PALM':
    angle=sector*2*math.pi/3;v+=np.array([math.cos(angle),math.sin(angle),0])*55
    if any(k in n for k in ('SKIN','RAIL','TERMINAL','SWIVEL','TIP_FACTORY','TENDON_WIRE')):v[:,2]-=30
    elif 'MOTOR' in n:v[:,2]+=30
   e=m.edges_unique[::max(1,len(m.edges_unique)//250)]
   for ax,(u,w),label in zip(axs,[(0,1),(0,2),(1,2)],['XY/top','XZ/front','YZ/side']):
    ax.add_collection(LineCollection(v[e][:,:,[u,w]],colors=[colours[sector] if n!='PALM' else (.5,.5,.5)],linewidths=.25));ax.autoscale();ax.set_aspect('equal');ax.set_title(label);ax.set_xlabel('mm');ax.grid(alpha=.2)
  title=f'{a.case} / '+('ILLUSTRATIVE EXPLODED — NOT an insertion path' if exploded else 'ACTUAL REST INDEXED ASSEMBLY')
  fig.suptitle(title);fig.text(.02,.02,f'292 indexed parts; actual REST bounds {lo.round(4).tolist()} .. {hi.round(4).tolist()} mm. Sampled exported edges only; individual STEP and feature tables authoritative.',fontsize=9)
  fig.tight_layout(rect=[0,.04,1,.94]);fig.savefig(out/('EXPLODED.svg' if exploded else 'ASSEMBLY.svg'));plt.close(fig)
 result=dict(status='ACTUAL_ASSEMBLY_REVIEW_VIEWS_GENERATED',case=a.case,parts=len(shapes),actual_REST_bounds_mm=[lo.tolist(),hi.tolist()],actual_REST_extents_mm=(hi-lo).tolist(),scope='Actual indexed mesh projections, sampled edges. Explosion illustrative only, not service proof or manufacturing approval.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result))
if __name__=='__main__':main()
