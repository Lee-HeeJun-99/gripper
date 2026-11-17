"""Independent matched actual-state energy/power inventory;NOT energy certificate.

Lobatto stage work plus the actual pre-impact partial-midpoint contribution.
No unmeasured term is filled with zero or residual reclassified as heat.
"""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reuse',help='exact energy diagnostic CPP and transitive headers;runtime physical input remains explicit');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text())
 if json.loads((src/'summary.json').read_text())['status']!='PASS' or not meta.get('combined_contact'):raise ValueError('completed actual combined accepted path required')
 ref=ROOT/'results'/('autonomous_film_'+meta['reference']);refmeta=json.loads((ref/'summary.json').read_text());out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');shutil.copy2(ref/'input.txt',out/'mechanics.txt')
 for name,digest in meta['sources'].items():
  if name.endswith('.h') and sha(archive/name)!=digest:raise ValueError('actual compiled energy model source drift:'+name)
 cpp=archive/'diagnostics/film_coupled_reintegrated/CombinedEnergy.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_coupled_reintegrated/CombinedEnergy.cpp',cpp)
 tree=ET.parse(src/'scene.scn');nx=int(tree.find('.//FilmRailTendon').get('nx'));count=nx*11;index=np.full(3*count,-1,dtype=int);weight=np.ones(3*count);nf=0
 for offset,ny in ((0,5),(5*nx,3),(8*nx,3)):
  for i in range(1,nx):
   for j in range(ny):
    for d in range(3):
     if i!=1 or d!=2:index[3*(offset+i*ny+j)+d]=nf;nf+=1
  for j in range(ny):index[3*(offset+ny+j)+2]=index[3*(offset+2*ny+j)+2];weight[3*(offset+ny+j)+2]=.25
 def expand(x):
  v=np.zeros(3*count);free=index>=0;v[free]=weight[free]*x[index[free]];return v
 def decode(s):return [np.fromstring(s[k],sep=' ') for k in ('local_displacement','local_velocity','body_center','body_velocity','body_omega')]
 initial=[np.fromstring(meta[k],sep=' ') for k in ('initial_displacement','initial_velocity','initial_body_center','initial_body_velocity')];initial=[*initial[:3],initial[3][:3],initial[3][3:]]
 states=list(csv.DictReader((src/'coupled.states.csv').open()));stages=list(csv.DictReader((src/'coupled.stages.csv').open()));events=list(csv.DictReader((src/'coupled.event_states.csv').open()));impacts=list(csv.DictReader((src/'coupled.events.csv').open()));samples=[('initial',meta['start_time'],initial)];before=initial;start=meta['start_time'];preterms={}
 for i,s in enumerate(states):
  end=float(s['time']);samples.append(('end'+str(i),end,decode(s)));births=[b for b in events if b['stage']=='pre' and start<float(b['time'])<=end]
  if births:
   if len(births)!=1:raise ValueError('one event subintegration per macro required')
   birth=births[0];pre=decode(birth);tau=float(birth['time'])-start;name='premid'+str(i);samples.append((name,start+tau/2,[(x+y)/2 for x,y in zip(before,pre)]));preterms[i]=(name,tau)
  before=decode(s);start=end
 for i,s in enumerate(stages):
  q=np.fromstring(s['q'],sep=' ');v=np.fromstring(s['v'],sep=' ');samples.append(('stage'+str(i),float(s['stage_time']),[expand(q),expand(v),q[nf:nf+3],v[nf:nf+3],v[nf+3:nf+6]]))
 with (out/'samples.txt').open('w') as f:
  f.write(str(len(samples))+'\n')
  for name,time,values in samples:f.write(name+' '+format(time,'.17g')+' '+' '.join(format(float(x),'.17g') for v in values for x in v)+'\n')
 binary=out/'reference'
 if a.reuse:
  reused=ROOT/'results'/('autonomous_film_'+a.reuse);prior=json.loads((reused/'summary.json').read_text());binary=reused/'reference'
  if prior['status']!='PASS' or sha(binary)!=prior['binary_sha256']:raise ValueError('energy observer binary changed')
  for name,digest in prior['sources'].items():
   if (name.endswith('.h') or name.endswith('/CombinedEnergy.cpp')) and (not (archive/name).is_file() or sha(archive/name)!=digest):raise ValueError('compiled pure energy observer header/CPP differs:'+name)
  compile=dict(exit_code=0,reused=a.reuse,scope='same compiled pure observer headers/CPP;unused SOFA owner sources not compiled into this executable')
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'mechanics.txt',out/'samples.txt',out/'observed.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent inventory on actual accepted/event/stage states;NOT full physical energy/time certificate',case=a.case,compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},input_hashes={f:sha(out/f) for f in ('mechanics.txt','samples.txt')},actual_hashes={f:sha(src/f) for f in ('identity.json','scene.scn','coupled.states.csv','coupled.event_states.csv','coupled.stages.csv','coupled.events.csv')},not_measured=['full-cycle energy','pressure/vacuum actuator work','friction history work','self-contact work','independent actual root-reaction work'],root_model_assumption='fixed time-independent ideal root mapping:no allowed-motion reaction power;not a measured reaction journal')
 if result['status']=='PASS':
  observed={r['name']:{k:float(v) for k,v in r.items() if k!='name'} for r in csv.DictReader((out/'observed.csv').open())};terms=('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation');energy=lambda s:sum(s[k] for k in terms);previous=observed['initial'];rows=[];totals=dict(tendon=0.,damping=0.,external=0.,contact=0.,impact=0.);start=meta['start_time'];ff_error=0.
  if not all(np.isfinite(v) for sample in observed.values() for v in sample.values()):raise ValueError('nonfinite actual energy observer output;not silently zeroed')
  for i,s in enumerate(states):
   end=float(s['time']);local={k:0. for k in totals}
   def add(value,dt):local['tendon']-=dt*value['tension']*value['cable_power'];local['damping']+=dt*value['damping_power'];local['external']+=dt*value['external_power']
   if i in preterms:name,tau=preterms[i];add(observed[name],tau)
   for j,stage in enumerate(stages):
    if abs(float(stage['macro_start'])-start)<1e-12:add(observed['stage'+str(j)],float(stage['weighted_time']));local['contact']+=float(stage['weighted_time'])*float(stage['normal_force'])*float(stage['normal_velocity'])
   atom_times={r['time'] for r in impacts if start<float(r['time'])<=end};local['impact']=sum(float(next(r for r in impacts if r['time']==t)['impact_loss']) for t in atom_times)
   value=observed['end'+str(i)];ff_error=max(ff_error,abs(value['U_skin']+value['U_rails']-float(s['U_shell'])),abs(value['U_attachment']-float(s['U_attachment'])),abs(value['K_film']-float(s['K_film'])))
   residual=energy(value)-energy(previous)-local['tendon']-local['external']-local['contact']+local['damping']+local['impact'];rows.append(dict(time=end,energy=energy(value),delta_energy=energy(value)-energy(previous),**local,integration_energy_residual=residual))
   for k,v in local.items():totals[k]+=v
   previous=value;start=end
  with (out/'inventory.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
  result.update(status='PASS' if ff_error<1e-11 else 'FAIL',binary_sha256=sha(binary),ff_observer_error=ff_error,metrics=dict(delta_energy=energy(previous)-energy(observed['initial']),**totals,total_signed_residual=sum(r['integration_energy_residual'] for r in rows),maximum_step_residual=max(abs(r['integration_energy_residual']) for r in rows)),energy_gate='NOT ASSESSED:no residual is relabeled physical heat or arbitrary dissipation')
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','metrics','ff_observer_error')}))
if __name__=='__main__':main()
