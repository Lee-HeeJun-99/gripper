"""Independent planar triangle intersection and deformed affine-gap extrema.
No producer, FEM assembler or optimizer imports. Only intersection cells whose
full polygons agree with recorded finite areas are qualified locally.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def polygon(a,b):
 # Sutherland-Hodgman in an orthogonal plane; no BRep intersection reuse.
 orient=np.cross(b[1]-b[0],b[2]-b[0]);out=list(a)
 for v,w in zip(b,np.roll(b,-1,axis=0)):
  old=out;out=[]
  for p,q in zip(old,old[1:]+old[:1]):
   dp=float(np.cross(w-v,p-v))*np.sign(orient);dq=float(np.cross(w-v,q-v))*np.sign(orient)
   if dp>=-1e-12:out.append(p)
   if dp*dq<0:out.append(p+(q-p)*dp/(dp-dq))
  if not out:break
 return np.array(out)
def bary(x,q):
 z=np.linalg.solve(np.column_stack([x[1]-x[0],x[2]-x[0]]),q-x[0]);return np.r_[1-z.sum(),z]
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated'/sys.argv[2];d=json.loads((src/'summary.json').read_text());e=json.loads((REPO/d['local_common_refinement']['path']).read_text());g=json.loads((REPO/d['geometry']['path']).read_text());a=[dict(np.load(REPO/r['path'])) for r in d['fields']]
 for k,b in enumerate(a):
  if 'U' not in b:b['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in d['body_results'][k]['displacement_chunks']])
 ops=np.load(REPO/d['operators']['path']);eq=ops['equality'];scale=np.tile([1,1,1,.01,.01,.01],2);cells=[];cursor=0
 for patch in e['patches']:
  for cell in patch['cells']:
   # Match exact cell by common label/area/centroid and single support triangle.
   cand=[j for j,p in enumerate(g['patches']) if p['label']==patch['label']+'_common' and abs(p['exact_CAD_area_mm2']-cell['area_mm2'])<1e-8 and np.linalg.norm(np.array(p['exact_CAD_centroid_mm'])-cell['centroid_mm'])<1e-7];assert len(cand)==1;j=cand[0]
   normal=np.array(g['patches'][j]['direction']);ax=int(np.argmax(abs(normal)));xy=[i for i in range(3) if i!=ax];nodes=[cell['base_nodes'],cell['receiver_nodes']];x=[b['points_mm'][nd] for b,nd in zip(a,nodes)];poly=polygon(x[0][:,xy],x[1][:,xy]);area=0.;cent=np.zeros(2)
   for i in range(1,len(poly)-1):
    ar=abs(float(np.cross(poly[i]-poly[0],poly[i+1]-poly[0])))/2;area+=ar;cent+=ar*(poly[0]+poly[i]+poly[i+1])/3
   cent/=area;delta=abs(area/cell['area_mm2']-1);cen=float(np.linalg.norm(cent-np.array(cell['centroid_mm'])[xy]));states=[]
   for row in d['rows']:
    p=np.array(row['contact_forces_N']);w=np.array(row['external_wrench_N_Nmm']);ae=np.array(row['reduced_equality_matrix']);lm=np.array(row['equality_multiplier']);T=ae@np.linalg.pinv(eq*scale[:,None]);r=(scale*(T.T@lm)).reshape(2,6);U=[(b['U']@np.r_[p,w if k==0 else -w]).reshape(-1,3) for k,b in enumerate(a)];gaps=[]
    for qp in poly:
     q=np.zeros(3);q[xy]=qp;q[ax]=cell['centroid_mm'][ax];u=[]
     for k in range(2):u.append(bary(x[k][:,xy],qp)@U[k][nodes[k]]+r[k,:3]+np.cross(r[k,3:],q))
     gaps.append(float(normal@(u[0]-u[1])))
    states.append(dict(case=row['case'],force_N=float(p[j]),pressure_MPa=row['pressures_MPa'][j],average_gap_mm=row['contact_gap_mm'][j],minimum_polygon_vertex_gap_mm=min(gaps),maximum_polygon_vertex_gap_mm=max(gaps),positive_pressure_negative_vertex=bool(p[j]>1e-9 and min(gaps)<-1e-8)))
   cells.append(dict(column=j,label=patch['label'],polygon_vertices_mm=poly.tolist(),full_triangle_intersection_area_mm2=area,recorded_common_cell_area_mm2=cell['area_mm2'],relative_area_error=delta,centroid_error_mm=cen,polygon_domain_identity=delta<1e-8 and cen<1e-7,states=states))
 checks=dict(local_common_partition_area=all(abs(p['uncovered_area_mm2'])<1e-7 for p in e['patches']),independent_polygon_area_centroid=bool(cells) and all(c['polygon_domain_identity'] for c in cells))
 negative=sum(s['positive_pressure_negative_vertex'] for c in cells for s in c['states']);minimum=min(s['minimum_polygon_vertex_gap_mm'] for c in cells for s in c['states'])
 dump(out/'summary.json',dict(status='ACTUAL_P1_LOCAL_COMMON_REFINEMENT_GEOMETRY_PASS_POINTWISE_CONTACT_FAIL' if all(checks.values()) and negative else 'ACTUAL_P1_COMMON_REFINEMENT_AUDIT_REVIEW_REQUIRED',candidate=d['candidate'],source=ref(src/'summary.json'),verifier=ref(out/'verifier.py'),checks=checks,cells=cells,minimum_local_polygon_gap_mm=minimum,positive_pressure_negative_vertex_states=negative,all_affine_polygon_vertex_gaps_nonnegative=minimum>=-1e-8,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Polygon area/centroid independent check tests selected common regions,not whole curved contact domain.','P0 force nonnegative and average complementarity do not enforce pointwise affine gap;vertex violations explicitly retained.','Conditional signed source and nominal axial springs unchanged;no physical fixture/material/globalenergy certification.']))
 print(json.dumps(dict(checks=checks,cells=len(cells),minimum=minimum,negative=negative)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
