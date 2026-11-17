"""Actual event continuation stage work after200us only;missing first interval null."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text());old=ROOT/'results/autonomous_film_20261118_three_film_actual_work946';proof=json.loads((old/'summary.json').read_text());binary=old/'reference'
 if meta['status']!='PASS' or meta['macro_steps'] not in (8,15,29,50) or sha(binary)!=proof['binary_sha256']:raise ValueError('completed actual bounded continuation and immutable full-AD observer required')
 for name,digest in meta['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed:'+name)
 for name,digest in proof['sources'].items():
  if name.endswith('.h') and sha(src/'sources'/name)!=digest:raise ValueError('compiled observer header changed:'+name)
 if sha(ROOT/'diagnostics/film_three_finger/DrivenPower.cpp')!=proof['sources']['diagnostics/film_three_finger/DrivenPower.cpp']:raise ValueError('observer driver changed')
 states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));films=[list(csv.DictReader((src/('film_'+str(f)+'.csv')).open())) for f in range(3)];event=next(csv.DictReader((src/'three.event.csv').open()))
 N=meta['macro_steps'];h=meta.get('post_contact_dt',.0002)
 if len(states)!=N or len(rows)!=9*(N-1) or any(len(f)!=N for f in films):raise ValueError('incomplete continuation/stage rows')
 samples=[('initial',.0002,states[0]['q'],states[0]['v'])];stages={}
 for i,state in enumerate(states[1:]):
  samples.append(('end'+str(i),float(state['time']),state['q'],state['v']))
  for k in range(3):
   group=rows[9*i+3*k:9*i+3*k+3];r=group[0];time=.0002+(i+(0,.5,1)[k])*h
   if any(int(x['owner_finger'])!=f or abs(float(x['time'])-time)>1e-12 or x['stage_q']!=r['stage_q'] or x['stage_v']!=r['stage_v'] for f,x in enumerate(group)):raise ValueError('actual continuation ownership/stage clock mismatch')
   name='stage'+str(i)+'_'+str(k);samples.append((name,float(r['time']),r['stage_q'],r['stage_v']));stages[i,k]=(name,group)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(src/'public_mass_reference.txt',out/'mass.txt');(out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(name+' '+format(time,'.17g')+' '+q+' '+v for name,time,q,v in samples)+'\n');run=guarded([binary,out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'run',120)
 result=dict(status='FAIL',scope='actual post-event200us..accepted-end partial stage work/energy inventory,NOT first interval/full energy/time/grasp',case=a.case,source_commit=meta['source_commit'],observer_binary_sha256=sha(binary),observer_proof_sha256=sha(old/'summary.json'),raw_hashes={n:sha(src/n) for n in ('summary.json','three.states.csv','three.rows.csv','three.event.csv')},run=run,first_interval_work=None,full_physical_energy_gate='BLOCKED',missing=['pre-event/free and impact-remainder integration work','root reaction work','full-thickness/friction/self-collision','closing from rest/release/full cycle'])
 if run['exit_code']==0:
  observed={r['sample']:{k:float(v) for k,v in r.items() if k!='sample'} for r in csv.DictReader((out/'observed.csv').open())};keys=('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation');energy=lambda r:sum(r[k] for k in keys);initial=observed['initial'];tendon=external=damping=contact=energy_error=0.;records=[];regular=np.zeros(3);nf=(len(np.fromstring(states[0]['q'],sep=' '))-6)//3
  for i,state in enumerate(states[1:]):
   for k in range(3):
    name,group=stages[i,k];value=observed[name];w=h*(2/3 if k==1 else 1/6);velocity=np.fromstring(group[0]['stage_v'],sep=' ');tendon+=w*value['profile_tension']*value['unit_tendon_power'];external+=w*(-.001)*velocity[3*nf+2];damping+=w*4*sum(value[x] for x in ('K_film','K_linear','K_rotation'));contact+=w*sum(float(r['force'])*float(r['normal_velocity']) for r in group);regular-=w*sum((float(r['force'])*np.array([float(r[d]) for d in ('nx','ny','nz')]) for r in group),np.zeros(3))
   value=observed['end'+str(i)];field=[f[i+1] for f in films];energy_error=max(energy_error,abs(sum(float(r['U_shell']) for r in field)-value['U_skin']-value['U_rails']),abs(sum(float(r['U_attachment']) for r in field)-value['U_attachment']),abs(sum(float(r['K']) for r in field)-value['K_film']));residual=energy(value)-energy(initial)-tendon-external+damping-contact;record=dict(time=float(state['time']),tendon_work_Nmm=tendon,external_work_Nmm=external,damping_work_Nmm=damping,normal_contact_work_Nmm=contact,stored_kinetic_change_Nmm=energy(value)-energy(initial),signed_residual_Nmm=residual,legacy_field_work_Nmm=sum(float(f[i+1]['tendon_work'])-float(f[0]['tendon_work']) for f in films));record.update({'regular_body_impulse_'+d+'_Ns':float(regular[j]) for j,d in enumerate('xyz')});records.append(record)
  with (out/'inventory.csv').open('w') as stream:w=csv.DictWriter(stream,fieldnames=records[0]);w.writeheader();w.writerows(records)
  control_error=generator_error=0.;scene=ET.parse(src/'scene.scn');rest=np.fromstring(scene.find('.//TriangleSetTopologyContainer').get('position'),sep=' ').reshape(-1,3);reference_length=2*(rest[:,0].max()-rest[:,0].min())
  for i in range(N):
   value=observed['initial' if i==0 else 'end'+str(i-1)]
   for f in films:
    control_error=max(control_error,abs(float(f[i]['T_per_rail'])-value['profile_tension']));generator_error=max(generator_error,abs(float(f[i]['U_tendon_generator'])-value['profile_tension']*(float(f[i]['cable_length'])-reference_length)))
  result.update(status='PASS' if energy_error<=1e-12 and control_error<=1e-18 and generator_error<=1e-12 else 'FAIL',actual_field_energy_error_Nmm=energy_error,actual_endpoint_control_error_N=control_error,actual_endpoint_generator_error_Nmm=generator_error,generator_reference_subtracted_length_mm=float(reference_length),generator_note='EXISTING Kernel.h generator=T*(length-2L);NOT elastic stored energy.1005 incorrectly assumed unsubtracted origin and remains FAIL.',interval=[.0002,float(states[-1]['time'])],end=records[-1],impact_loss_before_inventory_interval_Nmm=float(event['energy_loss']),residual_interpretation='signed integrator/roundoff/unmeasured work residual;NOT physical heat or full energy qualification',whole_surface_gap_min_mm=min(float(r['minimum_gap']) for r in states),momentum_max_Ns=max(float(r['momentum_residual']) for r in states),normal_velocity_max_mm_s=max(float(r['normal_velocity_residual']) for r in states))
  os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
  fig,axes=plt.subplots(1,3,figsize=(14,4));times=[r['time'] for r in records]
  for key in ('tendon_work_Nmm','external_work_Nmm','damping_work_Nmm','stored_kinetic_change_Nmm'):axes[0].plot(times,[r[key] for r in records],label=key)
  axes[0].legend(fontsize=7);axes[1].plot(times,[r['signed_residual_Nmm'] for r in records]);axes[1].set_ylabel('signed residual [Nmm],NOT heat');q=np.array([np.fromstring(r['q'],sep=' ') for r in states]);axes[2].plot([float(r['time']) for r in states],q[:,-4]-q[0,-4]);axes[2].set_ylabel('actual free sphere z change after200us [mm]')
  for ax in axes:ax.set_xlabel('actual physical time [s]');ax.grid()
  fig.suptitle('Actual SOFA3film/free sphere continued contact;common impact200us / post dt='+str(h)+'s / NOT lift/grasp/full energy\n'+meta['source_commit'][:8]+' DLL '+meta['binary_sha256'][:12]+' gravity0,Fz=-.001N,plastic frictionless impact');fig.tight_layout();fig.savefig(out/'actual_continuation_work.png',dpi=160);plt.close(fig)
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','actual_field_energy_error_Nmm','end','whole_surface_gap_min_mm','momentum_max_Ns','normal_velocity_max_mm_s') if k in result}))
if __name__=='__main__':main()
