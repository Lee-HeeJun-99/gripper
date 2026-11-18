"""Accepted Gauss-stage transmission sign/time response;no contact inference."""
import csv,json,argparse,shutil,os,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_routed_candidate_full1244';obs=ROOT/'results/autonomous_film_20261118_routed_station1253';old=ROOT/'results/autonomous_film_20261118_routed_work_full1250';meta=json.loads((obs/'summary.json').read_text());prior=json.loads((old/'summary.json').read_text());actual=json.loads((src/'summary.json').read_text())
 for path,m in ((src,actual),(obs,meta),(old,prior)):
  if m['status']!='PASS':raise ValueError('complete actual and read-only observers required')
  for f,d in m['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('immutable actual/observer changed')
 if meta['source_summary_sha256']!=prior['source_summary_sha256'] or meta['source_summary_sha256']!=sha(src/'summary.json'):raise ValueError('SAME actual physical path required')
 rows=list(csv.DictReader((obs/'stage_work.csv').open()));before=list(csv.DictReader((old/'stage_work.csv').open()));stages=list(csv.DictReader((src/'actual.csv.stages.csv').open()));same=len(rows)==len(before)==len(stages) and all(all(r[k]==b[k] for k in b) for r,b in zip(rows,before))
 if not same:raise ValueError('new station instrumentation altered old work/force outputs')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');values=[]
 for r,s in zip(rows,stages):
  if r['time']!=s['time']:raise ValueError('actual stage clocks differ')
  q=np.fromstring(s['q'],sep=' ').reshape(231,3);v=np.fromstring(s['v'],sep=' ').reshape(231,3);values.append(dict(time_s=float(r['time']),T_N=float(r['T']),skin75_mean_z_mm=float(q[75:80,2].mean()),skin75_mean_vz_mm_s=float(v[75:80,2].mean()),**{k:float(r[k]) for k in ('skin75_attachment_Fz_N','rail75_attachment_Fz_N','rail75_tendon_Fz_N')}))
 with (out/'response.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(3,1,figsize=(10,9));t=[r['time_s']*1000 for r in values]
 for k in ('skin75_attachment_Fz_N','rail75_attachment_Fz_N','rail75_tendon_Fz_N'):axes[0].plot(t,[r[k] for r in values],label=k)
 axes[0].set_ylabel('actual force component [N]');axes[0].legend();axes[1].plot(t,[r['skin75_mean_z_mm'] for r in values]);axes[1].set_ylabel('Skin75 mean z [mm]');axes[2].plot(t,[r['skin75_mean_vz_mm_s'] for r in values]);axes[2].set(ylabel='Skin75 mean vz [mm/s]',xlabel='physical Gauss-stage time [ms]');fig.suptitle('Actual SOFA no-object quadratic route,Tmax0.0001N/rail\nMaterial75mm station forces,NOT normal reaction/holding load;scale1');fig.tight_layout();fig.savefig(out/'actual_transmission_response.png',dpi=150);plt.close(fig)
 result=dict(status='PASS',scope='read-only actual material-station force response;NOT contact force/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),observer_summary_sha256=sha(obs/'summary.json'),old_columns_exact=same,samples=len(values),range={k:dict(minimum=min(r[k] for r in values),maximum=max(r[k] for r in values)) for k in values[0] if k!='time_s'},actual_contact_force=None,root_reaction=None,raw_hashes={f:sha(out/f) for f in ('response.csv','actual_transmission_response.png')});write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
