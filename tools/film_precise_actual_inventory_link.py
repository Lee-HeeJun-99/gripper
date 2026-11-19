"""Bind offline stage inventory to identical actual SOFA states;retain energy FAIL."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();energy=ROOT/'results/autonomous_film_20261119_plan_energy1742';em=json.loads((energy/'summary.json').read_text());reference=ROOT/'results/autonomous_film_20261119_precise_solver_plan1737';names=('20261119_plan_actual1743','20261119_plan_actual_half1744','20261119_plan_actual_quarter1745')
 for f,d in em['raw_hashes'].items():
  if sha(energy/f)!=d:raise ValueError('immutable offline inventory changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='FAIL',scope='actual-state/stage-linked partial work/energy inventory and actual unscaled shape plots;NOT whole-energy/contact/wrapping/grasp',energy_summary_sha256=sha(energy/'summary.json'),root_reaction_work=None,whole_energy_status='BLOCKED',partial_residual_time_status='FAIL retained',trials={});plot=[]
 for n,name in zip((40,80,160),names):
  parent=ROOT/'results'/('autonomous_film_'+name);m=json.loads((parent/'summary.json').read_text())
  if m['status']!='PASS':raise ValueError('completed actual API trial required')
  for f,d in m['raw_hashes'].items():
   if sha(parent/f)!=d:raise ValueError('actual raw changed')
  common={f:d for f,d in em['source_hashes'].items() if f.endswith('.h') and f in m['source_hashes']}
  if not common or any(m['source_hashes'][f]!=d for f,d in common.items()):raise ValueError('offline/actual physical headers mismatch')
  states=list(csv.DictReader((parent/'actual.csv').open()));ref=list(csv.DictReader((reference/str(n)/'state.csv').open()));stages=list(csv.DictReader((parent/'actual.csv.gauss4.csv').open()));truth=list(csv.DictReader((reference/str(n)/'state.csv.stages.csv').open()));fields=list(csv.DictReader((parent/'film.csv').open()));inventory=list(csv.DictReader((energy/str(n)/'energy.csv').open()))
  if len(states)!=len(ref) or len(stages)!=len(truth) or not len(fields)==len(inventory)==n:raise ValueError('complete inventory/state count required')
  exact_states=all(all(x[k]==y[k] for k in ('q','v','time')) for x,y in zip(states,ref));exact_stages=all(all(x[k]==y[k] for k in ('q','v','time','T','weight_s','reduced_physical_force_N')) for x,y in zip(stages,truth))
  mismatch=max(max(abs(float(f['U_shell'])-float(e['U_skin'])-float(e['U_rails'])),abs(float(f['U_attachment'])-float(e['U_attachment'])),abs(float(f['K'])-float(e['K']))) for f,e in zip(fields,inventory))
  trial=dict(actual_summary_sha256=sha(parent/'summary.json'),accepted_state_strings_EXACT=exact_states,stage_strings_EXACT=exact_stages,Field_energy_max_abs_Nmm=mismatch,common_physical_header_count=len(common),status='PASS' if exact_states and exact_stages and mismatch<=1e-12 else 'FAIL');r['trials'][str(n)]=trial
  for s in states:plot.append(dict(steps=n,time_s=float(s['time']),tension_N=float(s['T_end']),**shape(np.fromstring(s['q'],sep=' '))))
 r['actual_inventory_link_status']='PASS' if all(x['status']=='PASS' for x in r['trials'].values()) else 'FAIL';r['signed_residual_worst']=em['worst'];r['components_time_status']='PASS' if all(float(x['relative'])<=.001 for x in csv.DictReader((energy/'errors.csv').open()) if x['quantity']!='signed_partial_defect' and x['relative']) else 'FAIL'
 with (out/'actual_shapes.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(plot[0]));w.writeheader();w.writerows(plot)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,2,figsize=(11,7));keys=('skin_tip_z','left_tip_z','skin_max_curvature_per_mm','tension_N');labels=('Skin width-mean tip z [mm]','Left Rail width-mean tip z [mm]','Skin max curvature [1/mm]','Actual tendon tension [N/Rail]')
 for ax,key,label in zip(axes.flat,keys,labels):
  for n in (40,80,160):
   rows=[x for x in plot if x['steps']==n];ax.plot([x['time_s']*1000 for x in rows],[x[key] for x in rows],label=str(n)+' public steps')
  ax.set(xlabel='Actual accumulated time [ms]',ylabel=label);ax.grid(alpha=.3);ax.legend()
 fig.suptitle('Actual SOFA accepted states —1ms free precise coupon, no object/contact\nNo displacement amplification; NOT wrapping/grasp evidence; binary ef4f9ebe2b17');fig.tight_layout();fig.savefig(out/'actual_plan_1ms.png',dpi=150);plt.close(fig);r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file()};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('trials','raw_hashes')}))
if __name__=='__main__':main()
