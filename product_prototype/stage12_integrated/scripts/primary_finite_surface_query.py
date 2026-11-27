"""Actual P1 full deformed tetra-boundary closest-point contrast.
All original2169row identities retained; NO solve, constraint deletion or CAD
change. Signed closest surface geometry does not certify a normal cone or CCD.
"""
import sys,json,shutil,time
import numpy as np
from scipy.spatial.transform import Rotation
from skfem import MeshTet
from baseline_registry import ROOT,REPO,ref,sha,dump

def closest(q,x,tri,normals):
 a=x[tri[:,0]];e=x[tri[:,1]]-a;f=x[tri[:,2]]-a;d=q-a;aa=np.sum(e*e,1);bb=np.sum(e*f,1);cc=np.sum(f*f,1);de=np.sum(d*e,1);df=np.sum(d*f,1);den=aa*cc-bb*bb;s=(cc*de-bb*df)/den;t=(aa*df-bb*de)/den;ok=(s>=0)&(t>=0)&(s+t<=1);point=a+s[:,None]*e+t[:,None]*f;weights=np.c_[1-s-t,s,t];dist2=np.sum((q-point)**2,1);dist2[~ok]=np.inf;feature=np.full(len(tri),0)
 for i in range(3):
  edge=x[tri[:,(i+1)%3]]-x[tri[:,i]];v=np.clip(np.sum((q-x[tri[:,i]])*edge,1)/np.sum(edge*edge,1),0,1);cp=x[tri[:,i]]+v[:,None]*edge;dd=np.sum((q-cp)**2,1);better=dd<dist2;dist2[better]=dd[better];point[better]=cp[better];weights[better]=0;weights[better,i]=1-v[better];weights[better,(i+1)%3]=v[better];feature[better]=i+1
 k=int(np.argmin(dist2));delta=q-point[k];distance=float(np.sqrt(max(dist2[k],0)));sign=1 if delta@normals[k]>=0 else -1;gradient=sign*delta/max(distance,1e-300) if distance>1e-12 else normals[k];return dict(gap_mm=sign*distance,triangle=int(k),point_mm=point[k],weights=weights[k],gradient=gradient,feature=int(feature[k]),distance_mm=distance)

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated/primaryP1_local_surface2/summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['source_field']['path']);b=np.load(REPO/s['output']['path']);u=b['u_mm'];mo=int(a['motor_offset']);data={};surfaces={}
 for n in s['elastic_bodies']:
  X=a[n+'_points_mm'];tet=a[n+'_tetra'];o=int(a[n+'_offset']);x=X+u[o:o+3*len(X)].reshape(-1,3);m=MeshTet(X.T,tet.T);fi=m.boundary_facets();tri=m.facets[:,fi].T;parents=m.f2t[0,fi];centroid=x[tet[parents]].mean(1);normal=np.cross(x[tri[:,1]]-x[tri[:,0]],x[tri[:,2]]-x[tri[:,0]]);normal*=np.sign(np.sum(normal*(x[tri].mean(1)-centroid),1))[:,None];normal/=np.linalg.norm(normal,axis=1)[:,None];surfaces[n]=dict(x=x,tri=tri,normal=normal);data[n]=dict(X=X,o=o)
 desc=json.loads((ROOT/'validation/integrated/primaryP1_corotated_support1/summary.json').read_text());owners={r['label']:r['owner'] for r in desc['contact_groups']};pressure=a['contact_force_N'];gaps=[];grad=[];closest_points=[];weights=[];tids=[];features=[];queries=[];controls=[];row_descriptions=[]
 for label in np.unique(a['contact_label']):
  ids=np.flatnonzero(a['contact_label']==label);owner=owners[str(label)];S=surfaces[owner];first='Motor' if str(label).startswith('motor_') else ('F0_ROOT_BACK' if str(label).startswith('root_') else ('OPEN_FRAME' if str(label).startswith('frame_') else 'GROUND_PLATE'));lookup=None
  if first!='Motor':lookup={tuple(np.round(v,7)):j for j,v in enumerate(data[first]['X'])}
  for row in ids:
   q=a['contact_points_mm'][row]
   if first=='Motor':q=(q-[0,0,20])@Rotation.from_rotvec(u[mo+3:mo+6]).as_matrix().T+[0,0,20]+u[mo:mo+3]
   else:q=surfaces[first]['x'][lookup[tuple(np.round(q,7))]]
   c=closest(q,S['x'],S['tri'],S['normal']);queries.append(q);gaps.append(c['gap_mm']);grad.append(c['gradient']);closest_points.append(c['point_mm']);weights.append(c['weights']);tids.append(c['triangle']);features.append(c['feature']);row_descriptions.append(dict(original_row=int(row),label=str(label),owner=owner,first=first))
   # Positive-distance edge/corner witnesses independently expose old infinite
   # plane support. Freeze owner here; check nearest-point envelope derivative
   # without crossing the active feature, with fixed 1e-8 derivative criterion.
   if pressure[row]>1e-8 and c['distance_mm']>1e-5 and c['feature']!=0 and len(controls)<12:
    h=min(c['distance_mm']*.001,1e-5);fd=[]
    for e in np.eye(3):fd.append((closest(q+h*e,S['x'],S['tri'],S['normal'])['gap_mm']-closest(q-h*e,S['x'],S['tri'],S['normal'])['gap_mm'])/(2*h))
    controls.append(dict(row=int(row),gap_mm=c['gap_mm'],old_pressure_N=float(pressure[row]),feature=c['feature'],gradient=c['gradient'].tolist(),finite_difference=fd,max_error=float(np.max(abs(np.array(fd)-c['gradient'])))))
 order=np.argsort([r['original_row'] for r in row_descriptions]);gaps=np.array(gaps)[order];grad=np.array(grad)[order];cp=np.array(closest_points)[order];weights=np.array(weights)[order];tids=np.array(tids)[order];features=np.array(features)[order];queries=np.array(queries)[order];rows=[row_descriptions[j] for j in order];positive=(gaps>1e-8)&(pressure>1e-8);penetrating=(gaps<-1e-8);groups=[]
 for label in np.unique(a['contact_label']):
  ids=np.flatnonzero(a['contact_label']==label);groups.append(dict(label=str(label),rows=len(ids),positive_gap_with_old_pressure=int(positive[ids].sum()),penetrations_below_minus1e8=int(penetrating[ids].sum()),old_pressure_on_positive_gap_N=float(pressure[ids][positive[ids]].sum()),min_gap_mm=float(gaps[ids].min()),max_gap_mm=float(gaps[ids].max()),complementarity_Nmm=float(np.max(abs(gaps[ids]*pressure[ids])))))
 checks=dict(all2169rows=len(gaps)==2169,all_source_parts=len(s['elastic_bodies'])==5,barycentric_sum=float(np.max(abs(weights.sum(1)-1)))<1e-12,finite_simplex_weights=float(weights.min())>=-1e-12,actual_point_reconstruction=True,edge_work_derivative=len(controls)>=3 and max(r['max_error'] for r in controls)<1e-8)
 for i,r in enumerate(rows):
  S=surfaces[r['owner']];checks['actual_point_reconstruction'] &= bool(np.linalg.norm(weights[i]@S['x'][S['tri'][tids[i]]]-cp[i])<1e-10)
 np.savez_compressed(out/'finite_surface.npz',gap_mm=gaps,first_points_mm=queries,closest_points_mm=cp,normal_gradient=grad,barycentric_weights=weights,owner_triangle=tids,features=features,old_pressure_N=pressure)
 dump(out/'rows.json',rows)
 result=dict(status='ACTUAL_P1_FINITE_SURFACE_OLD_CONTACT_STATE_REJECTED' if all(checks.values()) else 'ACTUAL_P1_FINITE_SURFACE_QUERY_CHECK_FAIL',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],producer=ref(out/'producer.py'),output=ref(out/'finite_surface.npz'),rows=ref(out/'rows.json'),checks={k:bool(v) for k,v in checks.items()},contact_rows=len(gaps),positive_gap_with_old_pressure=int(positive.sum()),penetrations_below_minus1e8=int(penetrating.sum()),minimum_gap_mm=float(gaps.min()),maximum_gap_mm=float(gaps.max()),maximum_complementarity_Nmm=float(np.max(abs(gaps*pressure))),old_pressure_on_positive_gap_N=float(pressure[positive].sum()),groups=groups,edge_work=controls,contact_update_attempted=False,new_equilibrium_solved=False,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Full finite currenttetboundary nearestpoint,not infiniteplane. Existing coarse mesh/conditional deformation,not continuousCADsurface/CCD/finitewire.', 'Signs use oriented nearestfacet; edges/vertices/nonsmooth ties need normalcone and independent inside/outside check before a contactsolve. Positive-gap/pressure and penetration cannot be fixed by deleting rows or transferring oldpressures.', 'Onlyfirst-point distance derivatives on separatededgewitnesses checked. No fullowner/activefeature/movingpoint pullback verified here; no equilibrium/stress/mesh/globalenergy/full3Finger/physicalanchorPASS.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
