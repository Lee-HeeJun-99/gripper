"""Independent per-component inventory on actual3film accepted/stage states.

T=0 is a measured input here,not an unimplemented work term replaced by zero.
The residual is NOT heat or a full energy certificate.
"""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text())
 if json.loads((src/'summary.json').read_text())['status']!='PASS':raise ValueError('completed actual shared3film required')
 scene=ET.parse(src/'scene.scn');owner=scene.find('ThreeFilmPersistentODE')
 if owner is None or any(float(f.get('maximumTension'))!=0 for f in scene.findall('.//FilmRailTendon')):raise ValueError('qualified REST/T0 three-film input only')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/ActualEnergy.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/ActualEnergy.cpp',cpp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 mass=[]
 for f in range(3):mass.append(np.fromstring(scene.find('Node[@name="finger'+str(f)+'"]//DiagonalMass').get('vertexMass'),sep=' '))
 rigid=np.fromstring(scene.find('Node[@name="free_object"]//UniformMass').get('vertexMass'),sep=' ');body_mass=rigid[0];inertia=body_mass*rigid[2]
 with (out/'mass.txt').open('w') as stream:stream.write(str(len(mass[0]))+'\n'+'\n'.join(' '.join(format(v,'.17g') for v in row) for row in mass)+'\n'+format(body_mass,'.17g')+' '+format(inertia,'.17g')+'\n')
 states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));films=[list(csv.DictReader((src/('film_'+str(f)+'.csv')).open())) for f in range(3)];N=meta['steps'];h=meta['dt'];nf=(len(np.fromstring(states[0]['q'],sep=' '))-6)//3
 if len(states)!=N or len(rows)!=9*N or any(len(f)!=N for f in films):raise ValueError('incomplete actual accepted/field/stage inventory')
 samples=[('initial',rows[0]['stage_q'],rows[0]['stage_v'])];stages={}
 for i,s in enumerate(states):
  samples.append(('end'+str(i),s['q'],s['v']))
  for k in range(3):
   group=rows[9*i+3*k:9*i+3*k+3];first=group[0];clock=(i+(0,.5,1)[k])*h
   if any(int(r['owner_finger'])!=j or abs(float(r['time'])-clock)>1e-12 or r['stage_q']!=first['stage_q'] or r['stage_v']!=first['stage_v'] for j,r in enumerate(group)):raise ValueError('fixed-row owner order/physical clock/state differs')
   name='stage'+str(i)+'_'+str(k);samples.append((name,first['stage_q'],first['stage_v']));stages[i,k]=(name,group)
 with (out/'samples.txt').open('w') as stream:stream.write(str(len(samples))+'\n'+'\n'.join(name+' '+q+' '+v for name,q,v in samples)+'\n')
 binary=out/'reference'
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);pm=json.loads((prior/'summary.json').read_text());binary=prior/'reference'
  if pm['status']!='PASS' or sha(binary)!=pm['binary_sha256']:raise ValueError('actual energy binary differs')
  for name,digest in pm['sources'].items():
   if (name.endswith('.h') or name.endswith('/ActualEnergy.cpp')) and sources.get(name)!=digest:raise ValueError('compiled observer differs:'+name)
  compile=dict(exit_code=0,reused=a.reuse)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='independent inventory of actual3film accepted/stage states,explicit T0;NOT full energy certificate',case=a.case,sources=sources,compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),raw_hashes={f:sha(src/f) for f in ('identity.json','scene.scn','three.states.csv','three.rows.csv','film_0.csv','film_1.csv','film_2.csv')},missing=['independent root reaction work','friction/self-contact/pressure work models','full cycle','generic rotating-rigid torque work'])
 if run and run['exit_code']==0:
  observed={r['sample']:{k:float(v) for k,v in r.items() if k!='sample'} for r in csv.DictReader((out/'observed.csv').open())};fields=('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation');energy=lambda x:sum(x[k] for k in fields);previous=observed['initial'];external=damping=contact=tendon=0.;residual=0.;journal=[];error=0.;F=np.fromstring(owner.get('externalForce'),sep=' ');c=float(owner.get('rayleighMass'))
  for i,s in enumerate(states):
   sw=sd=sc=0.
   for k in range(3):
    name,group=stages[i,k];value=observed[name];weight=h*(2/3 if k==1 else 1/6);v=np.fromstring(group[0]['stage_v'],sep=' ');sw+=weight*F.dot(v[3*nf:3*nf+3]);sd+=weight*2*c*sum(value[key] for key in ('K_film','K_linear','K_rotation'));sc+=weight*sum(float(r['force'])*float(r['normal_velocity']) for r in group)
   value=observed['end'+str(i)];external+=sw;damping+=sd;contact+=sc;tendon=sum(float(f[i]['tendon_work']) for f in films)
   if any(float(f[i]['T_per_rail'])!=0 for f in films) or tendon!=0:raise ValueError('actual T0 work/input mismatch')
   error=max(error,abs(sum(float(f[i]['U_shell']) for f in films)-value['U_skin']-value['U_rails']),abs(sum(float(f[i]['U_attachment']) for f in films)-value['U_attachment']),abs(sum(float(f[i]['K']) for f in films)-value['K_film']));residual+=energy(value)-energy(previous)-sw+sd-sc;previous=value;journal.append(dict(time=float(s['time']),**value,external_work=external,damping_work=damping,contact_work=contact,cumulative_tendon_work=tendon,signed_energy_residual=residual))
  if not all(np.isfinite(v) for row in journal for v in row.values()):raise ValueError('nonfinite measured energy')
  with (out/'inventory.csv').open('w') as stream:writer=csv.DictWriter(stream,fieldnames=journal[0].keys());writer.writeheader();writer.writerows(journal)
  result.update(status='PASS' if error<=1e-12 else 'FAIL',binary_sha256=sha(binary),ff_energy_error=error,final_inventory=journal[-1],root_work='ideal fixed-root assumption,NOT measured reaction journal',energy_gate='NOT ASSESSED;residual NOT physical heat')
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','ff_energy_error','final_inventory')}))
if __name__=='__main__':main()
