"""Signed discrete metric/impulse inventory,NOT physical heat or global energy PASS."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from inertia_contact_audit import matrix
from native_response_blocks import friction_blocks
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];missing=[]
 for case in ('b3_inertia_input_contact600','b3_inertia_input_contact_half601','b3_inertia_input_contact_quarter602'):
  src=BASE/'results'/case;meta=json.loads((src/'summary.json').read_text());d=src/'0';root=ET.parse(d/'scene.scn').getroot();states=[read(d/f'guide{i}.csv') for i in (0,1)];mass=[read(d/f'mass{i}.csv') for i in (0,1)];direct=[read(d/f'direct{i}.csv') for i in (0,1)];inputs=[read(d/f'inertia_input{i}.csv') for i in (0,1)];responses=read(d/'response0.csv');oldpoints=[vec(root.find(f"./Node[@name='guide{i}']/Node[@name='massQuadrature']/MechanicalObject").get('position')).reshape(-1,3) for i in (0,1)]
  for k,state in enumerate(states[0]):
   t=float(state['time_s']);rows=[{int(r['row_id']):r for r in data if float(r['time_s'])==t} for data in direct];newpoints=[vec(mass[i][k]['q']).reshape(-1,3) for i in (0,1)]
   if not rows[0] or not rows[1]:missing.append(dict(case=case,time_s=t,reason='Actual Native free predictor not recorded without rows;NOT MEASURED,not silently reconstructed'));oldpoints=newpoints;continue
   totals=dict(actual_kinetic_change_J=0.,sampled_coordinate_input_metric_work_J=0.,contact_impulse_metric_work_J=0.,rotating_mass_metric_transport_J=0.,actual_kinetic_energy_J=0.);normalwork=0.;tangentwork=0.
   free=[];after=[]
   for i in (0,1):
    qold=np.array(meta['initial'][i]['q']) if k==0 else vec(states[i][k-1]['rigid_q']);qnew=vec(states[i][k]['rigid_q']);before=np.array(meta['initial'][i]['v']) if k==0 else vec(states[i][k-1]['rigid_v']);new=vec(states[i][k]['rigid_v']);vf=vec(next(iter(rows[i].values()))['free_v']);free.append(vf);after.append(new);M=matrix(oldpoints[i],qold[:3],meta['assumed_mass_kg']);Mn=matrix(newpoints[i],qnew[:3],meta['assumed_mass_kg']);imp=vec(states[i][k]['object_impulse_Ns_Nms']);torque=vec(inputs[i][k]['applied_torque_Nm']);input_imp=np.r_[np.zeros(3),torque*meta['dt_s']]
    totals['actual_kinetic_change_J']+=float(.5*(new@Mn@new-before@M@before));totals['sampled_coordinate_input_metric_work_J']+=float(input_imp@(.5*(vf+before)));totals['contact_impulse_metric_work_J']+=float(imp@(.5*(new+vf)));totals['rotating_mass_metric_transport_J']+=float(.5*new@(Mn-M)@new);totals['actual_kinetic_energy_J']+=float(.5*new@Mn@new)
   for b in friction_blocks(responses,t,rows[0]):
    for j in range(3):
     work=float(rows[0][b+j]['lambda_Ns'])*sum(float(vec(rows[i][b+j]['J'])@(.5*(after[i]+free[i]))) for i in (0,1))
     if j==0:normalwork+=work
     else:tangentwork+=work
   residual=totals['actual_kinetic_change_J']-sum(totals[n] for n in ('sampled_coordinate_input_metric_work_J','contact_impulse_metric_work_J','rotating_mass_metric_transport_J'));records.append(dict(case=case,time_s=t,**totals,normal_constraint_metric_work_J=normalwork,tangential_constraint_metric_work_J=tangentwork,signed_inventory_residual_J=residual,row_work_reconstruction_residual_J=normalwork+tangentwork-totals['contact_impulse_metric_work_J']));oldpoints=newpoints
 result=dict(status='SIGNED_DISCRETE_INVENTORY_ONLY',scope='Actual Native free predictor and mapped mass. Coordinate-input and mass-transport terms are NOT external actuator work or heat. Constraint work includes Native discrete stabilization,NOT certified impact dissipation. No global energy/continuous-time/mesh/Holding PASS.',producer_sha256=sha(Path(__file__)),records=records,missing_intervals=missing,root_reaction_work=None,physical_impact_heat=None,maximum_signed_inventory_residual_J=max(abs(r['signed_inventory_residual_J']) for r in records),maximum_row_work_reconstruction_residual_J=max(abs(r['row_work_reconstruction_residual_J']) for r in records),maximum_positive_normal_constraint_work_J=max(0.,max(r['normal_constraint_metric_work_J'] for r in records)))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k not in ('records','missing_intervals')},indent=2))
if __name__=='__main__':main()
