"""All-common-output/all-pair finite guide contact-mesh comparison;no floors."""
import argparse,csv,itertools,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);metadata=[json.loads((BASE/'results'/c/'summary.json').read_text()) for c in a.cases]
 for m in metadata[1:]:
  for key in ('source_config_sha256','dt_s','initial_rigid_q','initial_rigid_v','intersection'):
   if m[key]!=metadata[0][key]:raise ValueError('not a same-input mesh comparison:'+key)
 records=[]
 for alarm in ('1','5'):
  for body in (0,1):
   rows=[list(csv.DictReader((BASE/'results'/case/alarm/f'guide{body}.csv').open())) for case in a.cases]
   for i,j in itertools.combinations(range(3),2):
    if len(rows[i])!=len(rows[j]):raise ValueError('incomplete output')
    for u,v in zip(rows[i],rows[j]):
     if abs(float(u['time_s'])-float(v['time_s']))>1e-12:raise ValueError('clock mismatch')
     for key,cols,label in [('rigid_q',slice(0,3),'translation_from_initial_m'),('rigid_v',slice(0,3),'linear_velocity_m_s'),('rigid_v',slice(3,6),'angular_velocity_rad_s'),('object_impulse_Ns_Nms',slice(0,3),'linear_impulse_Ns'),('object_impulse_Ns_Nms',slice(3,6),'angular_impulse_Nms')]:
      x=np.fromstring(u[key],sep=' ')[cols];y=np.fromstring(v[key],sep=' ')[cols]
      if key=='rigid_q':x=x-np.array(metadata[i]['initial_rigid_q'][body][:3]);y=y-np.array(metadata[j]['initial_rigid_q'][body][:3])
      absolute=float(np.linalg.norm(x-y));den=max(float(np.linalg.norm(x)),float(np.linalg.norm(y)));relative=absolute/den if den else 0.
      records.append(dict(alarm_mm=int(alarm),body=body,cases=[a.cases[i],a.cases[j]],time_s=float(u['time_s']),quantity=label,absolute_error=absolute,relative_error=relative,status='PASS_SELECTED_OUTPUT' if relative<=.01 else 'FAIL'))
 result=dict(status='FAIL_GUIDE_CONTACT_MESH_GATE' if any(r['status']=='FAIL' for r in records) else 'PASS_SELECTED_GUIDE_CONTACT_MESH_ONLY',scope='Finite-eyelet contact tessellation16/32/64 with same inherited body mass,inertia and physical dimensions. Not B3 FEM mesh convergence or CAD solid readiness. No interpolation/error floor.',gate=.01,source_sha256=sha(Path(__file__)),source_summaries={c:sha(BASE/'results'/c/'summary.json') for c in a.cases},worst_by_alarm={alarm:max((r for r in records if r['alarm_mm']==int(alarm)),key=lambda r:r['relative_error']) for alarm in ('1','5')},records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
