"""Actual resumed stage work with an EXPLICIT measured preceding inventory."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--qualification',required=True);p.add_argument('--prior-work',required=True);p.add_argument('--prior-case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text());qual=ROOT/'results'/('autonomous_film_'+a.qualification);qm=json.loads((qual/'summary.json').read_text());prior=ROOT/'results'/('autonomous_film_'+a.prior_work);pm=json.loads((prior/'summary.json').read_text());previous=ROOT/'results'/('autonomous_film_'+a.prior_case);ps=json.loads((previous/'summary.json').read_text());provider=ROOT/'results/autonomous_film_20261118_routed_coupled_work1274';proof=json.loads((provider/'summary.json').read_text())
 if m['status']!='EXPERIMENTAL' or qm['status']!='PASS' or qm['actual_summary_sha256']!=sha(src/'summary.json') or pm['status']!='PASS' or pm['actual_summary_sha256']!=sha(previous/'summary.json') or ps['status'] not in ('PASS','EXPERIMENTAL') or proof['status']!='PASS':raise ValueError('complete actual/API/preceding physical inventory chain required')
 if ps['status']=='EXPERIMENTAL' and not pm.get('qualification_summary_sha256'):raise ValueError('preceding experimental actual requires qualified measured inventory')
 if sha(src/'input.checkpoint')!=m['input_checkpoint_sha256']:raise ValueError('actual input checkpoint changed')
 for path,meta in ((src,m),(prior,pm),(previous,ps)):
  for file,d in meta['raw_hashes'].items():
   if sha(path/file)!=d:raise ValueError('physical history changed')
 for file,d in proof['source_hashes'].items():
  if sha(provider/'sources'/file)!=d:raise ValueError('observer physical source changed')
 if sha(provider/'observer')!=proof['observer_binary_sha256']:raise ValueError('new-route observer changed')
 states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));N=len(states);nf=(len(np.fromstring(states[0]['q'],sep=' '))-6)//3;initial=rows[0];end=list(csv.DictReader((previous/'three.states.csv').open()))[-1]
 if len(rows)!=9*N or initial['time']!=end['time'] or any(not np.array_equal(np.fromstring(initial['stage_'+key],sep=' '),np.fromstring(end[key],sep=' ')) for key in ('q','v')) or float(end['time'])!=pm['final_inventory']['time_s']:raise ValueError('EXACT physical state/time bridge to measured preceding work absent')
 samples=[('initial',float(initial['time']),initial['stage_q'],initial['stage_v'])];transactions=[];h=m['dt_s'];time=float(initial['time'])
 for i,s in enumerate(states):
  if float(s['time'])!=time+h:raise ValueError('recorded used dt/accumulated time differs')
  transaction=[];samples.append(('end'+str(i),float(s['time']),s['q'],s['v']))
  for k in range(3):
   group=rows[9*i+3*k:9*i+3*k+3];first=group[0];t=time+h*(0,.5,1)[k]
   if any(int(r['owner_finger'])!=f or float(r['time'])!=t or r['stage_q']!=first['stage_q'] or r['stage_v']!=first['stage_v'] for f,r in enumerate(group)):raise ValueError('owned actual stages differ')
   name=f'stage{i}_{k}';samples.append((name,t,first['stage_q'],first['stage_v']));transaction.append((name,h*(2/3 if k==1 else 1/6),sum(float(r['force'])*float(r['normal_velocity']) for r in group)))
  transactions.append(transaction);time=float(s['time'])
 tokens=(src/'input.checkpoint').read_text().split();n=3*nf+6;offset=5+2*n+4;masses=tokens[offset:offset+693];Mb=np.array(tokens[offset+693:offset+729],float).reshape(6,6)
 if tokens[0]!='REGRIP_ROUTED_PERSISTENT_V1' or not np.array_equal(Mb,np.diag(np.diag(Mb))) or len(set(Mb.diagonal()[:3]))!=1 or len(set(Mb.diagonal()[3:]))!=1:raise ValueError('qualified sphere checkpoint mass/inertia required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(provider/'observer',out/'observer');(out/'mass.txt').write_text('231\n'+'\n'.join(' '.join(masses[231*f:231*(f+1)]) for f in range(3))+'\n'+format(Mb[0,0],'.17g')+' '+format(Mb[3,3],'.17g')+'\n');(out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(name+' '+format(t,'.17g')+' '+q+' '+v for name,t,q,v in samples)+'\n');forecast=2*proof['process']['runtime_s']*len(samples)/proof['samples']+30
 if forecast>480:raise ValueError('observer forecast exceeds480s policy')
 run=guarded([out/'observer',out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'process',480);r=dict(status='FAIL',scope='actual resumed new-route measured stage work with EXACT physical prefix;NOT whole energy/time/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),qualification_summary_sha256=sha(qual/'summary.json'),prior_work_summary_sha256=sha(prior/'summary.json'),prior_actual_summary_sha256=sha(previous/'summary.json'),observer_provider_summary_sha256=sha(provider/'summary.json'),observer_binary_sha256=sha(out/'observer'),process=run,predicted_child_runtime_s=forecast,root_reaction_work=None,legacy_sampled_work='NOT used;all first restart samples excluded',full_energy_gate='BLOCKED',residual_is_heat=False)
 if run['exit_code']==0:
  observed={r['sample']:{k:float(v) for k,v in r.items() if k!='sample'} for r in csv.DictReader((out/'observed.csv').open())};E=lambda r:sum(r[k] for k in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation'));K=lambda r:sum(r[k] for k in ('K_film','K_linear','K_rotation'));scene=ET.parse(src/'scene.scn');owner=scene.find('RoutedThreeFilmResumeODE');F=np.fromstring(owner.get('externalForce'),sep=' ');c=float(owner.get('rayleighMass'));fields=[list(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)];sample={name:(t,np.fromstring(v,sep=' ')) for name,t,q,v in samples};p0=pm['final_inventory'];prefixE0=E(p0)-p0['energy_change_Nmm'];bridge=abs(E(observed['initial'])-E(p0));W=We=D=C=error=control=length=0.;journal=[]
  for i,transaction in enumerate(transactions):
   for name,w,normal_power in transaction:
    value=observed[name];t,v=sample[name];W+=w*value['profile_tension']*value['unit_tendon_power'];We+=w*F.dot(v[3*nf:3*nf+3]);D+=w*2*c*K(value);C+=w*normal_power
   end=observed['end'+str(i)];error=max(error,abs(sum(float(f[i]['U_shell']) for f in fields)-end['U_skin']-end['U_rails']),abs(sum(float(f[i]['U_attachment']) for f in fields)-end['U_attachment']),abs(sum(float(f[i]['K']) for f in fields)-end['K_film']));control=max(control,max(abs(float(f[i]['T_per_rail'])-end['profile_tension']) for f in fields));length=max(length,abs(sum(float(f[i]['cable_length']) for f in fields)-end['cable_length']));totalW=p0['tendon_work_Nmm']+W;totalWe=p0['external_work_Nmm']+We;totalD=p0['damping_work_Nmm']+D;totalC=p0['normal_constraint_work_Nmm']+C;loss=p0['plastic_impact_loss_Nmm'];journal.append(dict(time_s=float(states[i]['time']),**end,tendon_work_Nmm=totalW,external_work_Nmm=totalWe,damping_work_Nmm=totalD,normal_constraint_work_Nmm=totalC,plastic_impact_loss_Nmm=loss,energy_change_Nmm=E(end)-prefixE0,signed_energy_defect_Nmm=E(end)-prefixE0-totalW-totalWe+totalD-totalC+loss,segment_tendon_work_Nmm=W,segment_external_work_Nmm=We,segment_damping_work_Nmm=D,segment_normal_work_Nmm=C))
  with (out/'inventory.csv').open('w') as file:w=csv.DictWriter(file,fieldnames=list(journal[0]));w.writeheader();w.writerows(journal)
  r.update(status='PASS' if bridge<1e-12 and error<1e-12 and control<=1e-18 and length<=1e-12 else 'FAIL',physical_prefix_energy_bridge_error_Nmm=bridge,actual_field_energy_error_Nmm=error,actual_endpoint_control_error_N=control,cable_length_error_mm=length,final_inventory=journal[-1],raw_hashes={f:sha(out/f) for f in ('observed.csv','inventory.csv','mass.txt','samples.txt')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='process'}))
if __name__=='__main__':main()
