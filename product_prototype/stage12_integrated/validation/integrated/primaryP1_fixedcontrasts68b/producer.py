"""Physical-coordinate fullvector contrasts; no rigid alignment or gauge fitting.
Degree2 fourpoint quadrature on each actual tetra; target interpolation exact.
Quadrature across a target mesh subdivision is a declared numerical observation,
NOT claimed exact continuous L2 integration or certified observer convergence.
"""
import sys,json,shutil,numpy as np
from scipy.spatial import cKDTree
from baseline_registry import ROOT,REPO,ref,dump
V=ROOT/'validation/integrated';out=V/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');parent=V/'primaryP1_fixedcontrasts68/summary.json';d=json.loads(parent.read_text());rows=d['rows'];fs=[np.load(REPO/json.loads((REPO/r['source']['path']).read_text())['field']['path']) for r in rows];geom={};maps={};bc4=np.full((4,4),.1381966011250105);np.fill_diagonal(bc4,.5854101966249685)
for r,a in zip(rows,fs):geom.setdefault(r['h_mm'],a)
for hs,a in geom.items():
 for ht,b in geom.items():
  if hs==ht:continue
  assert not(ROOT/'runtime/STOP').exists();ps=a['points_mm'];ts=a['tetra'];pt=b['points_mm'];tt=b['tetra'];vol=abs(np.linalg.det(ps[ts[:,1:]]-ps[ts[:,0,None]]))/6;points=np.einsum('qa,taj->tqj',bc4,ps[ts]).reshape(-1,3);weights=np.repeat(vol/4,4);centers=pt[tt].mean(1);radius=float(np.linalg.norm(pt[tt]-centers[:,None,:],axis=2).max())+1e-8;tree=cKDTree(centers);inv=np.linalg.inv(np.transpose(pt[tt[:,1:]]-pt[tt[:,0,None]],(0,2,1)));target=np.full(len(points),-1,dtype=int);bary=np.full((len(points),4),np.nan)
  for first in range(0,len(points),512):
   assert not(ROOT/'runtime/STOP').exists();xx=points[first:first+512];neighbors=tree.query_ball_point(xx,radius);qi=np.repeat(np.arange(len(xx)),[len(q) for q in neighbors]);fi=np.concatenate([np.array(q,dtype=int) for q in neighbors]);b123=np.einsum('nij,nj->ni',inv[fi],xx[qi]-pt[tt[fi,0]]);bs=np.c_[1-b123.sum(1),b123];ok=bs.min(1)>=-1e-10;uq,indices=np.unique(qi[ok],return_index=True);chosen=np.flatnonzero(ok)[indices];target[first+uq]=fi[chosen];bary[first+uq]=bs[chosen]
  mask=target>=0;np.savez_compressed(out/f'geometry_{hs:g}_to_{ht:g}.npz',points_mm=points,weights_mm3=weights,target_tetra=target,target_barycentric=bary,covered=mask,source_barycentric=bc4);maps[hs,ht]=(target,bary,mask,weights)
  print(json.dumps(dict(source_h=hs,target_h=ht,points=len(points),uncovered=int((~mask).sum()),uncovered_volume_weight_mm3=float(weights[~mask].sum()))),flush=True)
pairs=[]
for i in range(len(rows)):
 for j in range(i+1,len(rows)):
  hs=rows[i]['h_mm'];ht=rows[j]['h_mm']
  if hs==ht:continue
  directions=[]
  for ii,jj in [(i,j),(j,i)]:
   ha=rows[ii]['h_mm'];hb=rows[jj]['h_mm'];a=fs[ii];b=fs[jj];target,bary,mask,weights=maps[ha,hb];ua=np.einsum('qa,taj->tqj',bc4,a['displacement_mm'][a['tetra']]).reshape(-1,3);ub=np.einsum('ni,nij->nj',bary[mask],b['displacement_mm'][b['tetra'][target[mask]]]);err=float(np.sqrt(np.sum(weights[mask]*np.sum((ua[mask]-ub)**2,axis=1))/weights[mask].sum()));base=float(np.sqrt(np.sum(weights[mask]*np.sum(ub**2,axis=1))/weights[mask].sum()));relative=err/base;complete=bool(mask.all());directions.append(dict(source_h_mm=ha,target_h_mm=hb,geometry=ref(out/f'geometry_{ha:g}_to_{hb:g}.npz'),point_coverage_complete=complete,uncovered_points=int((~mask).sum()),uncovered_volume_weight_mm3=float(weights[~mask].sum()),covered_volume_vector_difference_RMS_mm=err,covered_volume_target_RMS_mm=base,covered_vector_relative_RMS=relative,full_volume_vector_relative_RMS=relative if complete else None,original1percent_observation=bool(complete and relative<.01),no_alignment=True))
  pairs.append(dict(a=rows[i]['source'],b=rows[j]['source'],both_full_load_local=rows[i]['full_load_local'] and rows[j]['full_load_local'],directions=directions))
d['status']='ACTUAL_P1_FIXED_INTEGRATION_ALLPAIR_SCALAR_AND_PHYSICAL_CROSSMESH_VECTOR_CONTRASTS';d['predecessor']=ref(parent);d['crossmesh_vector_producer']=ref(out/'producer.py');d['crossmesh_vector_pairs']=pairs;d['crossmesh_observation']='Degree2 fourpoint on each actual tetra, targetexact P1 interpolation, BOTH directions, no alignment. Pointcoverage failures retain null fullvolume metric. No continuousL2/observerconvergence PASS inferred.';dump(out/'summary.json',d);print(json.dumps(dict(pairs=len(pairs),geometries=len(maps))))
