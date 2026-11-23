"""Direct actual Native COM Jacobian/mass audit, including failed body-input case."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha,rotation
from closest_geometry import closest
from finite_guide_coupon import eyelet

def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());original=BASE/'results/b3_finite_mapped552';cfg=json.loads((original/'config.json').read_text());faces=eyelet(cfg,32)[0].faces;records=[]
 for variant in (0,1):
  d=src/str(variant)
  for i in (0,1):
   states=read(d/f'guide{i}.csv');mapped=read(d/f'mapped{i}_eyelet.csv');direct=read(d/f'direct{i}.csv');response=read(d/'response0.csv');M=np.array(json.loads((d/f'guide{i}.csv.mass.json').read_text())['elements'][0]['matrix']);expected=np.array(meta['initial'][i]['world_inertia_kg_m2']);oldv=np.array(meta['initial'][i]['v']);oldpos=np.array(meta['initial'][i]['q'])[:3];oldverts=np.array(json.loads((original/'summary.json').read_text())['models'][i]['vertices_m'])
   for k,state in enumerate(states):
    t=float(state['time_s']);v=vec(state['rigid_v']);rows={int(r['row_id']):r for r in direct if float(r['time_s'])==t};imp=sum((vec(r['J'])*float(r['lambda_Ns']) for r in rows.values()),np.zeros(6));checks=[]
    for row in response:
     if float(row['time_s'])!=t:continue
     b=int(row['first_row']);J=np.array([vec(rows[b+j]['J']) for j in range(3)]);lever=.5*sum((np.cross(j[:3],j[3:]) for j in J),np.zeros(3));point=oldpos+lever;tri=oldverts[faces];near=closest(tri,np.repeat(point[None,:],len(tri),axis=0));checks.append(dict(first_row=b,normal_impulse_Ns=float(rows[b]['lambda_Ns']),lever_fit_error_m=float(np.max(abs(np.cross(lever,J[:,:3])-J[:,3:]))),point_previous_mesh_distance_m=float(np.linalg.norm(near-point,axis=1).min())))
    records.append(dict(variant=variant,body=i,time_s=t,public_mass_world_inertia_mismatch_kg_m2=float(np.max(abs(M[3:,3:]-expected))),mass_impulse_error_Ns_Nms=float(np.max(abs(M@(v-oldv)-imp))),row_to_journal_impulse_error_Ns_Nms=float(np.max(abs(imp-vec(state['object_impulse_Ns_Nms'])))),points=checks));oldv=v;oldpos=vec(state['rigid_q'])[:3];oldverts=vec(mapped[k]['q']).reshape(-1,3)
 result=dict(status='NATIVE_COM_JACOBIAN_DIAGNOSTIC',scope='Public initial M,actual direct J/lambda and actual previous mapped surface. Constant-world matrix convention,not orientation-updated rigid mass certification.',source_summary_sha256=sha(src/'summary.json'),source_sha256=sha(Path(__file__)),records=records,maximum_mass_impulse_error_Ns_Nms=max(r['mass_impulse_error_Ns_Nms'] for r in records),maximum_world_initial_inertia_mismatch_kg_m2=max(r['public_mass_world_inertia_mismatch_kg_m2'] for r in records),maximum_lever_fit_error_m=max((p['lever_fit_error_m'] for r in records for p in r['points']),default=None),maximum_active_surface_point_error_m=max((p['point_previous_mesh_distance_m'] for r in records for p in r['points'] if p['normal_impulse_Ns']>0),default=None))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
