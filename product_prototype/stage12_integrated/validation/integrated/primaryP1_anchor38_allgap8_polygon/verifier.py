"""Independent common-polygon affine gap audit for actual P1 vertex constraints."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump
from audit_anchor_common38 import polygon,bary

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated'/sys.argv[2];d=json.loads((src/'summary.json').read_text());e=json.loads((REPO/d['local_common_refinement']['path']).read_text());g=json.loads((REPO/d['geometry']['path']).read_text());a=[dict(np.load(REPO/r['path'])) for r in d['fields']]
 for k,b in enumerate(a):
  if 'U' not in b:b['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in d['body_results'][k]['displacement_chunks']])
 ops=np.load(REPO/d['operators']['path']);eq=ops['equality'];scale=np.tile([1,1,1,.01,.01,.01],2);cells=[]
 for patch in e['patches']:
  for cell in patch['cells']:
   nodes=[cell['base_nodes'],cell['receiver_nodes']];x=[b['points_mm'][nd] for b,nd in zip(a,nodes)];axis=int(np.argmin(np.ptp(x[0],axis=0)));xy=[i for i in range(3) if i!=axis];poly=polygon(x[0][:,xy],x[1][:,xy]);area=0.;cent=np.zeros(2)
   for i in range(1,len(poly)-1):
    ar=abs(float(np.cross(poly[i]-poly[0],poly[i+1]-poly[0])))/2;area+=ar;cent+=ar*(poly[0]+poly[i]+poly[i+1])/3
   cent/=area;cols=[];points=[]
   for qp in poly:
    q=np.array(cell['centroid_mm']);q[xy]=qp;cand=[j for j,p in enumerate(g['patches']) if p['label']==patch['label']+'_common_vertex' and np.linalg.norm(np.array(p['exact_CAD_centroid_mm'])-q)<1e-7];assert len(cand)==1;cols.append(cand[0]);points.append(q)
   normal=np.array(g['patches'][cols[0]]['direction']);states=[]
   for row in d['rows']:
    p=np.array(row['contact_forces_N']);w=np.array(row['external_wrench_N_Nmm']);ae=np.array(row['reduced_equality_matrix']);lm=np.array(row['equality_multiplier']);T=ae@np.linalg.pinv(eq*scale[:,None],rcond=1e-10);r=(scale*(T.T@lm)).reshape(2,6);U=[(b['U']@np.r_[p,w if k==0 else -w]).reshape(-1,3) for k,b in enumerate(a)];gaps=[]
    for q in points:
     u=[]
     for k in range(2):u.append(bary(x[k][:,xy],q[xy])@U[k][nodes[k]]+r[k,:3]+np.cross(r[k,3:],q))
     gaps.append(float(normal@(u[0]-u[1])))
    states.append(dict(case=row['case'],vertex_columns=cols,forces_N=p[cols].tolist(),gaps_mm=gaps,minimum_polygon_gap_mm=min(gaps),gap_QP_witness_error_mm=float(abs(np.array(gaps)-np.array(row['contact_gap_mm'])[cols]).max()),force_gap_product_Nmm=float(abs(p[cols]*gaps).max())))
   cells.append(dict(base_nodes=nodes[0],receiver_nodes=nodes[1],polygon_area_mm2=area,reference_area_mm2=cell['area_mm2'],area_relative_error=abs(area/cell['area_mm2']-1),centroid_error_mm=float(np.linalg.norm(cent-np.array(cell['centroid_mm'])[xy])),states=states))
 states=[s for c in cells for s in c['states']];checks=dict(local_partition_area=all(abs(p['uncovered_area_mm2'])<1e-7 for p in e['patches']),independent_polygon_identity=bool(cells) and all(c['area_relative_error']<1e-8 and c['centroid_error_mm']<1e-7 for c in cells),all14_selected_polygon_impenetrability=bool(states) and min(s['minimum_polygon_gap_mm'] for s in states)>-1e-8,independent_gap_witness=bool(states) and max(s['gap_QP_witness_error_mm'] for s in states)<1e-8,local_complementarity=bool(states) and max(s['force_gap_product_Nmm'] for s in states)<1e-8)
 dump(out/'summary.json',dict(status='ACTUAL_P1_SELECTED_COMMON_POLYGON_VERTEX_CONTACT_PASS_LOCAL' if all(checks.values()) else 'ACTUAL_P1_SELECTED_COMMON_POLYGON_VERTEX_CONTACT_FAIL',candidate=d['candidate'],source=ref(src/'summary.json'),verifier=ref(out/'verifier.py'),mathematical_helper=ref(ROOT/'scripts/audit_anchor_common38.py'),checks=checks,cells=cells,minimum_selected_polygon_gap_mm=min(s['minimum_polygon_gap_mm'] for s in states),maximum_gap_witness_error_mm=max(s['gap_QP_witness_error_mm'] for s in states),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Affine gap extrema occur at vertices only for these independently verified planar common polygons. Unchanged remainder cells still average-only.','Discrete FE nodal forces,not source-backed physical contact pressure or head/nut/thread law. No physical external fixture.','No bulk/pressure convergence,globalenergy,operating load or system release certification.']))
 print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
