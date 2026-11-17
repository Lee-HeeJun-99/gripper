"""Read-only full-AD work inventory of actual resumed stages;explicit ledger origin.
Reuse qualified material observer. Missing root work remains NULL,not heat.
"""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 observer=ROOT/'results/autonomous_film_20261118_three_film_actual_work946';proof=json.loads((observer/'summary.json').read_text());binary=observer/'reference'
 if sha(binary)!=proof['binary_sha256']:raise ValueError('qualified read-only observer changed')
 # Every header used by observer is checked against its archived compiled bytes.
 for n,h in proof['sources'].items():
  if n.endswith('.h') and sha(ROOT/n)!=h:raise ValueError('observer material header changed:'+n)
 samples=[];macros=[];origin=None;previous=None;provenance=[];fields=[]
 for case in a.cases:
  src=ROOT/'results'/('autonomous_film_'+case);meta=json.loads((src/'summary.json').read_text())
  if meta['status'] not in ('PASS','EXPERIMENTAL') or meta['process']['exit_code'] or meta['sofa_errors']:raise ValueError('completed actual continuation required')
  for n,h in meta['raw_hashes'].items():
   if sha(src/n)!=h:raise ValueError('actual raw changed')
  tokens=(src/'input.checkpoint').read_text().split();time=float(tokens[1]);q=np.array(list(map(float,tokens[5:1958])));v=np.array(list(map(float,tokens[1958:3911])))
  if previous is not None and (time!=previous[0] or not np.array_equal(q,previous[1]) or not np.array_equal(v,previous[2])):raise ValueError('nonidentical chunk boundary:refuse stitching')
  if origin is None:origin=time;samples.append(('initial',time,' '.join(tokens[5:1958]),' '.join(tokens[1958:3911])))
  states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));film=[list(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)]
  if len(rows)!=len(states)*9 or any(len(f)!=len(states) for f in film):raise ValueError('incomplete stage/field journal')
  for i,state in enumerate(states):
   number=len(macros);groups=[];h=float(tokens[2])
   for k in range(3):
    group=rows[9*i+3*k:9*i+3*k+3];r=group[0];name=f'stage{number}_{k}';samples.append((name,float(r['time']),r['stage_q'],r['stage_v']));groups.append(group)
   name='end'+str(number);samples.append((name,float(state['time']),state['q'],state['v']));macros.append((state,groups,h));fields.append([f[i] for f in film])
  previous=float(states[-1]['time']),np.fromstring(states[-1]['q'],sep=' '),np.fromstring(states[-1]['v'],sep=' ');provenance.append(dict(case=case,summary_sha256=sha(src/'summary.json'),checkpoint_sha256=sha(src/'input.checkpoint')))
 (out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(name+' '+format(t,'.17g')+' '+q+' '+v for name,t,q,v in samples)+'\n');shutil.copy2(ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002/public_mass_reference.txt',out/'mass.txt');run=guarded([binary,out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'run',120)
 result=dict(status='FAIL',scope='actual saved resumed-stage partial energy/work inventory;NOT full energy/time/grasp certification',observer_binary_sha256=sha(binary),provenance=provenance,run=run,work_origin_s=origin,root_reaction_work=None,legacy_sampled_work='NOT continuous;private state intentionally not reconstructed',prior_interval_evidence=['Campaign1011:first200us','Campaign1007:200us..10ms,overlap must not be double counted'])
 if run['exit_code']==0:
  observed={r['sample']:{k:float(v) for k,v in r.items() if k!='sample'} for r in csv.DictReader((out/'observed.csv').open())};keys=('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation');energy=lambda x:sum(x[k] for k in keys);initial=observed['initial'];tendon=external=damping=normal=field_error=control_error=0.;records=[]
  for i,(state,groups,h) in enumerate(macros):
   for k,group in enumerate(groups):
    value=observed[f'stage{i}_{k}'];w=h*(2/3 if k==1 else 1/6);v=np.fromstring(group[0]['stage_v'],sep=' ');tendon+=w*value['profile_tension']*value['unit_tendon_power'];external+=w*(-.001)*v[-4];damping+=w*4*sum(value[k] for k in ('K_film','K_linear','K_rotation'));normal+=w*sum(float(r['force'])*float(r['normal_velocity']) for r in group)
   value=observed['end'+str(i)];field=fields[i];field_error=max(field_error,abs(sum(float(f['U_shell']) for f in field)-value['U_skin']-value['U_rails']),abs(sum(float(f['U_attachment']) for f in field)-value['U_attachment']),abs(sum(float(f['K']) for f in field)-value['K_film']));control_error=max(control_error,max(abs(float(f['T_per_rail'])-value['profile_tension']) for f in field));records.append(dict(time=float(state['time']),tendon_work_Nmm=tendon,external_work_Nmm=external,damping_work_Nmm=damping,normal_constraint_work_Nmm=normal,stored_kinetic_change_Nmm=energy(value)-energy(initial),signed_residual_Nmm=energy(value)-energy(initial)-tendon-external+damping-normal))
  with (out/'inventory.csv').open('w') as stream:w=csv.DictWriter(stream,fieldnames=records[0]);w.writeheader();w.writerows(records)
  result.update(status='PASS' if field_error<1e-12 and control_error==0 else 'FAIL',field_energy_max_abs_Nmm=field_error,control_max_abs_N=control_error,interval_s=[origin,records[-1]['time']],end=records[-1],interpretation='signed integration/roundoff/unmeasured-work residual,NOT physical heat;no impact in this resumed persistent interval',observed_sha256=sha(out/'observed.csv'),inventory_sha256=sha(out/'inventory.csv'))
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','interval_s','end','field_energy_max_abs_Nmm','control_max_abs_N') if k in result}))
if __name__=='__main__':main()
