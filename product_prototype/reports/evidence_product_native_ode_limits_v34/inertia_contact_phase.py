"""Read-only Native anticipatory gap/dt and feature-transition diagnostics.
Frozen linearized gap crossing is NOT a continuous-time event/CCD solution.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_response_blocks import friction_blocks
from closest_geometry import closest
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];summaries=[]
 for case in ('b3_inertia_matrix_contact649','b3_inertia_matrix_contact_half650','b3_inertia_matrix_contact_quarter651'):
  src=BASE/'results'/case;meta=json.loads((src/'summary.json').read_text());d=src/'0';root=ET.parse(d/'scene.scn').getroot();states=[read(d/f'guide{i}.csv') for i in (0,1)];surface=[read(d/f'mapped{i}_eyelet.csv') for i in (0,1)];direct=[read(d/f'direct{i}.csv') for i in (0,1)];response=read(d/'response0.csv');faces=[];initial=[]
  for i in (0,1):
   child=root.find(f"./Node[@name='guide{i}']/Node[@name='collision']");faces.append(vec(child.find('MeshTopology').get('triangles')).astype(int).reshape(-1,3));initial.append(vec(child.find('MechanicalObject').get('position')).reshape(-1,3))
  own=[]
  for k,s in enumerate(states[0]):
   t=float(s['time_s']);rows=[{int(r['row_id']):r for r in data if float(r['time_s'])==t} for data in direct];q=[np.array(meta['initial'][i]['q']) if k==0 else vec(states[i][k-1]['rigid_q']) for i in (0,1)];vertices=[initial[i] if k==0 else vec(surface[i][k-1]['q']).reshape(-1,3) for i in (0,1)]
   for b in friction_blocks(response,t,rows[0]):
    J=[np.array([vec(rows[i][b+j]['J']) for j in range(3)]) for i in (0,1)];lever=[.5*sum((np.cross(x[:3],x[3:]) for x in j),np.zeros(3)) for j in J];points=[q[i][:3]+lever[i] for i in (0,1)];gap=float((points[0]-points[1])@J[0][0,:3]-.0002);free=sum(float(J[i][0]@vec(rows[i][b]['free_v'])) for i in (0,1));post=sum(float(J[i][0]@vec(states[i][k]['rigid_v'])) for i in (0,1));lam=float(rows[0][b]['lambda_Ns']);provenance=next(r for r in response if float(r['time_s'])==t and int(r['row_id'])==b);errors=[]
    for i in (0,1):
     tri=vertices[i][faces[i]];near=closest(tri,np.repeat(points[i][None,:],len(tri),axis=0));errors.append(float(np.linalg.norm(near-points[i],axis=1).min()))
    r=dict(case=case,step_start_s=t-meta['dt_s'],accepted_time_s=t,row_id_THIS_STEP_ONLY=b,models=[provenance['model0'],provenance['model1']],previous_buffered_gap_m=gap,free_normal_velocity_m_s=free,accepted_normal_velocity_m_s=post,normal_impulse_Ns=lam,actual_previous_surface_point_distance_m=errors,linearized_free_endpoint_gap_m=gap+meta['dt_s']*free,active_gap_over_dt_residual_m_s=post+gap/meta['dt_s'] if lam>0 else None,anticipatory_active_with_positive_old_gap=bool(lam>0 and gap>0),frozen_linear_gap_crossing_fraction_NOT_ACTUAL_EVENT=(-gap/(meta['dt_s']*free)) if gap>0 and free<0 and gap+meta['dt_s']*free<0 else None);records.append(r);own.append(r)
  active=[r for r in own if r['normal_impulse_Ns']>0];summaries.append(dict(case=case,dt_s=meta['dt_s'],first_active_step_start_s=active[0]['step_start_s'],first_active_accepted_time_s=active[0]['accepted_time_s'],first_active_old_gap_m=active[0]['previous_buffered_gap_m'],first_active_free_normal_velocity_m_s=active[0]['free_normal_velocity_m_s'],first_active_normal_impulse_Ns=active[0]['normal_impulse_Ns'],active_contacts=len(active),active_positive_old_gap_contacts=sum(r['anticipatory_active_with_positive_old_gap'] for r in active),detector_feature_pairs=sorted({tuple(r['models']) for r in own}),maximum_active_gap_over_dt_residual_m_s=max(abs(r['active_gap_over_dt_residual_m_s']) for r in active)))
 result=dict(status='ACTUAL_NATIVE_CONTACT_PHASE_DIAGNOSTIC_ONLY',scope='Actual Native owned response rows/free velocity/previous mapped geometry. Anticipatory unilateral gap/dt constraint,not event-localized physical impact. Frozen linear gap crossing fractions are explicitly NOT actual continuous event times. No dt/alarm/physics changes,force reconstruction or Gate exclusion.',producer_sha256=sha(Path(__file__)),source_summary_hashes={r['case']:sha(BASE/'results'/r['case']/'summary.json') for r in summaries},cases=summaries,records=records,maximum_actual_surface_point_error_m=max(max(r['actual_previous_surface_point_distance_m']) for r in records))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
