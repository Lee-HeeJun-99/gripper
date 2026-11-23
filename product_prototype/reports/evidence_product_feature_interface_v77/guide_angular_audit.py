"""Global angular momentum inventory for actual free Native Rigid3 pair.
Separates impulse pullback identity from zero net INTERNAL moment;no corrections.
"""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_direct_rows513');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());records=[]
 for alarm in ('1','5'):
  d=src/alarm;states=[read(d/f'guide{i}.csv') for i in (0,1)];direct=[read(d/f'direct{i}.csv') for i in (0,1)];M=[np.array(json.loads((d/f'guide{i}.csv.mass.json').read_text())['elements'][0]['matrix']) for i in (0,1)]
  for m in M:
   if not np.array_equal(m,np.diag(np.diag(m))) or not np.all(np.diag(m)[3:]==m[3,3]):raise ValueError('isotropic mass required')
  for k,s in enumerate(states[0]):
   time=float(s['time_s']);oldq=[np.array(meta['initial_rigid_q'][i]) if k==0 else vec(states[i][k-1]['rigid_q']) for i in (0,1)];oldv=[np.array(meta['initial_rigid_v'][i]) if k==0 else vec(states[i][k-1]['rigid_v']) for i in (0,1)];newq=[vec(states[i][k]['rigid_q']) for i in (0,1)];newv=[vec(states[i][k]['rigid_v']) for i in (0,1)]
   def angular(q,v):return sum((np.cross(qi[:3],m[:3,:3]@vi[:3])+m[3:,3:]@vi[3:] for qi,vi,m in zip(q,v,M)),np.zeros(3))
   delta=angular(newq,newv)-angular(oldq,oldv);imp=[vec(states[i][k]['object_impulse_Ns_Nms']) for i in (0,1)];couple=sum((np.cross(q[:3],x[:3])+x[3:] for q,x in zip(oldq,imp)),np.zeros(3));advection=sum((np.cross(q[:3]-p[:3],m[:3,:3]@v[:3]) for q,p,v,m in zip(newq,oldq,newv,M)),np.zeros(3))
   contact_points=[];normal_moment=np.zeros(3);tangent_moment=np.zeros(3)
   for i in (0,1):
    rs=[x for x in direct[i] if float(x['time_s'])==time]
    if rs:
     j=np.array([vec(x['J']) for x in rs]);lever=.5*sum((np.cross(x[:3],x[3:]) for x in j),np.zeros(3));error=max(np.linalg.norm(np.cross(lever,x[:3])-x[3:]) for x in j)
     for offset,row in enumerate(rs):
      x=vec(row['J'])*float(row['lambda_Ns']);moment=np.cross(oldq[i][:3],x[:3])+x[3:]
      if offset==0:normal_moment+=moment
      else:tangent_moment+=moment
     contact_points.append(dict(body=i,J_rigid_lever_m=lever.tolist(),point_using_previous_body_origin_m=(oldq[i][:3]+lever).tolist(),rigid_lever_fit_residual_m=float(error)))
   points_couple=None
   if len(contact_points)==2:points_couple=np.cross(np.array(contact_points[0]['point_using_previous_body_origin_m'])-contact_points[1]['point_using_previous_body_origin_m'],imp[0][:3])
   records.append(dict(alarm_mm=int(alarm),time_s=time,global_angular_momentum_change_Nms=delta.tolist(),row_internal_moment_about_fixed_origin_Nms=couple.tolist(),normal_row_global_moment_Nms=normal_moment.tolist(),tangent_rows_global_moment_Nms=tangent_moment.tolist(),position_advection_term_Nms=advection.tolist(),inventory_closure_residual_Nms=float(np.max(abs(delta-couple-advection))),contact_point_pullback=contact_points,point_separation_couple_Nms=None if points_couple is None else points_couple.tolist(),point_couple_reconstruction_error_Nms=None if points_couple is None else float(np.max(abs(points_couple-couple)))))
 result=dict(status='ANGULAR_INVENTORY_ONLY_NOT_CONSERVATION_PASS',scope='Isotropic free pair,no external load. Exact inventory closure does NOT imply internal net moment is zero. Reconstructed row application points are not certified physical surface points. No B3 attribution or correction.',source_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),records=records,maximum_net_internal_moment_Nms=max(np.linalg.norm(x['row_internal_moment_about_fixed_origin_Nms']) for x in records),maximum_inventory_closure_residual_Nms=max(x['inventory_closure_residual_Nms'] for x in records))
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
