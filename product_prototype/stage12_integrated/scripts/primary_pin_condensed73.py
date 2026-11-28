"""Actual P1 finite split-pin / keeper / Root contact. Conditional gravity cut.
Entire source pin meshed, including eye/splayed legs. No physical fixed DOF.
Rigid keeper/Root are explicit local constitutive limits, not system approval.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.spatial.transform import Rotation
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
import osqp
from scipy.sparse.linalg import splu
from scipy.linalg import qr
from scipy.optimize import linprog, minimize
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_keeper_finite72 import meshpart
from primary_keeper_coupled71 import faces,pointdist
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder

def massgeometry(s):
 g=GProp_GProps();BRepGProp.VolumeProperties_s(s,g);c=g.CentreOfMass();return g.Mass(),np.array([c.X(),c.Y(),c.Z()])
def skew(v):
 x,y,z=v;return np.array([[0,-z,y],[z,0,-x],[-y,x,0.]])
def rotation(w):return Rotation.from_rotvec(w).as_matrix()
def leftJ(w):
 a=np.linalg.norm(w);W=skew(w)
 return np.eye(3)+((1-np.cos(a))/a**2 if a>1e-7 else .5-a*a/24)*W+((a-np.sin(a))/a**3 if a>1e-7 else 1/6-a*a/120)*W@W
def main():
 start=time.monotonic();h=float(sys.argv[1]);out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);names=['ROOT_SOCKET_KEEPER_INSTALLED_SPLIT_PIN','ROOT_SOCKET_KEEPER','F0_ROOT_BACK'];shapes=[read(REPO/refs[n]['path']) for n in names];meta=[massgeometry(s) for s in shapes];origin=np.array([60.,0.,-2.]);p,t,tri,Vcad=meshpart(REPO/refs[names[0]]['path'],h,12)
 # True split cuts x=60+-.02, NOT an unsplit cylinder. At vertical firstcontact
 # the actual split edge, not the missing x=60 crown, supports the bore.
 d=np.sqrt(.5**2-.02**2)-np.sqrt(.45**2-.02**2);p[:,2]-=d;keeper_shift=-2*d;N=3*len(p);M=N+12;L=.001;OBJ=.0001
 la,mu=lame_parameters(200000.,.3);mesh=MeshTet(p.T,t.T);K=sparse.csr_matrix((N,N))
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(mesh,ElementVector(ElementTetP1()),intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 xyz=p[t];mat=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2);vol=abs(np.linalg.det(mat))/6
 # Explicit assumed mass contrast, same actual solids and standard gravity.
 density=7.9e-6;g=9.80665;f=np.zeros(M);weights=np.zeros(len(p))
 for j in range(4):np.add.at(weights,t[:,j],vol/4)
 f[:N].reshape(-1,3)[:,2]=-density*g*weights
 kc=meta[1][1]+[0,0,keeper_shift];kf=np.array([0,0,-density*g*meta[1][0]]);f[N:N+3]=kf;f[N+3:N+6]=np.cross(kc-origin,kf)
 pinforce=f[:N].reshape(-1,3).sum(0);pinmoment=np.cross(p-origin,f[:N].reshape(-1,3)).sum(0)
 f[N+6:N+9]=-(pinforce+kf);f[N+9:N+12]=-(pinmoment+f[N+3:N+6]);load=f.copy()
 intervals=[(0,-1.,1.,origin+np.array([0,0,keeper_shift])),(1,-2.,-1.05,origin.copy()),(1,1.05,2.,origin.copy())]
 edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0);verts=np.unique(tri)
 # Only shaft material can enter these finite bores; all other surfaces retained
 # in mesh and checked separately against STEP at rigid settled reference.
 verts=verts[(p[verts,1]>-2.5)&(p[verts,1]<2.5)];edges=edges[np.any((p[edges,1]>-2.5)&(p[edges,1]<2.5),axis=1)]
 def geometry(x):
  pos=p+x[:N].reshape(-1,3)*L;keys=[];gaps=[];rr=[];cc=[];vv=[];pts=[];pull=[];hostpts=[]
  for ii,(body,lo,hi,center) in enumerate(intervals):
   off=N+6*body;dt=x[off:off+3]*L;w=x[off+3:off+6]*L
   # Small rigid chart; exact finite host rotation is independently checked.
   R=rotation(w);B=R.T;J=leftJ(w);local=(pos-origin-dt)@B.T+origin;features=[]
   for node in verts:
    if lo<=local[node,1]<=hi:features.append((('v',int(node),-1),[int(node)],[1.],local[node],None))
   for a,b in edges:
    delta=local[b]-local[a]
    if abs(delta[1])<1e-14:continue
    for end,y in enumerate([lo,hi]):
     tau=(y-local[a,1])/delta[1]
     if 0<tau<1:features.append((('e',int(a),int(b),end),[int(a),int(b)],[1-tau,tau],local[a]+tau*delta,delta))
   for key,nd,wt,pt,delta in features:
    radial=(pt-center)*[1,0,1];rho=np.linalg.norm(radial);n=-radial/rho;gap=.5-rho;grad=n.copy()
    if delta is not None:grad[1]-=n@delta/delta[1]
    # derivative at zero/small chart, including movingfiniteend materialtrim.
    worldgrad=B.T@grad;material=np.sum(pos[nd]*np.array(wt)[:,None],axis=0);hostgrad=-worldgrad;moment=J.T@np.cross(material-origin-dt,hostgrad)
    row=len(keys);keys.append((ii,*key));gaps.append(gap);pts.append(material);pull.append(worldgrad);hostpts.append(pt)
    for node,weight in zip(nd,wt):
     for j in range(3):rr.append(row);cc.append(3*node+j);vv.append(weight*worldgrad[j])
    for j in range(3):rr.append(row);cc.append(off+j);vv.append(hostgrad[j]);rr.append(row);cc.append(off+3+j);vv.append(moment[j])
  # Actual keeper tongue prism. Its upper exposed portion is clipped at the
  # moving Root top z=-1; wall normals do not extend above the physical slot.
  corners=np.array([[a,b,c] for a in [59.,61.] for b in [-1.,1.] for c in [-2.9,2.]])+[0,0,keeper_shift]
  edgepairs=[(a,b) for a in range(8) for b in range(a+1,8) if np.sum(corners[a]!=corners[b])==1]
  dk=x[N:N+3]*L;wk=x[N+3:N+6]*L;dr=x[N+6:N+9]*L;wr=x[N+9:N+12]*L
  RK=rotation(wk);RR=rotation(wr);JK=leftJ(wk);JR=leftJ(wr)
  kp=(corners-origin)@RK.T+origin+dk;local=(kp-origin-dr)@RR+origin;features=[]
  for j,pt in enumerate(local):
   if pt[2]<=-1:features.append((('v',j),pt,kp[j],None))
  for a,b in edgepairs:
   dd=local[b]-local[a]
   if abs(dd[2])<1e-14:continue
   tau=(-1-local[a,2])/dd[2]
   if 0<tau<1:features.append((('e',a,b),local[a]+tau*dd,kp[a]+tau*(kp[b]-kp[a]),dd))
  for key,pt,material,dd in features:
   for ax,lo,hi in [(0,58.95,61.05),(1,-1.05,1.05),(2,-3.1,None)]:
    if ax==2 and dd is not None:continue
    for sign,limit in [(1,lo)]+([(-1,hi)] if hi is not None else []):
     grad=np.eye(3)[ax]*sign;val=sign*(pt[ax]-limit)
     if dd is not None:grad[2]-=grad@dd/dd[2]
     worldgrad=RR@grad;row=len(keys);keys.append((3,ax,sign,*key));gaps.append(val);pts.append(material);pull.append(worldgrad);hostpts.append(pt)
     for off,sgn,dt,J in [(N,1,dk,JK),(N+6,-1,dr,JR)]:
      force=sgn*worldgrad;moment=J.T@np.cross(material-origin-dt,force)
      for j in range(3):rr.append(row);cc.append(off+j);vv.append(force[j]);rr.append(row);cc.append(off+3+j);vv.append(moment[j])
  A=sparse.coo_matrix((vv,(rr,cc)),shape=(len(keys),M)).tocsr();return np.array(gaps),A,keys,np.array(pts),np.array(pull),np.array(hostpts)
 print(json.dumps(dict(phase='mesh',nodes=len(p),tetra=len(t),clearance_each_mm=d,keeper_settled_z_mm=keeper_shift,conditional_keeper_weight_N=float(-kf[2]),conditional_pin_weight_N=float(-pinforce[2]))),flush=True)
 P=sparse.block_diag([K*(L*L/OBJ),sparse.csr_matrix((12,12))],format='csc');q=-f*L/OBJ;x=np.zeros(M);journal=[];final=None
 # Floating pin substructure condensation. Six internal gauges only define the
 # elastic/rigid decomposition; all six pin rigid modes are restored explicitly.
 RB=np.zeros((M,18));RB[:N,:3]=np.tile(np.eye(3),(len(p),1))
 for j,pt in enumerate(p):RB[3*j:3*j+3,3:6]=-skew(pt-origin)
 RB[N:,6:]=np.eye(12);G=np.linalg.qr(RB[:N,:6])[0]
 aug=sparse.bmat([[P[:N,:N],sparse.csc_matrix(G)],[sparse.csc_matrix(G.T),None]],format='csc');fac=splu(aug)
 def solvecontact(A,lower):
  Ae=A[:,:N];B=np.asarray(A@RB);rhs=np.c_[(-q[:N]),Ae.T.toarray()];sol=fac.solve(np.r_[rhs,np.zeros((6,rhs.shape[1]))]);U=sol[:N];C=np.asarray(Ae@U[:,1:]);C=(C+C.T)/2;hd=np.asarray(Ae@U[:,0])-lower;eq=B.T;target=RB.T@q
  _,rr,piv=qr(eq.T,mode='economic',pivoting=True);rank=int(np.sum(abs(np.diag(rr))>1e-10));sel=piv[:rank];E=eq[sel];v=target[sel]
  seed=linprog(hd,A_eq=E,b_eq=v,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
  if not seed.success:return None,dict(status='reaction_cone_infeasible',message=seed.message,rank=rank)
  result=minimize(lambda z:.5*z@C@z+hd@z,seed.x,jac=lambda z:C@z+hd,method='SLSQP',bounds=[(0,None)]*len(hd),constraints=[dict(type='eq',fun=lambda z:E@z-v,jac=lambda z:E)],options={'maxiter':500,'ftol':1e-13})
  eta=result.x;ue=U[:,0]+U[:,1:]@eta;active=np.flatnonzero(eta>1e-8);zr=np.linalg.lstsq(B[active],lower[active]-Ae[active]@ue,rcond=1e-11)[0];xn=RB@zr;xn[:N]+=ue;info=dict(status=str(result.message),iterations=int(result.nit),rank=rank,full18_reaction_residual=float(abs(eq@eta-target).max()),decomposition_gauge_residual=float(abs(sol[-6:,0]+sol[-6:,1:]@eta).max()),minimum_linear_gap=float((A@xn-lower).min()),active=len(active));return (xn,eta),info

 for iteration in range(10):
  assert not(ROOT/'runtime/STOP').exists();gap,A,keys,pts,pull,hpts=geometry(x);lower=-gap/L+A@x
  answer,info=solvecontact(A,lower);print(json.dumps(dict(phase='condensed',**info)),flush=True)
  if answer is None:
   dump(out/'summary.json',dict(status='ACTUAL_P1_PIN_SLOT_REACTION_CONE_REJECTED',candidate_reference=ref(cp),producer=ref(out/'producer.py'),condensation=info,journal=journal,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False));return 2
  xn,eta=answer;lam=eta*OBJ/L
  gapn,An,kn,pn,pbn,hpn=geometry(xn);same=kn==keys;force=A.T@lam;res=np.r_[K@(xn[:N]*L),np.zeros(12)]-force-load
  entry=dict(iteration=iteration,solver_status=info['status'],solver_iterations=info['iterations'],condensation=info,rows=len(keys),minimum_linearized_gap_mm=float((A@xn-lower).min()*L),minimum_next_curved_gap_mm=float(gapn.min()),force_torque_residual=float(abs(res).max()),min_multiplier_N=float(lam.min()),complementarity_Nmm=float(abs(lam*(A@xn-lower)*L).max()),delta_scaled=float(abs(xn-x).max()),contact_topology_same=same,energy_Nmm=float(xn[:N]@K@xn[:N]*L*L/2));journal.append(entry);print(json.dumps(entry),flush=True)
  np.savez_compressed(out/f'iterate_{iteration:02}.npz',unknown=xn,normal_force_N=lam,linearization_unknown=x,gap_mm=gap,contact_points_mm=pts,pullback=pull,load_N_Nmm=load)
  final=(gap,A,keys,pts,pull,lam,res);change=abs(xn-x).max();x=xn
  if same and change<1e-7 and abs(res).max()<1e-8 and gapn.min()>=-1e-9:break
 gap,A,keys,pts,pull,lam,res=final;u=x[:N].reshape(-1,3)*L;nodal=(A.T@lam)[:N].reshape(-1,3);deformed=p+u;bodyw=np.zeros((3,6));bodyw[0,:3]=(nodal+load[:N].reshape(-1,3)).sum(0);bodyw[0,3:]=np.cross(deformed-origin,nodal+load[:N].reshape(-1,3)).sum(0)
 gen=A.T@lam
 for b in range(2):
  bodyw[1+b]=gen[N+6*b:N+6*b+6]+load[N+6*b:N+6*b+6]
  J=leftJ(x[N+6*b+3:N+6*b+6]*L);bodyw[1+b,3:]=np.linalg.solve(J.T,bodyw[1+b,3:])
 gfinal,afinal,kfinal,*_=geometry(x)
 # Initial reference actual BRep nonpenetration, and actual contact edge distances.
 posed=[translate(shapes[0],0,0,-d),translate(shapes[1],0,0,keeper_shift),shapes[2]];booleans={f'{i}_{j}':common(posed[i],posed[j]) for i,j in [(0,1),(0,2),(1,2)]};surface=[]
 for ii,(body,lo,hi,c) in enumerate(intervals):
  for sx in [-1,1]:
   # keeper loads pin at top; Root reacts at bottom.
   z=c[2]+(1 if body==0 else -1)*np.sqrt(.5**2-.02**2);pt=np.array([60+sx*.02,(lo+hi)/2,z]);surface.append(dict(interval=ii,point_mm=pt.tolist(),pin_distance_mm=pointdist(posed[0],pt),host_distance_mm=pointdist(posed[1+body],pt)))
 checks=dict(all83_sources_verified=True,actual_settled_solids_clear=max(booleans.values())<1e-8,actual_split_edge_points=all(max(z['pin_distance_mm'],z['host_distance_mm'])<1e-7 for z in surface),original_full_force_torque=float(abs(res).max())<1e-8,all_body_deformed_wrenches=float(abs(bodyw).max())<1e-8,nonnegative_multipliers=float(lam.min())>=-1e-9,all_curved_clipped_facet_gaps=float(gfinal.min())>=-1e-9,complementarity=journal[-1]['complementarity_Nmm']<1e-8,final_topology_same=kfinal==keys)
 np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,boundary_triangles=tri,displacement_mm=u,load_N_Nmm=load,contact_nodal_force_N=nodal,rigid_keeper_root_chart=x[N:]*L,normal_force_N=lam,gap_mm=gap,contact_points_mm=pts,pullback=pull,element_volume_mm3=vol,body_residual_wrenches=bodyw)
 dump(out/'contact_keys.json',keys);dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_SPLITPIN_GRAVITY_CONTACT_LOCAL_REFERENCE' if all(checks.values()) else 'ACTUAL_P1_FINITE_SPLITPIN_CONTACT_FAIL_PRESERVED',candidate_reference=ref(cp),producer=ref(out/'producer.py'),part_references={n:refs[n] for n in names},field=ref(out/'field.npz'),contact_keys=ref(out/'contact_keys.json'),checks={k:bool(v) for k,v in checks.items()},h_mm=h,nodes=len(p),tetra=len(t),source_CAD_volume_mm3=Vcad,mesh_volume_mm3=float(vol.sum()),E_ASSUMED_MPa=200000,nu_ASSUMED=.3,density_ASSUMED_kg_mm3=density,gravity_m_s2=g,conditional_keeper_weight_N=float(-kf[2]),conditional_pin_weight_N=float(-pinforce[2]),keeper_settled_z_mm=keeper_shift,pin_settled_z_mm=-d,rigid_keeper_root_chart_mm_rad=(x[N:]*L).tolist(),maximum_displacement_mm=float(np.linalg.norm(u,axis=1).max()),static_pin_energy_Nmm=journal[-1]['energy_Nmm'],allbody_deformed_residuals_N_Nmm=bodyw.tolist(),original_force_torque_maximum=float(abs(res).max()),actual_BRep_intersection_mm3=booleans,exact_split_edge_contact_points=surface,physical_fixed_DOF=0,all_pin_elastic_DOF=N,free_keeper_root_DOF=12,numerical_fixation_reactions=[],journal=journal,newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,actual_changed_CAD=[],elapsed_s=time.monotonic()-start,limitations=['Whole real splitpin meshed including eye and splayedlegs. Actual finite three bores and split edges; no unsplit solidshaft substitution.','Keeper and Root are rigid constitutive limits; host compliance, bolt/nut/seat/thread/preload, gravity of other80bodies and actualoperatingequilibrium UNSOLVED.','Gravity uses explicit typicaldensity assumption, not a source-minimum/materialcertificate or actual100g demand. Root cut reaction balances localassembly weight; it is not a groundattachment solution.','Smallrotation rigidchart and linear elasticity; completepolyhedralfacet clipping is not curvedSTEP/fullspatial1percent/time.1percent/globalenergy qualification.','Eye and splayedleg finite solids retained but endstop/frictional contact is not included in this radialgravity branch; zero axialload/freeaxialnullmode is not stabilitycertification.']))
 return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
