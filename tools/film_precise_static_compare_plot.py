"""Completed common-load static states, explicitly NOT actual SOFA or contact."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();base=ROOT/'results/autonomous_film_20261119_precise_static_geometric1730';other=ROOT/'results/autonomous_film_20261119_precise_static_geometric_aspects1733';sources={.1:base,.075:other,.125:other};data={};proof={}
 for thick,parent in sources.items():
  m=json.loads((parent/'summary.json').read_text());file=parent/str(thick)/'equilibrium.states.csv'
  if sha(file)!=m['raw_hashes'][str(thick)+'/equilibrium.states.csv']:raise ValueError('immutable partial branch changed')
  data[thick]={int(x['stage']):x for x in csv.DictReader(file.open())};proof[str(thick)]=dict(summary_sha256=sha(parent/'summary.json'),binary_sha256=m['binary_sha256'],full_load_status=m['status'])
 stage=max(set.intersection(*(set(x) for x in data.values())));selected={t:rows[stage] for t,rows in data.items()};tensions={x['T'] for x in selected.values()}
 if len(tensions)!=1 or any(float(x['residual_N'])>1e-12 for x in selected.values()):raise ValueError('same T and completed force equilibrium required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records=[]
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(11,4));x=np.linspace(0,100,21)
 for t,row in selected.items():
  q=np.fromstring(row['q'],sep=' ').reshape(231,3);s=shape(q.ravel());record=dict(rail_thickness_mm=t,rail_width_mm=(439.3397917746089/3-120)/(200*t),T_N=float(row['T']),force_residual_N=float(row['residual_N']),**s,**{k:float(row[k]) for k in ('U_skin','U_rails','U_attachment')},tendon_shortening_mm=200-float(row['cable_length_mm']));records.append(record);skin=q[:105].reshape(21,5,3);axes[0].plot(x,skin[:,:,2].mean(axis=1),label=str(t*1000)+'um Rail');axes[1].plot(x,np.mean(q[105:168].reshape(21,3,3)[:,:,2],axis=1),label=str(t*1000)+'um Rail')
 for ax,title in zip(axes,('Skin width-mean displacement','Left Rail width-mean displacement')):ax.set(xlabel='Material x [mm]',ylabel='Displacement z [mm]',title=title);ax.legend();ax.grid(alpha=.3)
 fig.suptitle('Independent nonlinear static FEM, no object/contact — T='+format(float(next(iter(tensions))),'.6g')+' N/Rail\nActual stored static states; NOT SOFA, wrapping, stability or grasp evidence');fig.tight_layout();fig.savefig(out/'static_common_load.png',dpi=150);plt.close(fig)
 with (out/'comparison.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 r=dict(status='COMPARISON_ONLY',scope='completed common-load nonlinear static states;NOT failed full-load continuation/contact/actual SOFA/wrapping/stability/grasp',proof=proof,selected_stage=stage,T_N=float(next(iter(tensions))),core_volume_mm3_three_fingers=439.3397917746089,equal_material=True,equal_tension=True,equal_actuation_work=False,contact_area=None,pressure=None,holding_capacity=None,selected_design=None,metrics=records,raw_hashes={f.name:sha(f) for f in out.iterdir() if f.is_file()});write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('metrics','proof','raw_hashes')}))
if __name__=='__main__':main()
