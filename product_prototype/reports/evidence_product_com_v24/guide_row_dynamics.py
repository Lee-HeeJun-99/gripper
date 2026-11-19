"""Audit installed Native gap/dt target using actual direct mapped rows and mass.
No force/state updates,continuous collision claims,relative-error floors or heat labels.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha,rotation

def read(p):return list(csv.DictReader(p.open()))
def v(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);p.add_argument('--references',nargs='+',required=True);a=p.parse_args()
 if len(a.cases)!=len(a.references):raise ValueError('reference count')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];steps=[];files={}
 for case,ref in zip(a.cases,a.references):
  folder=BASE/'results'/case;meta=json.loads((folder/'summary.json').read_text());dt=meta['dt_s']
  for alarm in ('1','5'):
   d=folder/alarm;state=[read(d/f'guide{i}.csv') for i in (0,1)];direct=[read(d/f'direct{i}.csv') for i in (0,1)];det=read(d/'detector.csv');response=[read(d/f'response{i}.csv') for i in (0,1)]
   M=[np.array(json.loads((d/f'guide{i}.csv.mass.json').read_text())['elements'][0]['matrix']) for i in (0,1)]
   # Matrix rotation is immaterial ONLY because these actual matrices are isotropic.
   for mat in M:
    if not np.array_equal(mat,np.diag(np.diag(mat))) or not np.all(np.diag(mat)[3:]==mat[3,3]):raise ValueError('nonisotropic rigid inertia needs frame transport')
   scene=ET.parse(d/'scene.scn').getroot();radius=float(scene.find("./Node[@name='guide0']/Node/SphereCollisionModel").get('radius'))
   locals=[]
   for i in (0,1):
    qi=np.array(meta['initial_rigid_q'][i]);point=v(scene.find(f"./Node[@name='guide{i}']/Node/MechanicalObject").get('position'));locals.append(rotation(qi[3:]).T@(point-qi[:3]))
   purity=0.;impulse_error=0.;dv_error=0.;row_velocity_error=0.;target_errors=[];first=None;positive_energy=[];detector_center_error=0.
   for i in (0,1):
    reference=read(BASE/'results'/ref/alarm/f'guide{i}.csv')
    if len(reference)!=len(state[i]):raise ValueError('incomplete reference')
    for x,y in zip(state[i],reference):
     for key in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):purity=max(purity,float(np.max(abs(v(x[key])-v(y[key])))))
   for k,st in enumerate(state[0]):
    t=float(st['time_s']);r=[[x for x in data if float(x['time_s'])==t] for data in direct]
    if not r[0]:continue
    if len(r[0])!=3 or len(r[1])!=3:raise ValueError('expected one 3-row friction block')
    J=[np.array([v(x['J']) for x in data]) for data in r];lam=np.array([float(x['lambda_Ns']) for x in r[0]])
    if [x['row_id'] for x in r[0]]!=[x['row_id'] for x in r[1]]:raise ValueError('row mismatch')
    before=[np.array(meta['initial_rigid_v'][i]) if k==0 else v(state[i][k-1]['rigid_v']) for i in (0,1)];after=[v(state[i][k]['rigid_v']) for i in (0,1)]
    w=sum(j@np.linalg.solve(m,j.T) for j,m in zip(J,M));pre=sum(j@b for j,b in zip(J,before));post=sum(j@b for j,b in zip(J,after));prediction=pre+w@lam
    row_velocity_error=max(row_velocity_error,float(np.max(abs(prediction-post))))
    for i in (0,1):
     impulse=J[i].T@lam;impulse_error=max(impulse_error,float(np.max(abs(impulse-v(state[i][k]['object_impulse_Ns_Nms'])))))
     dv_error=max(dv_error,float(np.max(abs(M[i]@(after[i]-before[i])-impulse))))
    contacts=[x for x in det if float(x['accepted_time_s'])==t]
    if len(contacts)!=1:raise ValueError('expected one actual detector contact')
    c=contacts[0]
    # These model names determine the orientation;never guess the sign from distance.
    if '/guide1/' not in c['model0'] or '/guide0/' not in c['model1']:raise ValueError('unexpected detector ordering')
    oldq=[np.array(meta['initial_rigid_q'][i]) if k==0 else v(state[i][k-1]['rigid_q']) for i in (0,1)]
    centers=[q[:3]+rotation(q[3:])@local for q,local in zip(oldq,locals)]
    detector_center_error=max(detector_center_error,float(np.max(abs(v(c['detected_point1'])-centers[0]))),float(np.max(abs(v(c['detected_point0'])-centers[1]))))
    # Actual sphere detector output here stores centres,not surface points.
    # Verify against mapped previous accepted centres above;subtract BOTH radii.
    buffered_gap=float((v(c['detected_point1'])-v(c['detected_point0']))@J[0][0,:3]-2*radius-.0002)
    target=-buffered_gap/dt;defect=float(post[0]-target)
    if lam[0]>0:target_errors.append(abs(defect))
    delta=sum(float((z-b)@m@b+.5*(z-b)@m@(z-b)) for z,b,m in zip(after,before,M))
    if delta>0:positive_energy.append(dict(time_s=t,kinetic_change_J=delta))
    entry=dict(case=case,alarm_mm=int(alarm),time_s=t,step_start_s=t-dt,normal_impulse_Ns=float(lam[0]),tangent_impulses_Ns=lam[1:].tolist(),normal=J[0][0,:3].tolist(),previous_row_velocity_m_s=pre.tolist(),accepted_row_velocity_m_s=post.tolist(),effective_inverse_mass_per_kg=w.tolist(),detector_buffered_gap_m=buffered_gap,installed_gap_over_dt_target_m_s=target,normal_target_residual_m_s=defect,kinetic_change_J=delta,normal_complementarity_product_J=float(lam[0]*defect))
    steps.append(entry)
    if first is None and lam[0]>0:first=entry
   records.append(dict(case=case,alarm_mm=int(alarm),velocity_first=meta['velocity_first'],dt_s=dt,observer_state_max_error=purity,strict_state_pass=purity<=1e-12,detector_previous_mapped_center_max_error_m=detector_center_error,direct_J_impulse_residual_Ns_Nms=impulse_error,mass_velocity_impulse_residual_Ns_Nms=dv_error,effective_mass_row_velocity_residual_m_s=row_velocity_error,active_gap_over_dt_target_max_residual_m_s=max(target_errors,default=None),first_nonzero_normal_row=first,positive_kinetic_change_steps=positive_energy))
  for f in folder.rglob('*'):
   if f.is_file():files[str(f.relative_to(BASE.parent))]=sha(f)
 sdk=Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Constraint.Lagrangian.Model/sofa/component/constraint/lagrangian/model/BaseContactLagrangianConstraint.inl');files[str(sdk)]=sha(sdk)
 result=dict(status='NATIVE_DISCRETE_ROW_DIAGNOSTIC_ONLY',scope='Direct Native J includes zero multiplier rows;isotropic PUBLIC mass inventory. Detector points are Native discrete predictor points,NOT accepted/swept geometry. Kinetic change is NOT physical heat or global energy qualification. No event-time alignment/trajectory interpolation assumed.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_sha256=sha(Path(__file__)),records=records,files=files)
 (out/'steps.json').write_text(json.dumps(steps,indent=2));(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps([dict(case=r['case'],alarm=r['alarm_mm'],purity=r['observer_state_max_error'],mass_error=r['mass_velocity_impulse_residual_Ns_Nms'],row_error=r['effective_mass_row_velocity_residual_m_s'],target_error=r['active_gap_over_dt_target_max_residual_m_s']) for r in records],indent=2))
if __name__=='__main__':main()
