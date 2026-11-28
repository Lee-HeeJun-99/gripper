"""Independent original tetra and COMPLETE clipped plug facet gap audit.
Node/contact law verification stays separate from all-facet nonpenetration.
"""
import sys,json,shutil,math
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_keeper_coupled71 import faces,rot
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane

def clip(poly,z,above):
 result=[]
 if not len(poly):return result
 old=poly[-1];oi=(old[2]>=z) if above else (old[2]<=z)
 for new in poly:
  ni=(new[2]>=z) if above else (new[2]<=z)
  if ni!=oi:
   f=(z-old[2])/(new[2]-old[2]);result.append(old+f*(new-old))
  if ni:result.append(new)
  old=new;oi=ni
 return result

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[]
 for tag in sys.argv[2:]:
  sp=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(sp.read_text());cp=REPO/s['candidate']['path'];assert sha(cp)==s['candidate']['SHA256'];cad=json.loads(cp.read_text());f=REPO/s['field']['path'];assert sha(f)==s['field']['SHA256'];a=np.load(f);p=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];F=a['load_N'];ids=a['contact_node'];which=a['bolt_index'];norm=a['normal'];lam=a['normal_force_N'];xyz=p[t];mat=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2);iv=np.linalg.inv(mat);grad=iv[:,1:,:].transpose(0,2,1);vol=abs(np.linalg.det(mat))/6;G=np.einsum('tai,taj->tij',u[t],grad);strain=(G+G.transpose(0,2,1))/2;E=s['E_ASSUMED_MPa'];nu=s['nu_ASSUMED'];mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));stress=2*mu*strain+la*np.trace(strain,axis1=1,axis2=2)[:,None,None]*np.eye(3);element=np.einsum('tij,taj,t->tai',stress,grad,vol);internal=np.zeros_like(u)
  for j in range(4):np.add.at(internal,t[:,j],element[:,j])
  energy=float(np.sum(.5*np.einsum('tij,tij->t',strain,stress)*vol));pullback=np.zeros_like(F)
  for j in range(3):np.add.at(pullback[:,j],ids,lam*norm[:,j])
  bad=F.copy();bad[0,2]+=.01;forceerr=float(abs(internal-F).max());pb=float(abs(pullback-F).max());angle=np.array(s['bolt_reference_spin_rad'])+a['bolt_spin_increment_rad'];settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];allfacets=[];torqueres=[]
  for i,q in enumerate(settings):
   center=np.array([q['x'],q['y'],0.]);R=rot(angle[i]);dz=.5*angle[i]/(2*np.pi);walls=[]
   for face in faces(read(REPO/cad['part_references'][q['bolt']]['path'])):
    ad=BRepAdaptor_Surface(face)
    if ad.GetType()!=GeomAbs_Plane:continue
    pl=ad.Plane();o=pl.Location();axis=pl.Axis().Direction();o=np.array([o.X(),o.Y(),o.Z()]);n=np.array([axis.X(),axis.Y(),axis.Z()]);bb=bounds(face)
    if abs(n[2])<1e-7 and np.linalg.norm((np.array(bb[:3])+bb[3:])[:2]/2-center[:2])<2:
     if n@(center-o)<0:n=-n
     walls.append((R@(o-center)+center+[0,0,dz],R@n))
   assert len(walls)==6;tris=a['boundary_triangles'];eligible=tris[np.all(np.linalg.norm(p[tris,:2]-center[:2],axis=2)<1.6,axis=1)&np.any(p[tris,2]<dz+.01,axis=1)];minima=[];tested=0;worst=None
   for tr in eligible:
    poly=clip(list((p+u)[tr]),-1.3+dz,True);poly=clip(poly,dz,False)
    if not len(poly):continue
    points=np.array(poly);gaps=np.array([np.sum((points-o)*n,axis=1) for o,n in walls]);g=float(gaps.min());minima.append(g);tested+=len(poly)
    if worst is None or g<worst['gap_mm']:
     w,vertex=np.unravel_index(np.argmin(gaps),gaps.shape);worst=dict(gap_mm=g,original_triangle_nodes=tr.tolist(),point_mm=points[vertex].tolist(),wall_index=int(w))
   mask=which==i;ff=-lam[mask,None]*norm[mask];moment=np.cross((p+u)[ids[mask]]-center,ff).sum(0);torqueres.append(float(moment[2]+s['conditional_bolt_torque_Nmm'][i]));allfacets.append(dict(bolt=q['bolt'],finite_axial_socket_interval_mm=[-1.3+dz,dz],eligible_original_triangles=len(eligible),clipped_triangle_count=len(minima),tested_exact_clipped_polygon_vertices=tested,minimum_full_faceted_surface_gap_mm=min(minima),violating_clipped_triangles=sum(v<-1e-9 for v in minima),original_nonpenetration_1e9_pass=min(minima)>=-1e-9,worst=worst))
  checks=dict(all_original_tetra_force=forceerr<1e-8,physical_contact_Btranspose=pb<1e-12,independent_element_energy=abs(energy/s['static_energy_Nmm']-1)<1e-8,local_elastic_halfwork=abs(.5*float(np.sum(u*F))/energy-1)<1e-8,bolt_free_spin_balance=max(abs(np.array(torqueres)))<1e-8,nonnegative_normals=float(lam.min())>=-1e-9,contact_node_gap=float(a['gap_mm'].min())>=-1e-9,complementarity=float(abs(lam*a['gap_mm']).max())<1e-8,altered_original_zload_rejected=float(abs(internal-bad).max())>.009)
  rms=float(np.sqrt(np.sum(vol[:,None]*(u[t].sum(1)**2+np.sum(u[t]**2,axis=1)))/(20*vol.sum())));rows.append(dict(source=ref(sp),field=ref(f),checks={k:bool(v) for k,v in checks.items()},original_force_residual_N=forceerr,pullback_force_error_N=pb,independent_energy_Nmm=energy,volume_RMS_mm=rms,all_clipped_facets=allfacets,whole_faceted_interface_pass=all(q['original_nonpenetration_1e9_pass'] for q in allfacets),node_pass_is_not_whole_surface_pass=True))
 comparisons=[]
 for i,b in enumerate(rows):
  for c in rows[i+1:]:
   aa=np.load(REPO/b['field']['path']);bb=np.load(REPO/c['field']['path']);same=np.array_equal(aa['points_mm'],bb['points_mm']) and np.array_equal(aa['tetra'],bb['tetra']);comparisons.append(dict(first=b['source'],second=c['source'],same_mesh=same,relative_energy_difference=abs(b['independent_energy_Nmm']-c['independent_energy_Nmm'])/c['independent_energy_Nmm'],same_mesh_maximum_displacement_difference_mm=float(abs(aa['displacement_mm']-bb['displacement_mm']).max()) if same else None))
 passed=all(all(r['checks'].values()) for r in rows);whole=all(r['whole_faceted_interface_pass'] for r in rows);dump(out/'summary.json',dict(status='ACTUAL_P1_KEEPER_TETRA_CONTACT_VERIFIED_FULL_FACET_RESULT_SEPARATE' if passed else 'ACTUAL_P1_KEEPER_INDEPENDENT_TETRA_FAIL',producer=ref(out/'producer.py'),candidate=s['candidate'],rows=rows,same_mesh_solver_comparisons=comparisons,independent_original_DOF_verification_pass=passed,whole_faceted_interface_nonpenetration_pass=whole,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Completeclippedlinearboundarytriangle test usesactualposedconvexhexsideplanes and exact axial clipping; curvedSTEPfacetdomain andelasticlaw accuracy remainseparate.','Even fullfacetnonpenetration doesnotcertify quadratureconvergence/elasticpressure uniqueness/sourcecapacity or fullhost/pin/nut/cage equilibrium.','Localhalfwork isnot movingboundary/globalenergystoredclosure.']));print(json.dumps(dict(tetra_pass=passed,whole_facets_pass=whole,rows=rows,comparisons=comparisons)));return 0 if passed else 2
if __name__=='__main__':sys.exit(main())
