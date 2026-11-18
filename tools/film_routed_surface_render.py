"""Equal-aspect orthographic mesh views of actual NO-OBJECT Field coordinates."""
import argparse,csv,json,os,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS' or not m['stage_rows_exact']:raise ValueError('completed strict actual no-object case required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual raw changed')
 fields=list(csv.DictReader((src/'film_0.csv').open()));states=list(csv.DictReader((src/'actual.csv').open()))
 if len(fields)!=len(states) or any(x['time']!=y['time'] for x,y in zip(fields,states)):raise ValueError('actual Field/owner epochs differ')
 x=np.fromstring(fields[-1]['x'],sep=' ').reshape(231,3);q=np.fromstring(states[-1]['q'],sep=' ').reshape(231,3);rest=x-q
 if not np.isfinite(x).all():raise ValueError('nonfinite physical state')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');parts=[(0,5,'skin'),(105,3,'left_rail'),(168,3,'right_rail')];faces=[]
 with (out/'actual_surface.obj').open('w') as stream:
  stream.write('# Actual SOFA NO-OBJECT accepted Field coordinates;mm;displacement scale1\n')
  for v in x:stream.write('v '+' '.join(format(z,'.17g') for z in v)+'\n')
  for offset,ny,name in parts:
   stream.write('g '+name+'\n')
   for i in range(20):
    for j in range(ny-1):
     f=[offset+i*ny+j,offset+(i+1)*ny+j,offset+(i+1)*ny+j+1,offset+i*ny+j+1];faces.append(f);stream.write('f '+' '.join(str(k+1) for k in f)+'\n')
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 projections=[np.array([[1,0,0],[0,1,0]]),np.array([[1,0,0],[0,0,1]]),np.array([[1,-1,0],[1,1,-2]])/np.array([[2**.5],[6**.5]])]
 fig,axes=plt.subplots(3,1,figsize=(12,9))
 for ax,P,title in zip(axes,projections,['top XY','side XZ','orthographic isometric']):
  for offset,ny,name in parts:
   color='tab:blue' if offset==0 else 'tab:orange';grid=x[offset:offset+21*ny].reshape(21,ny,3);base=rest[offset:offset+21*ny].reshape(21,ny,3)
   for axis in (0,1):
    for line in (grid if axis==0 else grid.transpose(1,0,2)):
     y=line@P.T;ax.plot(y[:,0],y[:,1],color=color,lw=.5)
   for j in (0,ny-1):
    y=base[:,j]@P.T;ax.plot(y[:,0],y[:,1],color='gray',ls='--',lw=.5)
  low,high=ax.get_ylim()
  if high-low<10:ax.set_ylim((low+high)/2-5,(low+high)/2+5)
  ax.set_aspect('equal',adjustable='box');ax.set_title(title+';mm,equal axes,displacement scale1');ax.set_xlabel('projected mm');ax.set_ylabel('projected mm')
 fig.suptitle(f'Actual SOFA {a.case},t={fields[-1]["time"]}s\nNO object/contact;not wrapping qualification;gray=rest;blue=skin,orange=rails');fig.tight_layout();fig.savefig(out/'actual_surface.png',dpi=160);fig.savefig(out/'actual_surface.svg');plt.close(fig)
 result=dict(status='PASS',scope='read-only equal-aspect actual physical surface rendering;NOT qualified grasp',actual_summary_sha256=sha(src/'summary.json'),binary_sha256=m['binary_sha256'],time_s=float(fields[-1]['time']),dt='variable canonical plan;see source summary/plan.txt',displacement_scale=1,axes_equal=True,physical_state_altered=False,triangulation='render quads on existing21x5/21x3/21x3 structured nodes;not a new FEM discretization',wire_guides='NOT rendered',contact_area=None,pressure=None,raw_hashes={f:sha(out/f) for f in ('actual_surface.obj','actual_surface.png','actual_surface.svg')});write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
