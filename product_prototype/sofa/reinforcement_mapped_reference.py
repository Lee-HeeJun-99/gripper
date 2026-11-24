"""Independent infinitesimal rigid-guide pullback of actual linear coupon K.

Read-only reference,NOT a Native solver or nonlinear mapped tangent claim.
"""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.linalg import cho_factor,cho_solve
from analyse import BASE,sha
def cross(r):
 x,y,z=r;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';root=ET.parse(src/'scene.scn').getroot();finger=root.find("Node[@name='finger0']");guides=root.find("Node[@name='guides0']");free=root.find("Node[@name='free0']");q=np.fromstring(finger.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);frames=np.fromstring(guides.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);anchors=guides.find("Node[@name='anchors']");owner=np.fromstring(anchors.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);pairs=np.fromstring(finger.find('SubsetMultiMapping').get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);nf=len(np.fromstring(free.find('MechanicalObject').get('position'),sep=' '))//3;ng=len(frames);T=np.zeros((3*len(q),3*nf+6*ng))
 for k,(body,index) in enumerate(pairs):
  if body==0:T[3*k:3*k+3,3*index:3*index+3]=np.eye(3)
  else:
   j=owner[index];T[3*k:3*k+3,3*nf+6*j:3*nf+6*j+3]=np.eye(3);T[3*k:3*k+3,3*nf+6*j+3:3*nf+6*j+6]=-cross(q[k]-frames[j,:3])
 fixed=np.fromstring(free.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int);records=[]
 for name in ('baseline','reinforced'):
  file=BASE/'results/reinforcement_bending1380'/name/'reference.npz';x=np.load(file);K=x['K'];F=x['F'].ravel();n=len(x['q']);extra=n-len(q);J=np.zeros((3*n,T.shape[1]+3*extra));J[:len(T),:T.shape[1]]=T
  if extra:J[len(T):,T.shape[1]:]=np.eye(3*extra)
  constrained=(3*fixed[:,None]+np.arange(3)).ravel().tolist()
  if extra:
   g=json.loads((BASE/'results/proximal_reinforcement_geometry1364/mesh.json').read_text());constrained+=list((T.shape[1]+3*np.array(g['root_free_fixed_indices'])[:,None]+np.arange(3)).ravel())
  freeids=np.setdiff1d(np.arange(J.shape[1]),constrained);kf=(J.T@K@J)[np.ix_(freeids,freeids)];load=(J.T@F)[freeids];z=np.zeros(J.shape[1]);z[freeids]=cho_solve(cho_factor(kf),load);u=J@z;energy=float(.5*u@K@u);work=float(.5*F@u);res=float(abs(kf@z[freeids]-load).max());local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);tip=(local[:,0]==100)&(local[:,2]==.1);full=u.reshape(-1,3);test=np.sin(np.arange(J.shape[1])*.37)*1e-6;virtual_error=abs(float((J@test)@F-test@(J.T@F)));records.append(dict(name=name,full_dofs=len(u),reduced_dofs=len(z),root_fixed_dofs=len(constrained),guide_count=ng,static_tip_x_m=float(full[:len(q)][tip,0].mean()),energy_J=energy,half_work_J=work,energy_work_absolute_error_J=abs(energy-work),free_equilibrium_residual_N_Nm=res,virtual_work_pullback_error_J=virtual_error,displacement=full.tolist(),input_sha256=sha(file)))
 d=dict(status='INDEPENDENT_LINEAR_RIGID_GUIDE_REFERENCE_ONLY',records=records,effective_static_compliance_ratio=records[0]['half_work_J']/records[1]['half_work_J'],scope='Actual original anchor-owner/indexPairs;world infinitesimal rotation J=[I,-cross(r)]. No prestress/geometric stiffness or Native nonlinear tangent/energy API claim. Static reference not Native equilibrium. Original root conditions retained. No mass matching needed for statics;dynamic masses differ explicitly.',physical_validation='NOT QUALIFIED',source_sha256=sha(Path(__file__)),scene_sha256=sha(src/'scene.scn'));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(status=d['status'],ratio=d['effective_static_compliance_ratio'],metrics=[{k:v for k,v in r.items() if k!='displacement'} for r in records])))
if __name__=='__main__':main()
