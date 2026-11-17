"""Actual driven-state inventory;unit routed-cable gradient gives -T dL/dt.

Observed signed residual is NOT physical heat or a full gripper energy gate.
"""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_three_film_qualified import require_completed
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reuse');p.add_argument('--qualification');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text());s=json.loads((src/'summary.json').read_text());qualification=require_completed(src,a.qualification)
 if not meta['actual_solver'].startswith('ThreeFilmDriven'):raise ValueError('completed actual C2 owner required')
 scene=ET.parse(src/'scene.scn');owner=scene.find('ThreeFilmDrivenODE')
 if owner is None:owner=scene.find('ThreeFilmDrivenExactODE')
 for f in scene.findall('.//FilmRailTendon'):
  if any(float(f.get(k))!=v for k,v in dict(maximumTension=.0001,rampTime=.01,releaseBegin=.02,releaseEnd=.03,c2Control=1).items()):raise ValueError('explicit shared C2 pilot Data required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/DrivenPower.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/DrivenPower.cpp',cpp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 mass=[np.fromstring(scene.find('Node[@name="finger'+str(f)+'"]//DiagonalMass').get('vertexMass'),sep=' ') for f in range(3)];rigid=np.fromstring(scene.find('Node[@name="free_object"]//UniformMass').get('vertexMass'),sep=' ')
 with (out/'mass.txt').open('w') as stream:stream.write(str(len(mass[0]))+'\n'+'\n'.join(' '.join(format(x,'.17g') for x in m) for m in mass)+'\n'+format(rigid[0],'.17g')+' '+format(rigid[0]*rigid[2],'.17g')+'\n')
 states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));films=[list(csv.DictReader((src/('film_'+str(f)+'.csv')).open())) for f in range(3)];N=meta['steps'];h=meta['dt'];nf=(len(np.fromstring(states[0]['q'],sep=' '))-6)//3
 if len(states)!=N or len(rows)!=9*N or any(len(f)!=N for f in films):raise ValueError('incomplete actual traces')
 samples=[('initial',0.,rows[0]['stage_q'],rows[0]['stage_v'])];stages={}
 for i,state in enumerate(states):
  samples.append(('end'+str(i),float(state['time']),state['q'],state['v']))
  for k in range(3):
   group=rows[9*i+3*k:9*i+3*k+3];first=group[0];clock=(i+(0,.5,1)[k])*h
   if any(int(r['owner_finger'])!=j or abs(float(r['time'])-clock)>1e-12 or r['stage_q']!=first['stage_q'] or r['stage_v']!=first['stage_v'] for j,r in enumerate(group)):raise ValueError('actual owned stage/clock mismatch')
   name='stage'+str(i)+'_'+str(k);samples.append((name,float(first['time']),first['stage_q'],first['stage_v']));stages[i,k]=(name,group)
 with (out/'samples.txt').open('w') as stream:stream.write(str(len(samples))+'\n'+'\n'.join(name+' '+format(t,'.17g')+' '+q+' '+v for name,t,q,v in samples)+'\n')
 binary=out/'reference'
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prior/'summary.json').read_text());binary=prior/'reference'
  if old['status']!='PASS' or sha(binary)!=old['binary_sha256'] or any(sources.get(k)!=v for k,v in old['sources'].items() if k.endswith('.h') or k.endswith('/DrivenPower.cpp')):raise ValueError('compiled observer identity mismatch')
  compile=dict(exit_code=0,reused=a.reuse)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='actual C2 stored/kinetic and routed-tendon/stage power inventory;NOT full work/energy certificate',case=a.case,sources=sources,compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),raw_hashes={f:sha(src/f) for f in ('identity.json','scene.scn','three.states.csv','three.rows.csv','film_0.csv','film_1.csv','film_2.csv')},root_work='ideal static-root assumption,not independent reaction measurement',missing=['full cycle','generic friction/self-contact/pressure','independent root reaction work','general rotating-object torque work'])
 if run and run['exit_code']==0:
  observed={r['sample']:{k:float(v) for k,v in r.items() if k!='sample'} for r in csv.DictReader((out/'observed.csv').open())};keys=('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation');energy=lambda row:sum(row[k] for k in keys);previous=observed['initial'];external=damping=contact=tendon=residual=error=control_error=length_error=0.;journal=[];F=np.fromstring(owner.get('externalForce'),sep=' ');c=float(owner.get('rayleighMass'))
  for i,state in enumerate(states):
   sw=sd=sc=st=0.
   for k in range(3):
    name,group=stages[i,k];value=observed[name];weight=h*(2/3 if k==1 else 1/6);v=np.fromstring(group[0]['stage_v'],sep=' ');sw+=weight*F.dot(v[3*nf:3*nf+3]);sd+=weight*2*c*sum(value[key] for key in ('K_film','K_linear','K_rotation'));sc+=weight*sum(float(r['force'])*float(r['normal_velocity']) for r in group);st+=weight*value['profile_tension']*value['unit_tendon_power']
   value=observed['end'+str(i)];external+=sw;damping+=sd;contact+=sc;tendon+=st;field_work=sum(float(f[i]['tendon_work']) for f in films)
   error=max(error,abs(sum(float(f[i]['U_shell']) for f in films)-value['U_skin']-value['U_rails']),abs(sum(float(f[i]['U_attachment']) for f in films)-value['U_attachment']),abs(sum(float(f[i]['K']) for f in films)-value['K_film']));control_error=max(control_error,max(abs(float(f[i]['T_per_rail'])-value['profile_tension']) for f in films));length_error=max(length_error,abs(sum(float(f[i]['cable_length']) for f in films)-value['cable_length']));residual+=energy(value)-energy(previous)-sw-st+sd-sc;previous=value;journal.append(dict(time=float(state['time']),**value,external_work=external,damping_work=damping,contact_work=contact,tendon_work=tendon,field_sampled_tendon_work=field_work,signed_energy_residual=residual))
  if not all(np.isfinite(v) for r in journal for v in r.values()):raise ValueError('nonfinite inventory')
  with (out/'inventory.csv').open('w') as stream:w=csv.DictWriter(stream,fieldnames=journal[0]);w.writeheader();w.writerows(journal)
  result.update(status='PASS' if error<=1e-12 and control_error<=1e-18 and length_error<=1e-12 else 'FAIL',binary_sha256=sha(binary),ff_energy_error=error,accepted_tension_error_N=control_error,cable_length_error_mm=length_error,final_inventory=journal[-1],energy_gate='NOT ASSESSED:residual is not heat',tendon_sign='positive work=-integral T*dL;T is prescribed PER routed rail;not stored cable energy',stage_input_note='reconstructed existing ControlProfile at recorded stage times,not direct trial-tension log')
 result['explicit_reassessment']=qualification
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','ff_energy_error','final_inventory') if k in result}))
if __name__=='__main__':main()
