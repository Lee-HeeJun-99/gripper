"""Actual contact-model route contrast at EXACT common accumulated times."""
import argparse,csv,json,os,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import mapping,shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();names=('20261118_three_film_first_peak_actual1002',a.candidate);data=[]
 for name in names:
  path=ROOT/'results'/('autonomous_film_'+name);m=json.loads((path/'summary.json').read_text())
  if m['status']!='PASS':raise ValueError('completed actual model required')
  for file,digest in m['raw_hashes'].items():
   if sha(path/file)!=digest:raise ValueError('immutable actual contact output changed')
  states={float(r['time']):r for r in csv.DictReader((path/'three.states.csv').open())};fields=[{float(r['time']):r for r in csv.DictReader((path/f'film_{i}.csv').open())} for i in range(3)];data.append((path,m,states,fields))
 if sha(data[0][0]/'public_mass_reference.txt')!=sha(data[1][0]/'public_mass_reference.txt'):raise ValueError('same public masses required')
 times=sorted(set(data[0][2])&set(data[1][2]));P=mapping();nf=P.shape[1];records=[]
 for t in times:
  for f in range(3):
   if data[0][3][f][t]['T_per_rail']!=data[1][3][f][t]['T_per_rail']:raise ValueError('same ACTUAL per-finger endpoint tension required')
  for i,(path,m,states,fields) in enumerate(data):
   q=np.fromstring(states[t]['q'],sep=' ');v=np.fromstring(states[t]['v'],sep=' ')
   if q.size!=3*nf+6:raise ValueError('actual shared state dimension differs')
   for f in range(3):
    u=P@q[f*nf:(f+1)*nf];metrics=shape(u);skin=u.reshape(231,3)[:105].reshape(21,5,3);records.append(dict(case=names[i],time_s=t,finger=f,T_per_rail_N=float(fields[f][t]['T_per_rail']),object_z_mm=float(q[3*nf+2]),object_vz_mm_s=float(v[3*nf+2]),skin75_mean_z_mm=float(skin[15,:,2].mean()),skin75_centre_z_mm=float(skin[15,2,2]),minimum_whole_stage_gap_mm=float(states[t]['minimum_gap']),**metrics))
 if not times:raise ValueError('no exact common accepted time;no interpolation')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 with (out/'shape.csv').open('w') as file:w=csv.DictWriter(file,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(11,8))
 for name,label in zip(names,('baseline route','quadratic route')):
  r=[x for x in records if x['case']==name and x['finger']==0];t=[x['time_s']*1000 for x in r]
  for ax,key in zip(axes.ravel(),('skin_tip_z','skin75_mean_z_mm','skin_root_tip_total_angle_rad','object_z_mm')):ax.plot(t,[x[key] for x in r],label=label);ax.set(xlabel='actual physical time [ms]',ylabel=key);ax.legend()
 fig.suptitle('Actual3-film/free sphere,C2 original pulse,NO gravity/friction\nIncoming sphere impact coupon;NOT capture/wrapping/holding/lift;scale1');fig.tight_layout();fig.savefig(out/'actual_coupled_route_comparison.png',dpi=150);plt.close(fig);result=dict(status='PASS',scope='actual coupled route comparison,NOT time/mesh/grasp/superiority certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summaries={n:sha(d[0]/'summary.json') for n,d in zip(names,data)},common_exact_times=len(times),endpoint_time_s=times[-1],all_three_actual_tensions_exact=True,endpoint=[r for r in records if r['time_s']==times[-1]],contact_area=None,pressure=None,holding_load=None,gravity_lift='NOT RUN',matched_work=False,raw_hashes={f:sha(out/f) for f in ('shape.csv','actual_coupled_route_comparison.png')});write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='endpoint'}))
if __name__=='__main__':main()
