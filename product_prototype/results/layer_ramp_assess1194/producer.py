"""Independent accepted-state interlayer overlap/order and transient assessment."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def overlap(q,tet):
 witness=0
 for a,b in [(q[0],q[1]),(q[1],q[0])]:
  corners=a[tet];centres=b[tet].mean(axis=1);D=(corners[:,1:]-corners[:,0,None]).transpose(0,2,1);inv=np.linalg.inv(D);bary=np.einsum('aij,abj->abi',inv,centres[None]-corners[:,0,None]);w0=1-bary.sum(axis=-1);witness+=int(((bary>0).all(axis=-1)&(w0>0)).sum())
 return witness

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',default=['layer_free1189','layer_pressure_slip1190','layer_pressure_friction1191']);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records={};files=[Path(__file__)]
 for case in a.cases:
  src=BASE/'results'/case;pre=json.loads((src/'preflight.json').read_text());m=json.loads((src/'mesh.json').read_text());q0=np.array(m['q0']);tet=np.array(m['tetrahedra']);rows=[list(csv.DictReader((src/f'layer{i}.csv').open())) for i in (0,1)];count=min(map(len,rows));q=np.array([[np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rr[:count]] for rr in rows]);v=np.array([[np.fromstring(r['v'],sep=' ').reshape(-1,3) for r in rr[:count]] for rr in rows]);tip=q0[:,0]==.04;first=None;total=0;minimum_order=1.
  for k in range(count):
   w=overlap(q[:,k],tet);total+=w
   if w and first is None:first=float(rows[0][k]['time_s'])
   minimum_order=min(minimum_order,float((q[1,k,::2,2]-q[0,k,1::2,2]).min()))
  cr=list(csv.DictReader((src/'constraints.csv').open()));late=slice(max(0,count-50),count);tipz=.5*(q[0,:,tip,2].mean(axis=0)+q[1,:,tip,2].mean(axis=0)) if False else np.array([.5*(q[0,k,tip,2].mean()+q[1,k,tip,2].mean()) for k in range(count)]);initialmean=.000201
  slip=np.linalg.norm(q[1,:,::2,:2]-q[0,:,1::2,:2],axis=-1);maxspeed=float(np.linalg.norm(v[:,-1],axis=-1).max());d=dict(pressure_Pa=pre['pressure_Pa'],mu=pre['friction'],outputs=count,first_strict_tet_centroid_overlap_s=first,strict_overlap_witnesses=total,minimum_corresponding_interface_Z_order_m=minimum_order,maximum_relative_xy_node_shift_m=float(slip.max()),final_mean_tip_bending_m=float(tipz[-1]-initialmean),last50_mean_tip_bending_m=float((tipz[late]-initialmean).mean()),final_max_node_speed_m_s=maxspeed,maximum_solver_error=max(float(r['error']) for r in cr),iteration_limit_outputs=sum(int(r['iterations'])>=1000 for r in cr),status='FAIL_INTERLAYER_INTERSECTION' if first is not None else 'FAIL_INTERFACE_ORDER_DIAGNOSTIC' if minimum_order<0 else 'TRANSIENT_CONTACT_ONLY_NOT_STIFFNESS',static_equilibrium='NOT CERTIFIED',effective_stiffness=None,contact_force=None,energy_work=None)
  records[case]=d;files.extend([src/'preflight.json',src/'mesh.json',src/'layer0.csv',src/'layer1.csv',src/'constraints.csv'])
 result=dict(status='LAYER_COUPON_DIAGNOSTIC_ONLY',records=records,physical_validation='NOT QUALIFIED',layer_jamming='NOT VALIDATED',scope='Strict barycentric tetra-centroid overlap is a sufficient witness,not complete collision proof. Corresponding Z order is only an additional diagnostic. No contact area/pressure/force inferred from row counts.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in files});(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result))
if __name__=='__main__':main()
