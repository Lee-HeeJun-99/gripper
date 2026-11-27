"""Same P1 fourmount offaxis finite candidate with independent nut/bolt axes.
Planar search only;never remove spatial DOFs from subsequent actual statics.
"""
import json,math,shutil
import numpy as np
from scipy.optimize import minimize,brentq,minimize_scalar
from baseline_registry import ROOT,ref,sha,REPO,dump
from primary_takeup53e import constraints as old_constraints,rot,XY,C,NORMALS,HEX,K,CLEAR
from primary_edge54 import first_edge

def unpack(v):
 a=brentq(lambda a:51.5*math.sin(a)+2.05*math.cos(a)-2.1,0,.01,xtol=1e-15);u=(rot(a)-np.eye(2))@np.array([97.,0.]);q=np.r_[u,a,v[:29]];return q,v[29:].reshape(4,2)
def rows(v,detail=False):
 q,offsets=unpack(v);rr=[r for r in old_constraints(q,True) if r['kind']!='nutcage'];j=q[4:].reshape(4,7)
 for i in range(4):
  boltaxis=XY[i]+j[i,:2];nutaxis=XY[i]+offsets[i];beta,nu=j[i,2:4]
  for k,pt in enumerate(HEX@rot(nu).T+nutaxis):
   for wall,n in enumerate(NORMALS):rr.append(dict(label=f'nutcage_{i}_{k}_{wall}',gap_mm=float(4.1-n@(pt-XY[i])),i=i,kind='nutcage',point_xy=pt.tolist(),inward_xy=(-n).tolist()))
  delta=boltaxis-nutaxis;an,stop=first_edge(delta,beta,nu)
  # Opposite side mirrored at the same delta: angle coefficient flips K.
  angle=math.atan2(delta[1],delta[0]);rn=4.334/2
  def lower(a):
   p=rn*np.array([np.cos(a),np.sin(a)]);b=p-delta;rb=np.linalg.norm(b);da=math.atan2(p[0]*b[1]-p[1]*b[0],p@b);return -CLEAR+K*(beta-nu-da)-(rb-rn)/math.sqrt(3)
  ss=minimize_scalar(lambda a:-lower(a),bounds=(angle+math.pi-.5,angle+math.pi+.5),method='bounded',options=dict(xatol=1e-12));start=lower(ss.x)
  rr.append(dict(label=f'thread_minus_{i}',kind='thread_minus',i=i,gap_mm=float(stop-q[3]),angle_rad=float(an),opening_stop_mm=stop))
  rr.append(dict(label=f'thread_plus_{i}',kind='thread_plus',i=i,gap_mm=float(q[3]-start),angle_rad=float(ss.x),opening_stop_mm=start))
  rr.append(dict(label=f'offset_domain_{i}',kind='limited_search_domain',i=i,gap_mm=float(.08-np.linalg.norm(delta))))
 return rr if detail else np.array([r['gap_mm'] for r in rr if r['kind']!='guide'])
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_independent54';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_guide53/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());oldp=ROOT/'validation/integrated/primaryP1_takeup53e/summary.json';d=json.loads(oldp.read_text());q=np.array(d['coordinates']);v=np.r_[q[3:],q[4:].reshape(4,7)[:,:2].ravel()];v[0]-=.002
 bounds=[(0,.12)]+[b for i in range(4) for b in [(-.3,.3),(-.3,.3),(-.15,.15),(-.15,.15),(-.6,.6),(-.6,.6),(-.1,.1)]]+[(-.2,.2)]*8
 result=minimize(lambda v:-v[0],v,method='SLSQP',constraints=[dict(type='ineq',fun=rows)],bounds=bounds,options=dict(ftol=1e-11,maxiter=150));q,no=unpack(result.x);allrows=rows(result.x,True);minimum=min(r['gap_mm'] for r in allrows);j=q[4:].reshape(4,7);rc=(XY-C)@rot(q[2]).T+C+q[:2];poses={};names=[]
 for i in range(4):
  for typ,xy,a,z in [('BOLT',XY[i]+j[i,:2],j[i,2],q[3]),('NUT',XY[i]+no[i],j[i,3],0),('SOCKET_KEY',XY[i]+j[i,4:6],j[i,6],q[3]),('SPLIT_PIN',(rc[i]+XY[i]+j[i,4:6])/2,(q[2]+j[i,6])/2,q[3])]:
   n=f'BENCH_MOUNT_{typ}_{i}';names.append(n);poses[n]=dict(rotation_about_mm=[*XY[i],74],yaw_rad=float(a),translation_after_rotation_mm=[*(xy-XY[i]),float(z)])
 names+=['BENCH_ANCHOR_RAIL','BENCH_SUPPORT'];poses['BENCH_ANCHOR_RAIL']=dict(rotation_about_mm=[*C,74],yaw_rad=float(q[2]),translation_after_rotation_mm=[*q[:2],float(q[3])]);poses['BENCH_SUPPORT']=dict(rotation_about_mm=[*C,74],yaw_rad=0.,translation_after_rotation_mm=[0.,0.,0.])
 checks=dict(optimizer_success=bool(result.success),all_finite_gaps=minimum>-1e-7,independent_nut_axes=True,no_search_domain_boundary=all(r['gap_mm']>1e-5 for r in allrows if r['kind']=='limited_search_domain'))
 dump(out/'summary.json',dict(status='ACTUAL_P1_OFFAXIS_FINITE_CANDIDATE_NOT_EQUILIBRIUM' if all(checks.values()) else 'ACTUAL_P1_OFFAXIS_FINITE_CANDIDATE_SEARCH_FAIL',candidate=ref(cp),source=ref(oldp),producer=ref(out/'producer.py'),checks=checks,optimizer=dict(success=bool(result.success),iterations=result.nit,message=result.message),opening_mm=float(q[3]),minimum_gap_mm=float(minimum),variables=result.x.tolist(),old_coordinates=q.tolist(),nut_translations_mm=no.tolist(),poses=poses,body_names=names,active_constraints=[r for r in allrows if r['gap_mm']<1e-7],all_constraints=allrows,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Finite planar search with fixed receiverguide endpoint;full18body108DOFstatics NOTyet solved','Exact parallelaxis crest/flank law valid only declared profileband;allactualBRepcontactbindings/wholeassembly/pins required','Limited offaxis searchradius.08mm is computationalscope,NOT physicalcriterion;boundary result wouldnotprove productfailure','Nominalgaps havezero reaction;noexternalfixation/preload/friction oroperatingdemand']));print(json.dumps(dict(checks=checks,opening=float(q[3]),minimum_gap=minimum,iterations=result.nit,message=result.message)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
