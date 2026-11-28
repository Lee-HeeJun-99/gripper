"""Two-direction physical vector observations on SAME actual plate; no alignment.
Fourpoint degree2 rule and optional centroid subdivision contrast. A finite
observation contrast is not a certified exact L2 integration bound.
"""
import sys,json,shutil,itertools,numpy as np
from scipy.spatial import cKDTree
from baseline_registry import ROOT,REPO,ref,dump
V=ROOT/'validation/integrated';out=V/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');level=int(sys.argv[2]);tags=sys.argv[3:];fields=[np.load(V/n/'field.npz') for n in tags];summaries=[json.loads((V/n/'summary.json').read_text()) for n in tags]
base=np.full((4,4),.1381966011250105);np.fill_diagonal(base,.5854101966249685)
rows=[]
for level in [0,1]:
 sub=[np.eye(4)]
 for depth in range(level):
  new=[]
  for tet in sub:
   center=tet.mean(0)
   for j in range(4):a=tet.copy();a[j]=center;new.append(a)
  sub=new
 rule=np.concatenate([base@a for a in sub]);nr=len(rule)
 for ia,ib in itertools.permutations(range(len(tags)),2):
  assert not(ROOT/'runtime/STOP').exists()
  a,b=fields[ia],fields[ib];ps,ts,us=a['points_mm'],a['tetra'],a['displacement_mm'];pt,tt,ut=b['points_mm'],b['tetra'],b['displacement_mm'];vol=abs(np.linalg.det(ps[ts[:,1:]]-ps[ts[:,0,None]]))/6
  centers=pt[tt].mean(1);radius=float(np.linalg.norm(pt[tt]-centers[:,None,:],axis=2).max())+1e-8;tree=cKDTree(centers);inverse=np.linalg.inv(np.transpose(pt[tt[:,1:]]-pt[tt[:,0,None]],(0,2,1)))
  error=0.;denom=0.;coveredV=0.;missV=0.;miss=0;count=0;maxmiss=[]
  for first in range(0,len(ts),64):
   assert not(ROOT/'runtime/STOP').exists()
   tids=ts[first:first+64];xyz=np.einsum('qa,taj->tqj',rule,ps[tids]).reshape(-1,3);ua=np.einsum('qa,taj->tqj',rule,us[tids]).reshape(-1,3);weights=np.repeat(vol[first:first+64]/nr,nr);neigh=tree.query_ball_point(xyz,radius);qi=np.repeat(np.arange(len(xyz)),[len(q) for q in neigh]);fi=np.concatenate([np.array(q,dtype=int) for q in neigh]);bs3=np.einsum('nij,nj->ni',inverse[fi],xyz[qi]-pt[tt[fi,0]]);bs=np.c_[1-bs3.sum(1),bs3];ok=bs.min(1)>=-1e-10;uq,idx=np.unique(qi[ok],return_index=True);chosen=np.flatnonzero(ok)[idx];mask=np.ones(len(xyz),bool);mask[uq]=False
   ub=np.einsum('ni,nij->nj',bs[chosen],ut[tt[fi[chosen]]]);error+=float(np.sum(weights[uq]*np.sum((ua[uq]-ub)**2,axis=1)));denom+=float(np.sum(weights[uq]*np.sum(ub**2,axis=1)));coveredV+=float(weights[uq].sum());missV+=float(weights[mask].sum());miss+=int(mask.sum());count+=len(xyz)
   if mask.any() and len(maxmiss)<10:maxmiss.extend(xyz[mask][:10-len(maxmiss)].tolist())
  complete=miss==0;rel=(error/denom)**.5
  row=dict(source=ref(V/tags[ia]/'summary.json'),target=ref(V/tags[ib]/'summary.json'),points=count,subdivision_level=level,points_per_source_tetra=nr,covered_volume_mm3=coveredV,uncovered_points=miss,uncovered_volume_weight_mm3=missV,uncovered_examples_mm=maxmiss,coverage_complete=complete,covered_vector_relative_RMS=rel,full_volume_vector_relative_RMS=rel if complete else None,covered_difference_RMS_mm=(error/coveredV)**.5,covered_target_RMS_mm=(denom/coveredV)**.5,within_original_1percent=bool(complete and rel<.01),both_full_load_local=all(summaries[ia]['checks'].values()) and all(summaries[ib]['checks'].values()),no_alignment=True)
  rows.append(row);dump(out/'partial_rows.json',rows);print(json.dumps(row),flush=True)
dump(out/'summary.json',dict(status='ACTUAL_P1_BIDIRECTIONAL_PHYSICAL_VECTOR_OBSERVATIONS',candidate=summaries[0]['candidate'],producer=ref(out/'producer.py'),observation_subdivision_levels=[0,1],rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='All physical-coordinate meshpairs in both directions. Original1percent retained. Uncovered points give null fullvolume metric. Quadrature refinement is observation evidence, NOT exact intersection L2 certification. No time/globalenergy/full83body certificate.'))
