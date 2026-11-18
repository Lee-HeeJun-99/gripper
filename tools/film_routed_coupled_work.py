"""Offline new-route first-impact+Lobatto stage work,actual accepted states."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_compiled_sources import compiled_sources
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS':raise ValueError('complete qualified actual routed contact path required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual contact data changed')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('physical source archive changed')
 first=list(csv.DictReader((src/'three.first_interval.csv').open()));states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));N=len(states);nf=(len(np.fromstring(states[0]['q'],sep=' '))-6)//3
 if [r['stage'] for r in first]!=['initial','free_midpoint','pre_impact','post_impact','contact_initial','contact_midpoint','contact_end'] or len(rows)!=9*(N-1):raise ValueError('complete first interval and all subsequent3-stage/3-row transactions required')
 if first[2]['q']!=first[3]['q'] or first[3]['q']!=first[4]['q'] or first[3]['v']!=first[4]['v']:raise ValueError('impact state discontinuity ownership differs')
 for k in ('q','v'):
  if not np.array_equal(np.fromstring(first[-1][k],sep=' '),np.fromstring(states[0][k],sep=' ')):raise ValueError('first interval endpoint differs')
 samples=[(r['stage'],float(r['time']),r['q'],r['v']) for r in first];transactions=[[(r['stage'],float(r['weight_s']),float(r['normal_power_Nmm_s'])) for r in first]]
 if abs(sum(w for name,w,power in transactions[0])-float(states[0]['time']))>1e-18:raise ValueError('first physical quadrature duration differs')
 for i,state in enumerate(states):
  samples.append(('end'+str(i),float(state['time']),state['q'],state['v']))
  if i==0:continue
  t0=float(states[i-1]['time']);h=m['dt_s'];transaction=[]
  if float(state['time'])!=t0+h:raise ValueError('actual accumulated public clock differs from recorded used dt')
  for k in range(3):
   group=rows[9*(i-1)+3*k:9*(i-1)+3*k+3];r=group[0];time=t0+h*(0,.5,1)[k]
   if any(int(row['owner_finger'])!=f or row['stage_q']!=r['stage_q'] or row['stage_v']!=r['stage_v'] or float(row['time'])!=time for f,row in enumerate(group)):raise ValueError('actual owned-stage/time mismatch;no interpolation')
   name=f'stage{i}_{k}';samples.append((name,time,r['stage_q'],r['stage_v']));transaction.append((name,h*(2/3 if k==1 else 1/6),sum(float(row['force'])*float(row['normal_velocity']) for row in group)))
  transactions.append(transaction)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/DrivenPower.cpp';cpp.parent.mkdir(parents=True);text=(ROOT/'diagnostics/film_three_finger/DrivenPower.cpp').read_text();changes={'#include "../../models/film_three_finger/FrameLayout.h"':'#include "../../models/film_three_finger/FrameLayout.h"\n#include "../../models/film_routed_tendon/Route.h"','film.model.elements(x,1.,':'regrip_routed_tendon::elements(film.model,x,1.,4.5,','film.model.cableLength(x)':'regrip_routed_tendon::length(film.model,x,4.5)'}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('exact routed observer source anchor differs')
  text=text.replace(old,new)
 cpp.write_text(text);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};(out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(name+' '+format(t,'.17g')+' '+q+' '+v for name,t,q,v in samples)+'\n');binary=out/'observer'
 if a.reuse:
  prev=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prev/'summary.json').read_text())
  if old['status']!='PASS' or compiled_sources(old['source_hashes'])!=compiled_sources(sources) or sha(prev/'observer')!=old['observer_binary_sha256']:raise ValueError('exact observer source/binary required')
  if 2*old['process']['runtime_s']*len(samples)/old['samples']+30>480:raise ValueError('observer cost forecast>480s')
  shutil.copy2(prev/'observer',binary);compile=dict(exit_code=0,reused_from=a.reuse)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,src/'public_mass_reference.txt',out/'samples.txt',out/'observed.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='offline actual new-route first-impact+subsequent stage-work inventory;NOT whole energy/time/grasp certificate',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),source_hashes=sources,compile=compile,process=run,samples=len(samples),root_reaction_work=None,full_energy_gate='BLOCKED',residual_is_heat=False)
 if run and run['exit_code']==0:
  obs={r['sample']:{k:float(v) for k,v in r.items() if k!='sample'} for r in csv.DictReader((out/'observed.csv').open())};scene=ET.parse(src/'scene.scn').getroot();owner=next(n for n in scene if n.tag.startswith('RoutedThreeFilm') and n.tag.endswith('ODE'));F=np.fromstring(owner.get('externalForce'),sep=' ');c=float(owner.get('rayleighMass'));fields=[list(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)];values={name:(t,np.fromstring(v,sep=' ')) for name,t,q,v in samples};energy=lambda v:sum(v[k] for k in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation'));kinetic=lambda v:sum(v[k] for k in ('K_film','K_linear','K_rotation'));W=We=D=C=error=control=length=0.;journal=[];loss=float(next(csv.DictReader((src/'three.event.csv').open()))['energy_loss'])
  for i,transaction in enumerate(transactions):
   for name,w,power in transaction:
    value=obs[name];time,v=values[name];W+=w*value['profile_tension']*value['unit_tendon_power'];We+=w*F.dot(v[3*nf:3*nf+3]);D+=w*2*c*kinetic(value);C+=w*power
   end=obs['end'+str(i)];error=max(error,abs(sum(float(f[i]['U_shell']) for f in fields)-end['U_skin']-end['U_rails']),abs(sum(float(f[i]['U_attachment']) for f in fields)-end['U_attachment']),abs(sum(float(f[i]['K']) for f in fields)-end['K_film']));control=max(control,max(abs(float(f[i]['T_per_rail'])-end['profile_tension']) for f in fields));length=max(length,abs(sum(float(f[i]['cable_length']) for f in fields)-end['cable_length']));change=energy(end)-energy(obs['initial']);journal.append(dict(time_s=float(states[i]['time']),**end,tendon_work_Nmm=W,external_work_Nmm=We,damping_work_Nmm=D,normal_constraint_work_Nmm=C,plastic_impact_loss_Nmm=loss,energy_change_Nmm=change,signed_energy_defect_Nmm=change-W-We+D-C+loss))
  with (out/'inventory.csv').open('w') as file:writer=csv.DictWriter(file,fieldnames=list(journal[0]));writer.writeheader();writer.writerows(journal)
  r.update(status='PASS' if error<=1e-12 and control<=1e-18 and length<=1e-12 else 'FAIL',actual_field_energy_error_Nmm=error,actual_endpoint_control_error_N=control,cable_length_error_mm=length,final_inventory=journal[-1],observer_binary_sha256=sha(binary),raw_hashes={f:sha(out/f) for f in ('observed.csv','inventory.csv')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
