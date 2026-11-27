"""Actual saved P1 tetra stress location and R0.5geometry contrast; no peak approval."""
import json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha

def main():
 out=ROOT/'validation/integrated/primaryP1_joint_hotspot1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();rows=[]
 for tag in ('primaryP1_joint5_2','primaryP1_joint35_1','primaryP1_joint25_1','primaryP1_joint15_5_1','primaryP1_joint15_35_1','primaryP1_joint15_25_1'):
  src=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(src.read_text());assert sha(REPO/s['field']['path'])==s['field']['SHA256'];a=np.load(REPO/s['field']['path']);u=a['u_mm'];ng=int(a['G_ndof']);bodies=[]
  for name,off,E,nu in [('G',0,200000,.3),('B',ng,68900,.33)]:
   p=a[name+'_points_mm'];t=a[name+'_tetra'];uu=u[off:off+3*len(p)].reshape(-1,3);dx=p[t[:,1:]]-p[t[:,0,None]];du=uu[t[:,1:]]-uu[t[:,0,None]];grad=np.linalg.solve(dx,du).transpose(0,2,1);eps=(grad+grad.transpose(0,2,1))/2;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));sigma=2*mu*eps+lam*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);dev=sigma-np.trace(sigma,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev**2,axis=(1,2)));indices=np.argsort(vm)[-10:][::-1];centers=p[t].mean(axis=1);bodies.append(dict(body=name,top10=[dict(element=int(i),centroid_mm=centers[i].tolist(),vm_MPa=float(vm[i])) for i in indices]))
  rows.append(dict(source=ref(src),candidate=s['candidate'],h_mm=s['h_mm'],bodies=bodies))
 dump(out/'summary.json',dict(status='ACTUAL_P1_STRESS_LOCALIZATION_NOT_STRENGTH_OR_CONVERGENCE',producer=ref(out/'producer.py'),rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False,interpretation='R0.5geometry does NOT demonstrate monotone lower peak: finest newGround peak0.731692MPa exceeds old0.436605MPa. Changed tetra/contact topology and singular boundaries cannot be compared as certified stress reduction. Localize and resolve finite bearing/contact/load-port behavior rather than blanket refinement or source-allowable claims.'));print(json.dumps([dict(tag=r['source']['path'],h=r['h_mm'],peaks=[b['top10'][0] for b in r['bodies']]) for r in rows]))
if __name__=='__main__':main()
