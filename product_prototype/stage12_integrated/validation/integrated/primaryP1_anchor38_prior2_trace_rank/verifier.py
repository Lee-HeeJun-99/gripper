"""Independent pointwise diagnostic of actual planar nonmatching FE traces.
Average-cell complementarity is not pointwise impenetrability. No release gate.
Rigid recovery uses the producer equilibrium rank cutoff1e-10; near-null
roundoff equilibrium modes must not be inverted as physical rigid modes.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def rigid(pos,r):return r[:3]+np.cross(r[3:],pos)
def prepare(a,axis,value):
 p=a['points_mm'];tri=a['boundary_triangles'];tri=tri[np.all(abs(p[tri,axis]-value)<1e-7,axis=1)];x=p[tri];inv=np.linalg.pinv((x[:,1:]-x[:,0,None]).transpose(0,2,1));return tri,x,inv

def locate(q,prepared):
 tri,x,inv=prepared;bb=(x.min(1)<=q+1e-7).all(1)&(x.max(1)>=q-1e-7).all(1);ix=np.flatnonzero(bb)
 if not len(ix):return None
 v=np.einsum('tij,tj->ti',inv[ix],q-x[ix,0]);bc=np.c_[1-v.sum(1),v];good=np.flatnonzero((bc.min(1)>-1e-7)&(bc.max(1)<1+1e-7))
 if not len(good):return None
 return tri[ix[good[0]]],bc[good[0]]

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated'/sys.argv[2];d=json.loads((src/'summary.json').read_text());geo=json.loads((REPO/d['geometry']['path']).read_text());a=[dict(np.load(REPO/r['path'])) for r in d['fields']];ops=np.load(REPO/d['operators']['path']);eq=ops['equality'];scale=np.tile([1,1,1,.01,.01,.01],2);nc=d['contact_variables'];prepared={};results=[]
 for k,b in enumerate(a):
  if 'U' not in b:b['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in d['body_results'][k]['displacement_chunks']])
 for row in d['rows']:
  if 'equality_multiplier' not in row:continue
  p=np.array(row['contact_forces_N']);w=np.array(row['external_wrench_N_Nmm']);ae=np.array(row['reduced_equality_matrix']);lm=np.array(row['equality_multiplier']);T=ae@np.linalg.pinv(eq*scale[:,None],rcond=1e-10);r=(scale*(T.T@lm)).reshape(2,6);U=[(b['U']@np.r_[p,w if k==0 else -w]).reshape(-1,3) for k,b in enumerate(a)];patches=[]
  for j,patch in enumerate(geo['patches']):
   if patch['label'].startswith('bolt'):continue
   direction=np.array(patch['direction']);axis=int(np.argmax(abs(direction)));value=patch['exact_CAD_centroid_mm'][axis];key=(axis,round(value,7))
   if key not in prepared:prepared[key]=prepare(a[1],axis,value)
   samples=[];miss=0;average=0.;area=0.
   for qd in geo['body_quadrature'][0][j]['quadrature']:
    q=np.array(qd['point_mm']);hit=locate(q,prepared[key])
    if hit is None:miss+=1;continue
    nodes,bc=hit;u0=np.array(qd['barycentric'])@U[0][qd['nodes']];u1=bc@U[1][nodes];gap=float(direction@(u0-u1+rigid(q,r[0])-rigid(q,r[1])));samples.append(gap);average+=gap*qd['area_mm2'];area+=qd['area_mm2']
   patches.append(dict(patch=j,label=patch['label'],cell_force_N=float(p[j]),pressure_positive=bool(p[j]>1e-9),samples=len(samples),unmapped=miss,minimum_sampled_gap_mm=min(samples) if samples else None,maximum_sampled_gap_mm=max(samples) if samples else None,quadrature_average_gap_mm=average/area if area else None,QP_average_gap_mm=row['contact_gap_mm'][j],positive_pressure_samples_negative_1e_minus8=sum(v<-1e-8 for v in samples) if p[j]>1e-9 else 0))
  allmin=[x['minimum_sampled_gap_mm'] for x in patches if x['minimum_sampled_gap_mm'] is not None];results.append(dict(case=row['case'],patches=patches,minimum_sampled_gap_mm=min(allmin),positive_pressure_samples_negative_1e_minus8=sum(x['positive_pressure_samples_negative_1e_minus8'] for x in patches),unmapped=sum(x['unmapped'] for x in patches)))
 dump(out/'summary.json',dict(status='ACTUAL_P1_CELL_AVERAGE_CONTACT_POINTWISE_TRACE_FAIL' if any(r['positive_pressure_samples_negative_1e_minus8'] for r in results) else 'ACTUAL_P1_POINTWISE_TRACE_DIAGNOSTIC_NO_CERTIFICATE',candidate=d['candidate'],source=ref(src/'summary.json'),verifier=ref(out/'verifier.py'),rows=results,minimum_sampled_gap_mm=min(r['minimum_sampled_gap_mm'] for r in results),positive_pressure_negative_gap_samples=sum(r['positive_pressure_samples_negative_1e_minus8'] for r in results),pointwise_impenetrability_qualified=False,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Actual same-point planar P1 displacement+rigid trace at saved finite-area centroids; no nominal-zero-gap substitution after deformation.','Sampled minima are not continuous gap bounds; common refinement/active local contact refinement still needed. Bolts are average axial branches only,not pointwise head/nut/threads.']))
 print(json.dumps(dict(minimum=min(r['minimum_sampled_gap_mm'] for r in results),negative=sum(r['positive_pressure_samples_negative_1e_minus8'] for r in results))))
if __name__=='__main__':main()
