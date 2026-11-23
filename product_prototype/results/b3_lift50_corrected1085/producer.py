"""Predeclared actual Root/cable-origin/free-object lift evaluation."""
import argparse,csv,json,os
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
def read(path):return list(csv.DictReader(path.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--partition',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 meta=json.loads((src/'summary.json').read_text());protocol=json.loads((src/'lift_protocol.json').read_text());part=BASE/'results'/a.partition
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED' or sha(src/'lift_protocol.json')!=meta['lift_protocol_sha256']:raise ValueError('complete run and unchanged preregistration required')
 objects=read(src/'object.csv');t=np.array([float(r['time_s']) for r in objects]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in objects]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in objects]);ref=int(np.argmin(abs(t-protocol['reference_s'])));end=(t>=1.95-1e-12)&(t<=2+1e-12);active=t>=1.6-1e-12
 expected=.005*np.clip((t-1.6)/.3,0,1);root_mean=[];root_error=0;origin_error=0;pre_error=0;tree=ET.parse(src/'scene.scn');local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);cfg=json.loads((src/'config.json').read_text());ids=np.flatnonzero(local[:,0]<=cfg['finger']['clamp_length']);baseline=BASE/'results/b3_alarm_window485'
 for f in range(3):
  rows=read(src/f'finger{f}.csv');before=read(baseline/f'finger{f}.csv');state=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);rest=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);delta=state[:,ids]-rest[ids];wanted=np.zeros_like(delta);wanted[:,:,2]=expected[:,None];root_error=max(root_error,float(abs(delta-wanted).max()));root_mean.append(delta[:,:,2].mean(axis=1))
  for k in np.flatnonzero(t<1.6-1e-12):
   for field in ('q_m','v_m_s','guide0_q_m','guide1_q_m'):pre_error=max(pre_error,float(abs(np.fromstring(rows[k][field],sep=' ')-np.fromstring(before[k][field],sep=' ')).max()))
  for c in range(2):
   rs=read(src/f'origin_f{f}_c{c}.csv')
   if len(rs)!=len(t) or any(float(r['accepted_time_s'])!=t[k] for k,r in enumerate(rs)):raise ValueError('origin clock/count mismatch')
   d=np.array([np.fromstring(r['actual_pullPoint_m'],sep=' ')-np.fromstring(r['initial_pullPoint_m'],sep=' ') for r in rs]);want=np.zeros_like(d);want[:,2]=expected;origin_error=max(origin_error,float(abs(d-want).max()))
 root=np.array(root_mean).mean(axis=0);rise=(q[:,2]-q[ref,2])*1000;rootrise=(root-root[ref])*1000;slip=rootrise-rise
 sr=read(src/'support.csv');support=np.array([np.fromstring(r['q'],sep=' ') for r in sr]);sphere_radius=float(tree.find("./Node[@name='object']/Node/SphereCollisionModel").get('radius'));support_radius=float(tree.find("./Node[@name='floor']/SphereCollisionModel").get('radius'));gap=(np.linalg.norm(q[:,:3]-support,axis=1)-sphere_radius-support_radius)*1000
 forces=read(part/'response_forces.csv');ft=np.array([float(r['time_s']) for r in forces]);
 if not np.array_equal(t,ft):raise ValueError('response-force clock mismatch')
 skin=np.array([float(r['skin_vertical_N']) for r in forces]);guide=np.array([float(r['guide_vertical_N']) for r in forces]);rail=np.array([float(r['rail_vertical_N']) for r in forces]);supp=np.array([float(r['support_vertical_N']) for r in forces]);weight=.05*9.81
 support_vector=np.zeros((len(t),3));index={x:k for k,x in enumerate(t)}
 for row in read(src/'response_rows.csv'):
  pair=[row['model0'],row['model1']]
  if any('/object/' in x for x in pair) and any('/floor/' in x for x in pair):support_vector[index[float(row['time_s'])]]+=np.fromstring(row['object_impulse_Ns_Nms'],sep=' ')[:3]/meta['dt_s']
 support_resultant=np.linalg.norm(support_vector,axis=1);partition=json.loads((part/'summary.json').read_text())
 tests=dict(root_motion=root_error<=1e-12,origin_motion=origin_error<=1e-12,object_rise=float(rise[end].min())>=protocol['minimum_object_rise_mm'],relative_slip=float(slip[active].max())<=2,end_speed=float(np.linalg.norm(v[end,:3],axis=1).max()*1000)<=5,support_gap=float(gap[active].min())>=5,support_force=float(support_resultant[active].max())<=1e-5,skin_load=float((skin[end]/weight).min())>=.8,hardware_vertical_force=float(np.maximum(abs(guide[active]),abs(rail[active])).max())<=1e-5,response_partition=partition['status']=='PASS_RESPONSE_PARTITION_ONLY')
 d=dict(status='PASS_EXPLORATORY_LIFT_ONLY' if all(tests.values()) else 'FAIL_EXPLORATORY_LIFT',tests=tests,minimum_end_object_rise_mm=float(rise[end].min()),maximum_relative_vertical_slip_mm=float(slip[active].max()),maximum_end_speed_mm_s=float(np.linalg.norm(v[end,:3],axis=1).max()*1000),minimum_support_gap_mm=float(gap[active].min()),maximum_support_vertical_force_N=float(abs(supp[active]).max()),end_mean_skin_vertical_N=float(skin[end].mean()),maximum_root_position_error_m=root_error,maximum_origin_position_error_m=origin_error,pre_lift_finger_state_vs_frozen485_error=pre_error,object_gravitational_potential_change_J=float(weight*(q[-1,2]-q[ref,2])),cable_work=None,root_fixture_work=None,energy_balance='NOT MEASURED',numerical_convergence='EXISTING_FAIL_NOT_RETESTED',physical_validation='NOT QUALIFIED',scope='Actual free-object lift with independently measured Root/origins and direct response force partition;NOT motor/CAD hardware/100g/time/mesh/energy qualification. Support criterion here is VERTICAL load;full resultant retained in response inventory.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in [src/'summary.json',src/'lift_protocol.json',src/'object.csv',part/'summary.json',part/'response_forces.csv',Path(__file__)]})
 d['maximum_support_resultant_N']=float(support_resultant[active].max());d['scope']='Actual free-object lift with independently measured Root/origins and direct response partition;full support resultant required. NOT motor/CAD hardware/100g/time/mesh/energy qualification.'
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2))
 os.environ.setdefault('MPLCONFIGDIR',str(out/'mplconfig'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(3,1,sharex=True,figsize=(8,8));ax[0].plot(t,rise,label='Actual free object');ax[0].plot(t,rootrise,label='Actual Root');ax[0].set_ylabel('rise mm from1.6s');ax[0].legend();ax[1].plot(t,slip);ax[1].set_ylabel('Root-object slip mm');ax[2].plot(t,skin,label='Skin Z');ax[2].plot(t,supp,label='Support Z');ax[2].axhline(weight,color='k',ls='--',label='gravity load');ax[2].set(ylabel='N',xlabel='Accepted time s');ax[2].legend();fig.suptitle(a.case+' Actual Native SOFA 50g R30 dt2.5ms\n'+d['status']+'; time/mesh/energy NOT QUALIFIED');fig.tight_layout();fig.savefig(out/'actual_lift.png');plt.close(fig);print(json.dumps(d))
if __name__=='__main__':main()
