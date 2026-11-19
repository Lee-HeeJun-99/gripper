"""Native three-row Coulomb reaction split;no inferred area/maximum capacity."""
import argparse,json,csv,hashlib
import numpy as np
from mechanism_candidates import BASE
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);m=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());obj=read(src/'object.csv');t=np.array([float(r['time_s']) for r in obj]);index={x:k for k,x in enumerate(t)};normal=np.zeros((len(t),6));tangent=np.zeros_like(normal);blocks={};bad=0
 if m['status']!='RUN_COMPLETED_NOT_QUALIFIED' or cfg['simulation']['friction']<=0:raise ValueError('completed native three-row friction response required')
 for r in read(src/'response_rows.csv'):
  if not(any('/object/' in r[x] for x in ('model0','model1')) and any('/skinCollision/' in r[x] for x in ('model0','model1'))):continue
  k=index[float(r['time_s'])];offset=int(r['row_id'])-int(r['first_row']);group=(k,r['constraint_path'],int(r['first_row']),offset//3);j=offset%3;v=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');(normal if j==0 else tangent)[k]+=v;blocks.setdefault(group,{})[j]=float(r['lambda_Ns'])
 defects=[]
 for key,b in blocks.items():
  if set(b)!={0,1,2}:raise ValueError('incomplete native Coulomb row group')
  defects.append(max(0.,np.hypot(b[1],b[2])-cfg['simulation']['friction']*b[0]));bad+=b[0]<0
 hold=(t>=1.6-1e-12)&(t<=2.+1e-12);dt=m['dt_s'];n=normal/dt;v=tangent/dt;w=n+v;weight=cfg['simulation']['sphere_mass_kg']*9.81
 result=dict(status='MEASURED_WRENCH_INVENTORY_ONLY',scope='actual response-owned Skin row normal/tangential J^Tlambda/dt split with native3-row Coulomb groups;NOT maximum holding capacity,6DOF closure,time convergence or grasp certification',case=a.case,hold_window_s=[1.6,2],mean_skin_normal_force_N=n[hold,:3].mean(axis=0).tolist() if hold.any() else None,mean_skin_tangential_force_N=v[hold,:3].mean(axis=0).tolist() if hold.any() else None,maximum_skin_resultant_moment_Nm=float(np.linalg.norm(w[hold,3:],axis=1).max()) if hold.any() else None,maximum_skin_vertical_gravity_balance_error_N=float(abs(w[hold,2]-weight).max()) if hold.any() else None,maximum_normal_row_moment_Nm=float(np.linalg.norm(n[:,3:],axis=1).max()),negative_normal_multiplier_count=bad,maximum_scalar_Coulomb_cone_excess_Ns=max(defects,default=None),external_wrench_resistance=None,contact_area=None,pressure=None,source_sha256=hashlib.sha256(__file__.encode()).hexdigest(),input_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (src/'response_rows.csv',src/'summary.json')})
 from pathlib import Path
 result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 with (out/'wrenches.csv').open('w') as f:
  writer=csv.writer(f);writer.writerow(['time_s','normal_Fz_N','tangent_Fz_N','total_Fz_N','Mx_Nm','My_Nm','Mz_Nm']);writer.writerows(zip(t,n[:,2],v[:,2],w[:,2],w[:,3],w[:,4],w[:,5]))
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
