"""Accepted actual SOFA centerline comparison, not contact-area or grasp certification."""
import argparse,csv,json,os
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args()
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'mpl'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(1,2,figsize=(11,4),layout='constrained');metrics={};inputs={}
 for tag in a.cases:
  source=ROOT/'results'/('autonomous_film_'+tag);summary=json.loads((source/'summary.json').read_text())
  if summary['status']!='PASS':raise RuntimeError('requires completed finite trial')
  path=source/'1/journal.csv';rows=list(csv.DictReader(path.open()));inputs[str(path.relative_to(ROOT))]=sha(path)
  q=np.fromstring(rows[-1]['x'],sep=' ').reshape(-1,3);line=q[:105].reshape(21,5,3)[:,2,:];delta=np.diff(line,axis=0);angle=np.unwrap(np.arctan2(delta[:,2],delta[:,0]));curvature=np.diff(angle)/(.5*(np.linalg.norm(delta[:-1],axis=1)+np.linalg.norm(delta[1:],axis=1)))
  metrics[tag]=dict(time=float(rows[-1]['time']),midspan_center_z_mm=float(line[10,2]),tip_center_z_mm=float(line[-1,2]),maximum_centerline_z_mm=float(max(line[:,2])),minimum_centerline_z_mm=float(min(line[:,2])),minimum_discrete_curvature_per_mm=float(min(curvature)),maximum_discrete_curvature_per_mm=float(max(curvature)),turning_angle_degrees=float(np.degrees(angle[-1]-angle[0])),contact_area=None,wrapping_qualification='NOT RUN',free_object_grasp='NOT RUN')
  ax[0].plot(line[:,0],line[:,2],'.-',label=tag.split('_')[-1]);ax[1].plot([float(r['time']) for r in rows],[float(r['skin_tip_z']) for r in rows],label=tag.split('_')[-1])
 ax[0].set(xlabel='actual x [mm]',ylabel='actual centerline z [mm]',aspect='equal');ax[1].set(xlabel='time [s]',ylabel='width-averaged tip z [mm]')
 for axis in ax:axis.legend();axis.grid(True)
 fig.suptitle('Actual SOFA states; unscaled; experimental routing, NOT qualified grasp');fig.savefig(out/'actual_routing.png',dpi=160);fig.savefig(out/'actual_routing.svg');plt.close(fig)
 write_json(out/'summary.json',dict(status='EXPERIMENTAL',scope='actual geometry comparison; no force/area/grasp approval',inputs=inputs,metrics=metrics));print(json.dumps(metrics))
if __name__=='__main__':main()
