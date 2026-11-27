"""Independent ray-parity audit and same-reference six-pair guard inventory.

Solid-angle classification is audited with triangle-ray intersections. Whole
solid omitted pairs use interval separation; no adjacent CCD/force PASS implied.
"""
import sys,json,time,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import boundary,Union,closest


def parity(q,tri):
 # Fixed non-axis rays with different irrational directions. A ray near an edge
 # is rejected, not counted twice or silently assigned to one face.
 for direction in [np.array([1.,np.sqrt(2),np.sqrt(3)]),np.array([np.sqrt(5),-1.,np.sqrt(7)]),np.array([-np.sqrt(11),np.sqrt(13),1.])]:
  direction=direction/np.linalg.norm(direction);e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(direction,e2.shape),e2);det=np.einsum('ij,ij->i',e1,h);ok=abs(det)>1e-12;inv=np.zeros(len(tri));inv[ok]=1/det[ok];v=q-tri[:,0];u=inv*np.einsum('ij,ij->i',v,h);cross=np.cross(v,e1);vv=inv*(cross@direction);t=inv*np.einsum('ij,ij->i',e2,cross)
  hits=ok&(u>=-1e-12)&(vv>=-1e-12)&(u+vv<=1+1e-12)&(t>1e-10)
  if np.any(hits&((u<1e-9)|(vv<1e-9)|(u+vv>1-1e-9))):continue
  return int(hits.sum())%2,int(hits.sum())
 return None,0


def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');modelpath=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(modelpath.read_text());sources={};pairs=['frameground','groundbase','motorframe','motorcap','capframe']
 for pair in pairs:sources[pair]=json.loads((ROOT/f'validation/integrated/primaryP1_{pair}_transaction28/summary.json').read_text())
 rootpath=ROOT/'validation/integrated/primaryP1_inactive_certificate27bounded/summary.json';root=json.loads(rootpath.read_text());omittedpath=ROOT/'validation/integrated/primaryP1_omitted_separation28/summary.json';omitted=json.loads(omittedpath.read_text());candidate=model['candidate'];assert all(s['candidate']==candidate for s in [root,omitted,*sources.values()])
 dump(out/'inputs.json',dict(candidate=candidate,fivebody=ref(modelpath),root_guard=ref(rootpath),other_guards={p:ref(ROOT/f'validation/integrated/primaryP1_{p}_transaction28/summary.json') for p in pairs},omitted_separation=ref(omittedpath),producer=ref(out/'producer.py'),guard_operator=ref(ROOT/'scripts/primary_pair_transaction28.py'),scope='Unchanged reference geometry; all sixpair unavailable sample rows. Independent parity tested on every unavailable point, plus positive interior controls. Not a whole support transaction or physical equilibrium.'))
 reports=[];arrays={}
 for mr in model['results']:
  h=mr['mesh_level'];m=np.load(REPO/mr['reference_model']['path']);entries=[];common=min([r['geometry_derived_bound_mm_per_body'] for r in root['results'] if r['mesh_level']==h]+[next(r['tighter_bound_mm_per_body'] for r in s['results'] if r['mesh_level']==h) for s in sources.values()]);total=0;allun=0;originalfail=0;minlower=np.inf
  for pair in ['rootframe',*pairs]:
   if pair=='rootframe':
    us=json.loads((ROOT/'validation/integrated/primaryP1_face_union27/summary.json').read_text());ss=json.loads((ROOT/'validation/integrated/primaryP1_signed_boundary27v2/summary.json').read_text());a=np.load(REPO/us['operator_data']['path']);c=np.load(REPO/ss['chart_data']['path']);q=a[f'h{h}_material_points_mm'];d=a[f'h{h}_distance_mm'];valid=c[f'h{h}_accepted'];owner='OPEN_FRAME'
   else:
    sr=json.loads((ROOT/f'validation/integrated/primaryP1_{pair}_boundary27/summary.json').read_text());a=np.load(REPO/sr['material_ledger']['path']);q=a[f'h{h}_source_material_points_mm'];d=a[f'h{h}_unsigned_distance_mm'];valid=a[f'h{h}_accepted'];owner=sr['results'][0]['owner']
   p=m[owner+'_points_mm'];f=boundary(p,m[owner+'_tetra']);tri=p[f];u=Union(p,f);ids=np.flatnonzero(~valid);outside=np.zeros(len(q),bool);ambiguous=0;maxhits=0
   for k,i in enumerate(ids):
    if k%32==0:assert not(ROOT/'runtime/STOP').exists()
    v,hits=parity(q[i],tri);maxhits=max(maxhits,hits)
    if v is None:ambiguous+=1
    outside[i]=(v==0)
   # Interior positive controls at real tetrahedron centroids must have odd parity.
   t=m[owner+'_tetra'];positive=[parity(x,tri)[0] for x in p[t[np.linspace(0,len(t)-1,12,dtype=int)]].mean(1)]
   exacterrors=[]
   for i in ids[np.linspace(0,len(ids)-1,min(8,len(ids)),dtype=int)]:
    exact=closest(q[i],tri)[0].min();exacterrors.append(abs(exact-d[i]))
   certified=outside&(d-2*common>1e-10);total+=len(q);allun+=len(ids);originalfail+=int(np.sum(d[ids]-.1<=1e-10));minlower=min(minlower,float((d[ids]-2*common).min()));arrays[f'h{h}_{pair}_certified_inactive']=certified
   entries.append(dict(pair=pair,all_rows=len(q),unavailable_rows=len(ids),parity_exterior_rows=int(outside.sum()),ambiguous_ray_rows=ambiguous,interior_positive_controls=positive,max_ray_intersections=maxhits,
    exhaustive_distance_max_error_mm=float(max(exacterrors)),remaining_unresolved_rows=int(np.sum((~valid)&(~certified))),original_05_bound_failed_rows=int(np.sum(d[ids]-.1<=1e-10))))
  reports.append(dict(mesh_level=h,all_material_rows=total,all_original_unavailable_rows=allun,original_05_bound_FAILED_rows=originalfail,common_actual_vertex_bound_mm_per_body=common,minimum_unavailable_next_step_lower_mm=minlower,
   remaining_unavailable_rows_within_common_bound=sum(r['remaining_unresolved_rows'] for r in entries),pairs=entries,accepted_chart_continuation_certified=False,adjacent_fullsurface_coverage_certified=False,physical_load_solve_ready=False))
 np.savez_compressed(out/'all_retained_inactive_masks.npz',**arrays)
 checks=dict(independent_exterior_parity=all(p['ambiguous_ray_rows']==0 and p['parity_exterior_rows']==p['unavailable_rows'] and all(x==1 for x in p['interior_positive_controls']) for r in reports for p in r['pairs']),
  independent_exhaustive_distance=all(p['exhaustive_distance_max_error_mm']<1e-8 for r in reports for p in r['pairs']),all_unavailable_sample_guards_positive=all(r['remaining_unavailable_rows_within_common_bound']==0 and r['minimum_unavailable_next_step_lower_mm']>1e-10 for r in reports),
  original_05_bound_failure_preserved=all(r['original_05_bound_FAILED_rows']>0 for r in reports),omitted_solid_pairs=all(omitted['checks'].values()))
 dump(out/'summary.json',dict(status='ACTUAL_P1_SIXPAIR_SAMPLE_GUARDS_INDEPENDENTLY_AUDITED_NOT_FULL_TRANSACTION' if all(checks.values()) else 'ACTUAL_P1_SIXPAIR_SAMPLE_GUARD_AUDIT_FAIL',candidate=candidate,inputs=ref(out/'inputs.json'),checks=checks,results=reports,masks=ref(out/'all_retained_inactive_masks.npz'),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
 limitations=['No absent Jacobian becomes zero. All unavailable rows remain in original ledger with NaN gaps, no physical pressure. Masks certify only bounded exterior inactivity.',
 'All accepted charts must be recomputed and finite owners checked on trial movement. Full adjacent continuous surfaces and physical coupled sources/Baseanchor remain mandatory.',
 'Common bound is geometry search restriction, not dt or convergence criterion change. Original.05mm/rad, force1e-8N/gap1e-10mm/mesh1%/time.1% unchanged.']))
 print(json.dumps(dict(checks=checks,results=reports)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
