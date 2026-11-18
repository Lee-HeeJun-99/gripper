"""All three resolution pairs at exact shared FREE observation endpoint."""
import argparse,csv,itertools,json,math,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_routed_recovery_audit import checkpoint
from film_transmission_time import relative
def rows(path):return list(csv.DictReader(path.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();data=[];identity=None
 for name in a.cases:
  src=ROOT/'results'/('autonomous_film_'+name);m=json.loads((src/'summary.json').read_text());key=(m['source_checkpoint_sha256'],m['binary_sha256'],m['reference_binary_sha256'],m['source_hashes'])
  if m['status']!='PASS' or m['process']['exit_code'] or not m['accumulated_common_clock_exact'] or not m['all_contexts_exact']:raise ValueError('complete actual exact-clock/API-qualified study required')
  if identity is None:identity=key
  elif identity!=key:raise ValueError('same physical IVP/compiled model required')
  for f,d in m['raw_hashes'].items():
   if sha(src/f)!=d:raise ValueError('actual/reference raw changed')
  t,q0,v0,quat,D,maps=checkpoint(src/'input.checkpoint');accepted=rows(src/'three.states.csv');last=accepted[-1];q=np.fromstring(last['q'],sep=' ');v=np.fromstring(last['v'],sep=' ');fields=[rows(src/f'film_{f}.csv')[-1] for f in range(3)];stages=rows(src/'three.free.stages.csv');values=dict(film_displacement_change=q[:-6]-q0[:-6],film_velocity=v[:-6],object_displacement=q[-6:-3]-q0[-6:-3],object_velocity=v[-6:-3],object_angular_velocity=v[-3:],U_shell=math.fsum(float(x['U_shell']) for x in fields),U_attachment=math.fsum(float(x['U_attachment']) for x in fields),K_film=math.fsum(float(x['K']) for x in fields),K_body=.5*float(np.dot(D[-6:]*v[-6:],v[-6:])))
  ref=m['reference_metrics'];energy_parity=max(abs(values['U_shell']-float(ref['U_skin'])-float(ref['U_rails'])),abs(values['U_attachment']-float(ref['U_attachment'])),abs(values['K_film']-float(ref['K_film'])),abs(values['K_body']-float(ref['K_body'])))
  if energy_parity>1e-12 or any(float(x['T_per_rail'])!=0 for x in fields):raise ValueError('actual field physical energy/input differs from independent observer')
  values.update(U_skin=float(ref['U_skin']),U_rails=float(ref['U_rails']));We=Wd=0.
  for row in stages:
   weight=float(row['weight_s']);velocity=np.fromstring(row['v'],sep=' ');We+=weight*(-.001)*velocity[-4];Wd+=weight*2*float(np.dot(D*velocity,velocity))
  initial=ROOT/'results/autonomous_film_20261118_routed_recovery_window1393';originfields=[rows(initial/f'film_{f}.csv')[-1] for f in range(3)];E0=math.fsum(float(x[k]) for x in originfields for k in ('U_shell','U_attachment','K'))+.5*float(np.dot(D[-6:]*v0[-6:],v0[-6:]));E=values['U_shell']+values['U_attachment']+values['K_film']+values['K_body'];values.update(external_work=We,damping_work=Wd,stored_kinetic_change=E-E0,signed_inventory_defect=E-E0-We+Wd);data.append(dict(case=name,summary_sha256=sha(src/'summary.json'),steps=m['steps'],time=float(last['time']),values=values,all_actual_times=[float(x['time']) for x in accepted],actual_field_energy_parity_Nmm=energy_parity))
 if sorted(x['steps'] for x in data)!=[8,16,32] or len({x['time'] for x in data})!=1:raise ValueError('base/half/quarter and EXACT shared physical endpoint required')
 pairs=[]
 for x,y in itertools.combinations(sorted(data,key=lambda z:z['steps']),2):
  errors={k:relative(x['values'][k],y['values'][k]) for k in x['values']};pairs.append(dict(cases=[x['case'],y['case']],status='PASS' if all(z['pass_0p1'] for z in errors.values()) else 'FAIL',metrics=errors))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='PASS' if all(x['status']=='PASS' for x in pairs) else 'FAIL',scope='actual same31.6ms IVP100/50/25us ALL3pairs at exact32.4ms endpoint ONLY;NOT whole time/contact/recovery/energy qualification',time_gate_percent=.1,endpoint_s=data[0]['time'],pairs=pairs,source_summaries={x['case']:x['summary_sha256'] for x in data},common_exact_accepted_epochs=sorted(set(data[0]['all_actual_times'])&set(data[1]['all_actual_times'])&set(data[2]['all_actual_times'])),interpolation=False,root_reaction_work=None,normal_contact_force=None,impact_impulse=None,whole_time='NOT QUALIFIED',defect_note='signed numerical/measurement/root inventory defect retained,NOT heat;no small-absolute-error exemption');write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='pairs'}));print(json.dumps([dict(cases=x['cases'],status=x['status'],failed={k:z for k,z in x['metrics'].items() if not z['pass_0p1']}) for x in pairs]))
if __name__=='__main__':main()
