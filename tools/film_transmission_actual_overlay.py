"""Actual NO-object snapshots + virtual fixed sphere,never contact-solver results."""
import argparse,csv,json,os,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_transmission_hold50_1187';meta=json.loads((src/'summary.json').read_text());old=ROOT/'results/autonomous_film_20261118_transmission_static_overlay1180';proof=json.loads((old/'summary.json').read_text())
 if meta['status']!='PASS' or proof['status']!='PASS' or sha(old/'geometry')!=proof['binary_sha256']:raise ValueError('qualified actual geometry and archived closest-triangle observer required')
 for file,digest in meta['raw_hashes'].items():
  if sha(src/file)!=digest:raise ValueError('actual raw changed')
 for name in ('models/film_rail_tendon/Kernel.h','models/film_three_finger/FrameLayout.h','models/film_sphere_contact/ClosestPrimitive.h'):
  if meta['source_hashes'][name]!=proof['sources'][name]:raise ValueError('same reference geometry/closest primitive required')
 rows=list(csv.DictReader((src/'actual.csv').open()));chosen=[min(rows,key=lambda r:abs(float(r['time'])-t)) for t in (.01,.02,.03,.04,.05)];out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(old/'geometry',out/'geometry');(out/'samples.txt').write_text(str(len(chosen))+'\n'+'\n'.join(r['time']+' '+r['q'] for r in chosen)+'\n');run=guarded([out/'geometry',out/'samples.txt',out/'geometry.csv'],out/'process',120);result=dict(status='FAIL',scope='ACTUAL no-object SOFA snapshots with VIRTUAL fixed original-layout sphere overlay;NOT contact/wrapping dynamics',actual_summary_sha256=sha(src/'summary.json'),geometry_binary_sha256=sha(out/'geometry'),geometry_source_summary_sha256=sha(old/'summary.json'),process=run,contact_force=None,contact_area=None,pressure=None,holding_capacity=None)
 if run['exit_code']==0:
  values=list(csv.DictReader((out/'geometry.csv').open()));metrics=[];os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
  fig,axes=plt.subplots(1,2,figsize=(12,5));theta=np.linspace(0,2*np.pi,200)
  for ax in axes:ax.plot(75+30*np.cos(theta),-30.01+30*np.sin(theta),'--',color='gray',label='VIRTUAL fixed R30 sphere')
  for r,g in zip(chosen,values):
   q=np.fromstring(r['q'],sep=' ').reshape(231,3);skin=q[:105].reshape(21,5,3);line=skin[:,2,:].copy();line[:,0]+=np.linspace(0,100,21);line[:,1]+=12
   for ax in axes:ax.plot(line[:,0],line[:,2],label=f'actual {1000*float(r["time"]):.1f}ms')
   metrics.append(dict(actual_time_s=float(r['time']),material_x75_skin_centre_z_mm=float(skin[15,2,2]),material_x75_skin_mean_z_mm=float(skin[15,:,2].mean()),virtual_minimum_buffer_gap_mm=float(g['minimum_buffer_gap_mm']),virtual_violated_triangles=int(g['violated_buffer_triangles'])))
  for ax in axes:ax.set_xlabel('actual local x [mm]');ax.set_ylabel('actual local z [mm],scale1');ax.legend(fontsize=7)
  axes[0].set_aspect('equal');axes[0].set_title('Actual centreline projection + VIRTUAL obstacle');axes[1].set_xlim(60,90);axes[1].set_ylim(-1,1);axes[1].set_title('Axis zoom at original contact region,NOT amplified')
  fig.suptitle('No-object Gauss dt=200us,Tmax=0.0001N/rail;DLL '+meta['binary_sha256'][:12]+'\nWhole320-triangle overlay gaps computed separately;no contact force/area inference');fig.tight_layout();fig.savefig(out/'actual_virtual_overlay.png',dpi=150);plt.close(fig);result.update(status='PASS' if len(values)==len(chosen) else 'FAIL',snapshots=metrics,interpretation='At50ms material x75 arches toward positive localz while tip moves negative. Tip motion alone is NOT wrapping. Overlay does not replace contact-solved trajectories.',image_sha256=sha(out/'actual_virtual_overlay.png'))
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('process','raw_hashes')}))
if __name__=='__main__':main()
