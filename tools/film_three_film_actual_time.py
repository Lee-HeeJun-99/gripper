"""Actual same-DLL3film refinement with separate skin/rail/attachment energies."""
import argparse,copy,csv,itertools,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_time import metric
def canonical_scene(path):
 tree=ET.parse(path);root=tree.getroot();root.attrib.pop('dt',None)
 for node in root.iter():
  for key in ('filename','displacementFilename'):node.attrib.pop(key,None)
  if node.tag=='ThreeFilmPersistentODE':node.attrib.pop('maxSteps',None)
 return ET.tostring(root)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);p.add_argument('--energies',nargs=3,required=True);a=p.parse_args();runs=[]
 for case,energy in zip(a.cases,a.energies):
  src=ROOT/'results'/('autonomous_film_'+case);observer=ROOT/'results'/('autonomous_film_'+energy);m=json.loads((src/'identity.json').read_text());s=json.loads((src/'summary.json').read_text());e=json.loads((observer/'summary.json').read_text())
  if s['status']!='PASS' or e['status']!='PASS' or e['case']!=case:raise ValueError('completed actual state and corresponding inventory required')
  for name,digest in e['raw_hashes'].items():
   if sha(src/name)!=digest:raise ValueError('actual inventory raw state changed:'+name)
  if runs:
   prior=runs[0]
   for key in ('binary_sha256','duration','external_force_N','tension_per_rail_N','material_parameters','geometry','sources'):
    if m[key]!=prior['meta'][key]:raise ValueError('different actual source/physical input:'+key)
   if canonical_scene(src/'scene.scn')!=canonical_scene(prior['path']/'scene.scn'):raise ValueError('physical XML differs beyond dt/count/output paths')
  states=list(csv.DictReader((src/'three.states.csv').open()));work=list(csv.DictReader((observer/'inventory.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));N=m['steps'];h=m['dt']
  if len(states)!=N or len(work)!=N or len(rows)!=9*N:raise ValueError('partial actual experiment')
  impulses=[];normal=[]
  for step in range(N):
   pbody=np.zeros(3);last=np.zeros(3)
   for stage in range(3):
    for f in range(3):
     row=rows[step*9+stage*3+f]
     if int(row['owner_finger'])!=f or abs(float(row['time'])-(step+(0,.5,1)[stage])*h)>1e-12:raise ValueError('used actual row ownership/time mismatch')
     pbody-=h*(2/3 if stage==1 else 1/6)*float(row['force'])*np.array([float(row[k]) for k in ('nx','ny','nz')])
     if stage==2:last[f]=float(row['force'])
   impulses.append(pbody);normal.append(last)
  runs.append(dict(name=case,path=src,meta=m,states=states,work=work,normal=np.array(normal),impulse=np.array(impulses),energy_case=energy))
 runs.sort(key=lambda r:r['meta']['steps']);pairs={}
 for left,right in itertools.combinations(runs,2):
  ratio=right['meta']['steps']//left['meta']['steps'];indices=np.arange(ratio-1,right['meta']['steps'],ratio);ls=left['states'];rr=[right['states'][k] for k in indices]
  if len(rr)!=len(ls) or max(abs(float(x['time'])-float(y['time'])) for x,y in zip(ls,rr))>1e-12:raise ValueError('no common actual physical output times')
  errors={};lw=left['work'];rw=[right['work'][k] for k in indices]
  for x,y in zip(ls,lw):
   if abs(float(x['time'])-float(y['time']))>1e-12:raise ValueError('actual energy clock mismatch')
  for key in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation','external_work','damping_work','cumulative_tendon_work'):errors[key]=metric(np.array([float(x[key]) for x in lw]),np.array([float(x[key]) for x in rw]))
  for key in ('q','v'):
   x=np.array([np.fromstring(s[key],sep=' ') for s in ls]);y=np.array([np.fromstring(s[key],sep=' ') for s in rr]);errors[key]=metric(x,y)
   if key=='q':
    initial=np.array([0,0,-63.44761697652639]);errors['film_displacement']=metric(x[:,:-6],y[:,:-6]);errors['body_displacement']=metric(x[:,-6:-3]-initial,y[:,-6:-3]-initial)
  errors['normal_force']=metric(left['normal'],right['normal'][indices]);coarse=left['impulse']/left['meta']['dt'];fine=right['impulse'].reshape(len(ls),ratio,3).sum(axis=1)/left['meta']['dt'];errors['common_window_body_contact_force']=metric(coarse,fine)
  pairs[left['name']+'__'+right['name']]=dict(status='PASS' if all(v['status']=='PASS' for v in errors.values()) else 'FAIL',errors=errors,integration_defect_observations={key:metric(np.array([float(x[key]) for x in lw]),np.array([float(x[key]) for x in rw])) for key in ('contact_work','signed_energy_residual')})
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(p['status']=='PASS' for p in pairs.values()) else 'FAIL',scope='actual3film/ONEfreeSphere100us REST/T0/-1mN fixed patch time gate for listed observables ONLY;NOT closing/impact/fullenergy/grasp',relative_gate=.001,pairs=pairs,cases=[r['name'] for r in runs],energy_observers=[r['energy_case'] for r in runs],raw={r['name']:{f:sha(r['path']/f) for f in ('identity.json','scene.scn','three.states.csv','three.rows.csv')} for r in runs},not_qualified=['full C2 closing/hold/release','impact/birth in3finger owner','mesh/friction/self-contact','independent full force/Jacobian API','full energy certificate','lift/holding/grasp/12wrench/Optuna'])
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(10,4))
 for r in runs:
  t=[float(x['time']) for x in r['work']];axes[0].plot(t,[float(x['U_rails']) for x in r['work']],'.-',label=str(r['meta']['steps'])+' steps');axes[1].plot(t,r['normal'].sum(axis=1),'.-',label=str(r['meta']['steps']))
 axes[0].set_ylabel('Actual-state rail energy [N mm]');axes[1].set_ylabel('Actual end-stage normal force sum [N]')
 for ax in axes:ax.set_xlabel('Physical time [s]');ax.grid();ax.legend()
 fig.suptitle('Actual SOFA REST-contact,T=0;NOT closing/grasp qualification');fig.tight_layout();fig.savefig(out/'actual_time.png',dpi=170);plt.close(fig);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],pairs={k:{n:v.get('relative_error') for n,v in p['errors'].items()} for k,p in pairs.items()})))
if __name__=='__main__':main()
