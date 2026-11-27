"""Finite same-P1 four-mount planar candidate search. Coaxial-thread subspace only.
Fresh contact geometry, no inherited endpoint multipliers or fixed-body statics.
"""
import json,math,sys,shutil,os,time
import numpy as np
from scipy.optimize import minimize,linprog
from baseline_registry import ROOT,REPO,ref,sha,dump
XY=np.array([[-59.,-58.],[101.,-58.],[-59.,39.],[101.,39.]])
C=np.array([21.,-9.5]);K=.8/(2*math.pi);CLEAR=(4.605-4.456)/2/math.sqrt(3)
def rot(a):return np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
def polygon(n,r):return r*np.array([[math.cos(j*2*math.pi/n),math.sin(j*2*math.pi/n)] for j in range(n)])
HEX=polygon(6,8/math.sqrt(3));KEYHEX=polygon(6,3.9/math.sqrt(3));SQUARE=np.array([[-4.5,-4.5],[-4.5,4.5],[4.5,-4.5],[4.5,4.5]])
NORMALS=np.array([[math.cos(j*math.pi/3+math.pi/6),math.sin(j*math.pi/3+math.pi/6)] for j in range(6)])
# q: receiver tx,ty,yaw,opening; each mount axis tx,ty,beta,nu,key tx,ty,keyyaw.
def unpack(q):
 t=q[2];rc=(XY-C)@rot(t).T+C+q[:2];j=q[4:].reshape(4,7);axes=XY+j[:,:2];keys=XY+j[:,4:6];return rc,axes,keys,j

def constraints(q,details=False):
 rc,axes,keys,j=unpack(q);t=q[2];R=rot(t);rows=[]
 def add(label,g,**kw):rows.append(dict(label=label,gap_mm=float(g),**kw))
 for i in range(4):
  axis=axes[i];kc=keys[i];beta,nu,a=j[i,[2,3,6]]
  # Circumscribed actual crest envelope: sufficient clearance only,not thread/bore contact certification.
  add(f'bore_receiver_{i}',.262-np.linalg.norm(axis-rc[i]),kind='conservative_crest_envelope')
  add(f'bore_support_{i}',.262-np.linalg.norm(axis-XY[i]),kind='conservative_crest_envelope')
  for v,pt in enumerate(HEX@rot(nu).T+axis):
   for wall,n in enumerate(NORMALS):add(f'nutcage_{i}_{v}_{wall}',4.1-n@(pt-XY[i]),i=i,kind='nutcage',vertex=v,wall=wall,point_xy=pt.tolist(),inward_xy=(-n).tolist())
  for v,pt in enumerate(SQUARE@rot(a).T+kc):
   loc=R.T@(pt-rc[i])
   for dim in [0]:
    for sign in [-1,1]:
     n=R[:,dim]*sign;add(f'keycage_{i}_{v}_{dim}_{sign}',4.6-sign*loc[dim],i=i,kind='keycage',vertex=v,point_xy=pt.tolist(),inward_xy=(-n).tolist())
  for v,pt in enumerate(KEYHEX@rot(a).T+kc):
   for wall,n0 in enumerate(NORMALS):
    n=rot(beta)@n0;add(f'socket_{i}_{v}_{wall}',2.-n@(pt-axis),i=i,kind='socket',vertex=v,wall=wall,point_xy=pt.tolist(),inward_xy=(-n).tolist())
 for gi,y in enumerate([-58.,39.]):
  for v,p in enumerate(np.array([[-78.05,y-3],[-78.05,y+3],[-73.95,y-3],[-73.95,y+3]])):
   pt=R@(p-C)+C+q[:2];loc=pt-[-76,y]
   for dim,h in [(0,2.1),(1,3.1)]:
    for sign in [-1,1]:
     n=np.eye(2)[dim]*sign;add(f'guide_{gi}_{v}_{dim}_{sign}',h-sign*loc[dim],kind='guide',point_xy=pt.tolist(),inward_xy=(-n).tolist(),guide=gi,vertex=v)
 return rows if details else np.array([r['gap_mm'] for r in rows])
def phaseeq(q):
 j=q[4:].reshape(4,7);return q[3]-CLEAR-K*(j[:,2]-j[:,3])
def eq(q):
 from scipy.optimize import brentq
 a=brentq(lambda t:51.5*math.sin(t)+2.05*math.cos(t)-2.1,0,.01,xtol=1e-15)
 u=(rot(a)-np.eye(2))@np.array([97.,0.])
 return np.r_[phaseeq(q),q[:2]-u,q[2]-a]
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_takeup53e';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_guide53/summary.json';d=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*d['part_references'].values(),d['assembly'],d['BOM']]);solutions=[]
 bounds=[(-.5,.5),(-.5,.5),(-.006,.006),(0,.1)]+[b for i in range(4) for b in [(-.3,.3),(-.3,.3),(-.15,.15),(-.15,.15),(-.6,.6),(-.6,.6),(-.1,.1)]]
 from scipy.optimize import brentq
 a=brentq(lambda t:51.5*math.sin(t)+2.05*math.cos(t)-2.1,0,.01,xtol=1e-15);u=(rot(a)-np.eye(2))@np.array([97.,0.]);fixed=np.r_[u,a]
 def expand(v):
  q=np.zeros(32);q[:3]=fixed;q[3]=v[0];j=q[4:].reshape(4,7);vv=v[1:].reshape(4,6);j[:,:2]=vv[:,:2];j[:,3]=vv[:,2];j[:,2]=vv[:,2]+(v[0]-CLEAR)/K;j[:,4:6]=vv[:,3:5];j[:,6]=vv[:,5];return q
 def reduced_constraints(v):
  q=expand(v);rows=constraints(q,True);beta=q[4:].reshape(4,7)[:,2];return np.r_[[r['gap_mm'] for r in rows if r['kind']!='guide'],.15-beta,.15+beta]
 v=np.zeros(25);v[0]=CLEAR
 rc=(XY-C)@rot(a).T+C+u
 for i in range(4):
  dy=np.clip(rc[i,1]-XY[i,1],-.095,.095);v[1+i*6+1]=dy;v[1+i*6+4]=dy
 rb=[(0,.1)]+[b for i in range(4) for b in [(-.3,.3),(-.3,.3),(-.15,.15),(-.6,.6),(-.6,.6),(-.1,.1)]]
 r=minimize(lambda x:-x[0],v,method='SLSQP',bounds=rb,constraints=[dict(type='ineq',fun=reduced_constraints)],options=dict(ftol=1e-12,maxiter=500));q=expand(r.x)
 solutions.append(dict(start='finite_feasible_bore_offsets',success=bool(r.success),message=r.message,iterations=r.nit,q=q.tolist(),initial_minimum_gap_mm=float(min(reduced_constraints(v))),minimum_gap_mm=float(min(constraints(q))),phase_residual_mm=float(max(abs(eq(q))))));print(json.dumps(solutions[-1]),flush=True)
 feasible=[s for s in solutions if s['success'] and s['minimum_gap_mm']>-1e-8 and s['phase_residual_mm']<1e-8];assert feasible
 best=max(feasible,key=lambda s:s['q'][3]);q=np.array(best['q']);active=[r for r in constraints(q,True) if r['gap_mm']<1e-7];rc,axes,keys,j=unpack(q);bodies=[]
 for i in range(4):
  for typ in ['BOLT','NUT','SOCKET_KEY','SPLIT_PIN']:bodies.append(f'BENCH_MOUNT_{typ}_{i}')
 bodies+=['BENCH_ANCHOR_RAIL','BENCH_SUPPORT'];poses={}
 for i in range(4):
  for typ,xy,a,z in [('BOLT',axes[i],j[i,2],q[3]),('NUT',axes[i],j[i,3],0),('SOCKET_KEY',keys[i],j[i,6],q[3]),('SPLIT_PIN',(rc[i]+keys[i])/2,(q[2]+j[i,6])/2,q[3])]:poses[f'BENCH_MOUNT_{typ}_{i}']=dict(rotation_about_mm=[*XY[i],74],yaw_rad=float(a),translation_after_rotation_mm=[*(xy-XY[i]),float(z)])
 poses['BENCH_ANCHOR_RAIL']=dict(rotation_about_mm=[*C,74],yaw_rad=float(q[2]),translation_after_rotation_mm=[*q[:2],float(q[3])]);poses['BENCH_SUPPORT']=dict(rotation_about_mm=[*C,74],yaw_rad=0.,translation_after_rotation_mm=[0.,0.,0.])
 path=[]
 for s in np.linspace(0,1,21):
  p=q*s;p[3]=CLEAR*s+K*(p[6]-p[7]);g=constraints(p);phase=p[3]-K*(p[4:].reshape(4,7)[:,2]-p[4:].reshape(4,7)[:,3]);path.append(dict(fraction=float(s),minimum_envelope_gap_mm=float(min(g)),thread_loaded_side_gap_mm=(CLEAR-phase).tolist()))
 result=dict(status='ACTUAL_P1_FINITE_GUIDE_ENGAGED_COAXIAL_TAKEUP_CANDIDATE_NOT_EQUILIBRIUM',candidate=ref(cp),actual_parts=128,producer=ref(out/'producer.py'),coordinates=q.tolist(),poses=poses,body_names=bodies,solutions=solutions,active_constraints=active,all_constraints=constraints(q,True),sampled_path=path,opening_mm=float(q[3]),receiver_translation_mm=q[:2].tolist(),receiver_yaw_rad=float(q[2]),coaxial_thread_assumption=True,phase_residual_mm=float(max(abs(eq(q)))),minimum_constraint_gap_mm=float(min(constraints(q))),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Planar finite kinematic search with common bolt/nut axes;NOT equilibrium,unique path or dynamics;rx/ry excluded only from search,NOT from subsequent statics','Circumscribed2.488mm thread crest against2.75mm bores is sufficient envelope clearance,not actual bore contact or continuous helicoid proof','Rigid guide/cage corners require BRep binding and elastic bearing/strength;pin displacement may add earlier contacts','21analytic sampled path states are not continuous full128part CCD;actual wholeassembly motion must be revalidated','No 100goperatingfield,elasticpressure,materialminimum,mesh/time/globalenergy/host orStage3'])
 dump(out/'summary.json',result)
if __name__=='__main__':main()
