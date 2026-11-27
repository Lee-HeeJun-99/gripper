"""Actual unloaded end traction and curved-BRep/facet mismatch witnesses.
Explicitly excludes prescribed source-loaded portions of Front/Rail end faces.
No producer/assembler/solver import; no pointwise boundary PASS from weak KKT.
"""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump,S1
from verify_finite_body34 import independent_eps,sigma
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(sp.read_text());cad=json.loads((REPO/s['candidate']['path']).read_text());gp=ROOT/'validation/integrated/primaryP1_gamma_attachment29/pin_hole_geometry.json';geo=json.loads(gp.read_text());dump(out/'inputs.json',dict(candidate=s['candidate'],source=ref(sp),geometry=ref(gp),producer=ref(out/'producer.py'),independent_gradient=ref(ROOT/'scripts/verify_finite_body34.py')));results=[]
 for row in s['results']:
  assert not(ROOT/'runtime/STOP').exists();a=np.load(REPO/row['fields']['path']);p=a['points_mm'];t=a['tetra'];tri=a['boundary_triangles'];part=row['part'];E=row['conditional_E_MPa'];nu=row['conditional_nu'];M=a['F'].shape[1];dx=p[t[:,1:]]-p[t[:,0,None]];inv=np.linalg.inv(dx);fields=[]
  for key in ['UF','VFE']:
   v=a[key].reshape(len(p),3,M);du=v[t[:,1:]]-v[t[:,0,None]];gr=np.einsum('tij,tjkm->tkim',inv,du).transpose(0,3,1,2);fields.append((gr+gr.swapaxes(2,3))/2)
  end=48.5 if part=='F0_ROOT_BACK' else (50. if part=='F0_ROOT_FRONT' else 50.3);free=tri[np.all(abs(p[tri,0]-end)<1e-8,axis=1)&np.all(p[tri,2]<3-1e-9,axis=1)];need={tuple(sorted(v)) for v in free};owner={}
  for i,tt in enumerate(t):
   for face in [tt[[1,2,3]],tt[[0,2,3]],tt[[0,1,3]],tt[[0,1,2]]]:
    key=tuple(sorted(face))
    if key in need:owner[key]=i
  fe=[];en=[];area=[]
  for tr in free:
   tid=owner[tuple(sorted(tr))];pt=p[tr].mean(0);epsH=independent_eps(pt[None],a['centers_mm'],a['directions'],E,nu)[0];combined=fields[1][tid]+np.einsum('kij,km->mij',epsH,a['alpha']);fe.append(np.linalg.norm(sigma(fields[0][tid],E,nu)[:,:,0],axis=1));en.append(np.linalg.norm(sigma(combined,E,nu)[:,:,0],axis=1));area.append(np.linalg.norm(np.cross(p[tr[1]]-p[tr[0]],p[tr[2]]-p[tr[0]]))/2)
  fe=np.array(fe);en=np.array(en);area=np.array(area);j=json.loads((REPO/row['quadrature']['path']).read_text());errors=[]
  for q in j:
   if q['kind']!='conditional_contact_patch':continue
   g=geo[q['global_port']];R=1 if part=='F0_ROOT_BACK' else 1.05;yc,zc=g['pin']['axis_point_mm'][1:];pt=np.array(q['point_mm']);errors.append(abs(np.linalg.norm(pt[1:]-[yc,zc])-R))
  witnesses=[]
  if part=='F0_ROOT_BACK':
   shape=read(REPO/row['part_reference']['path'])
   for yc in [-10.,10.]:
    for depth in [.02,.1,.5]:
     point=np.array([48.5,yc+1-depth,1.]);dist=BRepExtrema_DistShapeShape(shape,BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex());dist.Perform();matches=[]
     for tr in free:
      pts=p[tr,1:];v=np.linalg.solve(np.column_stack([pts[1]-pts[0],pts[2]-pts[0]]),point[1:]-pts[0]);bc=np.r_[1-v.sum(),v]
      if bc.min()>-1e-9:matches.append(owner[tuple(sorted(tr))])
     assert matches,(part,point);vals=[]
     eh=independent_eps(point[None],a['centers_mm'],a['directions'],E,nu)[0]
     for tid in set(matches):vals.append(np.linalg.norm(sigma(fields[1][tid]+np.einsum('kij,km->mij',eh,a['alpha']),E,nu)[:,:,0],axis=1).tolist())
     witnesses.append(dict(unseated_actual_Root_tip_point_mm=point.tolist(),actual_BRep_point_distance_mm=dist.Value(),adjacent_FE_stress_traces_MPa_per_unit_N=vals,required_unloaded_traction=[0,0,0],pointwise_boundary_qualified=False))
  results.append(dict(part=part,unloaded_end_faces=len(free),source_loaded_faces_excluded=True,unloaded_region='actual end x='+str(end)+'; all triangle vertices z<3mm excludes conditional source z>=3mm',FE_only_unloaded_traction_L2_MPa_sqrt_mm2_per_unit_N=np.sqrt(np.sum(fe**2*area[:,None],axis=0)).tolist(),enriched_unloaded_traction_L2_MPa_sqrt_mm2_per_unit_N=np.sqrt(np.sum(en**2*area[:,None],axis=0)).tolist(),enriched_unloaded_max_traction_MPa_per_unit_N=float(en.max()),maximum_contact_facet_radial_error_mm=max(errors),minimum_contact_facet_radial_error_mm=min(errors),root_actual_tip_witnesses=witnesses,pointwise_boundary_qualified=False,actual_continuous_contact_qualified=False))
 checks=dict(all4actual_bodies=len(results)==4,unloaded_end_samples_exist=all(r['unloaded_end_faces']>0 for r in results),nonzero_unloaded_end_traction_retained=all(r['enriched_unloaded_max_traction_MPa_per_unit_N']>1e-8 for r in results),actual_Root_tip_BRep_membership=all(w['actual_BRep_point_distance_mm']<1e-8 for r in results for w in r['root_actual_tip_witnesses']),curved_facet_error_recorded=all(r['maximum_contact_facet_radial_error_mm']>0 for r in results))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_END_AND_CURVED_BOUNDARY_UNQUALIFIED',candidate=s['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=results,accepted_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,correction='Producer Front/Rail raw end trace included conditional source-loaded faces: it is NOT a free-boundary residual. This new audit explicitly excludes source z>=3mm. Producer traces retained unchanged. Root free-tip was already unloaded.',limitations=['Neumann Ritz operator satisfies only discrete variational equations. Nonzero unloaded-end stress traces and faceted contact geometry prevent pointwise traction/contact acceptance.','This is conditional unit-patch/source sensitivity, NOT a coupled fourport load split, 100g demand, actual strength, fullsourcefield or globalenergy result. E/nu remain conditional. Kelvin analytic sources are not physical forces.']))
 print(json.dumps(dict(checks=checks,results=results)))
if __name__=='__main__':main()
