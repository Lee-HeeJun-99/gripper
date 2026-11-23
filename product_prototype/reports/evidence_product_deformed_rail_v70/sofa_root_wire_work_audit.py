"""Accepted journals only:detector chronology and discrete identities,NOT energy certification."""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def v(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];inputs={}
 for case in a.cases:
  folder=BASE/'results'/case;meta=json.loads((folder/'summary.json').read_text());rows=list(csv.DictReader((folder/'wire.csv').open()));m=meta['mass_kg'];dt=meta['dt_s'];f=np.array(meta['external_force_N']);q=np.array([v(r['rigid_q'])[:3] for r in rows]);vel=np.array([v(r['rigid_v'])[:3] for r in rows]);imp=np.array([v(r['object_impulse_Ns_Nms'])[:3] for r in rows]);oldq=np.vstack([meta['initial_q_m'],q[:-1]]);oldv=np.vstack([meta['initial_v_m_s'],vel[:-1]]);dv=vel-oldv;avg=(vel+oldv)/2;dk=m*np.einsum('ij,ij->i',dv,avg)
  midpoint_external=dt*avg@f;midpoint_contact=np.einsum('ij,ij->i',imp,avg);external_geometric=(q-oldq)@f;endpoint_contact=np.einsum('ij,ij->i',imp,vel);be_defect=-.5*m*np.einsum('ij,ij->i',dv,dv)
  bytime={float(r['time_s']):i for i,r in enumerate(rows)};previous_errors=[];accepted_errors=[];count=0
  for r in csv.DictReader((folder/'detector.csv').open()):
   if '/wire_section/' not in r['model0']+r['model1']:continue
   i=bytime[float(r['accepted_time_s'])];point=v(r['detected_point0'] if '/wire_section/' in r['model0'] else r['detected_point1']);previous_errors.append(float(np.linalg.norm(point-oldq[i])));accepted_errors.append(float(np.linalg.norm(point-q[i])));count+=1
  fields=['time_s','stable_delta_kinetic_J','external_geometric_work_J','external_midpoint_impulse_work_J','contact_midpoint_impulse_work_J','contact_endpoint_impulse_work_J','backward_euler_inertial_defect_J']
  with (out/(case+'_discrete_work.csv')).open('w',newline='') as handle:
   w=csv.writer(handle);w.writerow(fields)
   for i,row in enumerate(rows):w.writerow([row['time_s'],dk[i],external_geometric[i],midpoint_external[i],midpoint_contact[i],endpoint_contact[i],be_defect[i]])
  rec=dict(case=case,detector_wire_points=count,maximum_detector_center_vs_previous_accepted_m=max(previous_errors),maximum_detector_center_vs_current_accepted_m=max(accepted_errors),maximum_BE_position_update_residual_m=float(abs(q-oldq-dt*vel).max()),maximum_midpoint_impulse_identity_residual_J=float(abs(dk-midpoint_external-midpoint_contact).max()),maximum_BE_work_identity_residual_J=float(abs(dk-external_geometric-endpoint_contact-be_defect).max()),sum_stable_delta_kinetic_J=float(dk.sum()),sum_external_geometric_work_J=float(external_geometric.sum()),sum_contact_midpoint_impulse_work_J=float(midpoint_contact.sum()),sum_contact_endpoint_impulse_work_J=float(endpoint_contact.sum()),sum_BE_inertial_defect_J=float(be_defect.sum()),physical_impact_loss_J=None,root_reaction_work_J=None,wire_elastic_energy_J=None,physical_energy_certified=False)
  rec['status']='PASS_DISCRETE_CHRONOLOGY_IDENTITY_ONLY' if count and rec['maximum_detector_center_vs_previous_accepted_m']<1e-12 and rec['maximum_midpoint_impulse_identity_residual_J']<1e-22 and rec['maximum_BE_work_identity_residual_J']<1e-22 else 'FAIL_DISCRETE_CONTRACT'
  active=np.where(np.linalg.norm(imp,axis=1)>0)[0]
  if len(active):
   first=int(active[0]);normal=imp[first]/np.linalg.norm(imp[first]);plane_gap_previous=float(-normal@(q[first]-oldq[first]));rec['first_contact_diagnostic']=dict(accepted_time_s=float(rows[first]['time_s']),normal_from_actual_impulse=normal.tolist(),previous_normal_velocity_m_s=float(normal@oldv[first]),free_normal_velocity_m_s=float(normal@(oldv[first]+f*dt/m)),accepted_normal_velocity_m_s=float(normal@vel[first]),next_accepted_normal_velocity_m_s=float(normal@vel[first+1]) if first+1<len(rows) else None,previous_gap_to_accepted_contact_plane_m=plane_gap_previous,position_level_normal_velocity_reference_m_s=-plane_gap_previous/dt,scope='Gap referenced to plane through accepted contact,not an independently solved continuous event. Normal derived from measured aggregate impulse;mu0 singleactivepair. Nonzero inward accepted velocity is NOT e=0 velocity-lawPASS.')
  records.append(rec)
  for file in ('summary.json','scene.scn','wire.csv','detector.csv'):inputs[str((folder/file).relative_to(BASE))]=sha(folder/file)
 result=dict(status='DISCRETE_IMPULSE_WORK_AUDIT_NOT_PHYSICAL_ENERGY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=inputs,source_sha256=sha(Path(__file__)),records=records,scope='Detector observation label is AnimateEnd time,coordinates compared to actual previous/current states. Midpoint impulse work is an algebraic momentum identity,NOT stage quadrature or physical heat. BE inertial defect includes abrupt contact andsmooth acceleration,NOT separately measured plastic/damping loss. External F dot actual dq measured;root/work/fullwire energyNULL. No time/mesh/physicalenergy/holdingPASS.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
