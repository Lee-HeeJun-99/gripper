"""Independent finite-material contact IFT, both cones and physical field audit."""
import sys,json,shutil,time
import numpy as np
from scipy.optimize import nnls
from skfem import MeshTet
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
from primary_keeper_coupled71 import faces,pointdist
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.TopAbs import TopAbs_REVERSED
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_shoulder73a/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);host=read(REPO/cad['part_references']['F0_ROOT_BACK']['path']);hostfaces=[]
 for face in faces(host):
  ad=BRepAdaptor_Surface(face)
  if ad.GetType()==GeomAbs_Plane:
   n=ad.Plane().Axis().Direction();n=np.array([n.X(),n.Y(),n.Z()])*(-1 if face.Orientation()==TopAbs_REVERSED else 1);hostfaces.append((face,n))
 rows=[];data=[]
 for tag in sys.argv[2:]:
  root=ROOT/'validation/integrated'/tag;d=json.loads((root/'summary.json').read_text());a=np.load(root/'field.npz');p=a['points_mm'];t=a['tetra'];tri=a['boundary_triangles'];u=a['displacement_mm'];pos=p+u;f=a['gravity_nodal_force_N'];c=a['contact_nodal_force_N'];lam=a['normal_force_N'];pts=a['contact_points_mm'];features=json.loads((root/'contact_features.json').read_text());pulled=np.zeros_like(p);active=[];directionerr=[]
  requested={tuple(sorted(map(int,tr))) for tr in tri};opposite={}
  for tet in t:
   for omit in range(4):
    key=tuple(sorted(int(tet[j]) for j in range(4) if j!=omit))
    if key in requested:opposite[key]=int(tet[omit])
  normals={}
  for tr in tri:
   xyz=pos[tr];n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);n*=(-1 if n@(pos[opposite[tuple(sorted(map(int,tr)))]]-xyz.mean(0))>0 else 1);n/=np.linalg.norm(n)
   for nd in tr:normals.setdefault(int(nd),[]).append(-n)
  for i,q in enumerate(features):
   nd=np.array(q['triangle']);b=np.array(q['barycentric']);xyz=pos[nd];pt=b@xyz;support=np.flatnonzero(abs(b)>1e-9);g=np.array([0.,0.,1.])
   if len(support)==2:
    edge=xyz[support[1]]-xyz[support[0]];axes=[j for j in [0,1] if any(abs(pt[j]-bound)<1e-9 for bound in ([57,58.95,61.05,63] if j==0 else [-2,-1.05,1.05,2])) and abs(edge[j])>1e-12]
    assert axes;ax=axes[0];g[ax]=-edge[2]/edge[ax]
   elif len(support)==3:
    n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);g=n/n[2]
   for node,w in zip(nd,b):pulled[node]+=lam[i]*w*g
   if lam[i]<=1e-9:continue
   # Keeper cone at material vertex/edge/interior, not all normals at unrelated vertices.
   if len(support)==1:kn=np.array(normals[int(nd[support[0]])]).T
   elif len(support)==2:
    edgeids=set(nd[support]);ns=[]
    for tr in tri:
     if edgeids.issubset(set(tr)):
      v=pos[tr];n=np.cross(v[1]-v[0],v[2]-v[0]);n*=(-1 if n@(pos[opposite[tuple(sorted(map(int,tr)))]]-v.mean(0))>0 else 1);ns.append(-n/np.linalg.norm(n))
    kn=np.array(ns).T
   else:
    n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);kn=(n*np.sign(n[2])/np.linalg.norm(n))[:,None]
   hn=np.array([n for face,n in hostfaces if pointdist(face,pt)<1e-7]).T
   ke=nnls(kn,g,maxiter=1000)[1]/np.linalg.norm(g);he=nnls(hn,g,maxiter=1000)[1]/np.linalg.norm(g) if hn.size else 1.
   active.append(dict(row=i,point_mm=pt.tolist(),lambda_N=float(lam[i]),Root_distance_mm=pointdist(host,pt),keeper_cone_residual=float(ke),Root_cone_residual=float(he),material_support_nodes=len(support),gradient=g.tolist()))
  mat=np.concatenate([np.ones((len(t),4,1)),p[t]],axis=2);iv=np.linalg.inv(mat);grad=iv[:,1:,:].transpose(0,2,1);vol=abs(np.linalg.det(mat))/6;DG=np.einsum('tai,taj->tij',u[t],grad);FG=DG+np.eye(3);eps=(FG.transpose(0,2,1)@FG-np.eye(3))/2;mu=200000/2.6;la=200000*.3/(1.3*.4);stress=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);ef=np.einsum('tij,taj,t->tai',FG@stress,grad,vol);internal=np.zeros_like(p)
  for j in range(4):np.add.at(internal,t[:,j],ef[:,j])
  energy=float(np.sum(.5*stress*eps*vol[:,None,None]));wrench=np.r_[(f+c).sum(0),np.cross(pos-[60,0,-1],f+c).sum(0)]
  def physical(uu):
   FF=np.eye(3)+np.einsum('tai,taj->tij',uu[t]-uu[t[:,0,None]],grad);EE=(FF.transpose(0,2,1)@FF-np.eye(3))/2;SS=2*mu*EE+la*np.trace(EE,axis1=1,axis2=2)[:,None,None]*np.eye(3);ef=np.einsum('tij,taj,t->tai',FF@SS,grad,vol);ff=np.zeros_like(uu)
   for jj in range(4):np.add.at(ff,t[:,jj],ef[:,jj])
   return ff,np.sum(.5*SS*EE*vol[:,None,None])
  rng=np.random.default_rng(7401);direction=rng.normal(size=u.shape);fc,ec=physical(u.astype(complex)+1e-20j*direction);gradienterror=float(abs(ec.imag/1e-20-np.sum(internal*direction)));angle=.173;rot=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]]);ur=(p.astype(np.longdouble)+u.astype(np.longdouble))@rot.astype(np.longdouble).T+np.array([.2,-.3,.1],dtype=np.longdouble)-p.astype(np.longdouble);fr,er=physical(ur);rotationforce=float(abs(fr-internal@rot.T).max());rotationenergy=float(abs(er/energy-1))
  checks=dict(independent_energy_gradient=gradienterror<1e-8,independent_rigidrotation_force=rotationforce<1e-8,independent_rigidrotation_energy=rotationenergy<1e-6,independent_material_trim_force=float(abs(pulled-c).max())<1e-12,independent_element_force=float(abs(internal-c-f).max())<1e-8,independent_element_energy=abs(energy-d['static_energy_Nmm'])<1e-12,deformed_wrench=float(abs(wrench).max())<1e-8,active_points_on_actual_Root=all(q['Root_distance_mm']<1e-7 for q in active),both_physical_normalcones=all(max(q['keeper_cone_residual'],q['Root_cone_residual'])<1e-8 for q in active),altered_gravity_rejected=float(abs(internal-c-1.01*f).max())>1e-8,source_checks=all(d['checks'].values()))
  rows.append(dict(source=ref(root/'summary.json'),checks={k:bool(v) for k,v in checks.items()},nodes=len(p),tetra=len(t),energy_Nmm=energy,energy_gradient_error_N=gradienterror,rigid_rotation_force_error_N=rotationforce,rigid_rotation_energy_relative_error=rotationenergy,force_residual_N=float(abs(internal-c-f).max()),material_trim_pullback_error_N=float(abs(pulled-c).max()),deformed_wrench_N_Nmm=wrench.tolist(),maximum_Root_distance_mm=max(q['Root_distance_mm'] for q in active),active_contacts=active));data.append((p,t,u,iv,vol))
 # Deterministic full-volume quadrature on finest tetra: report EVERY unmapped point.
 # A missing point is a domain mismatch and blocks whole-domain comparison.
 p,t,u,iv,vol=data[-1];probes=p[t].mean(1);vectors=[];unmapped=[]
 for pp,tt,uu,ii,vv in data:
  finder=MeshTet(pp.T,tt.T).element_finder();ids=np.full(len(probes),-1)
  for first in range(0,len(probes),200):
   assert not(ROOT/'runtime/STOP').exists()
   try:ids[first:first+200]=finder(*probes[first:first+200].T)
   except ValueError:
    for k in range(first,min(first+200,len(probes))):
     try:ids[k]=finder(*probes[k:k+1].T)[0]
     except ValueError:pass
  valid=ids>=0;val=np.full((len(probes),3),np.nan);bb=np.einsum('pi,pij->pj',np.c_[np.ones(valid.sum()),probes[valid]],ii[ids[valid]]);val[valid]=np.einsum('pa,pai->pi',bb,uu[tt[ids[valid]]]);vectors.append(val);unmapped.append(int((~valid).sum()))
 comparisons=[]
 for i,j in [(i,j) for i in range(len(data)) for j in range(i+1,len(data))]:
  valid=np.isfinite(vectors[i]).all(1)&np.isfinite(vectors[j]).all(1);scalar=abs(rows[i]['energy_Nmm']/rows[j]['energy_Nmm']-1);vec=float(np.sqrt(np.sum(vol[valid,None]*(vectors[i][valid]-vectors[j][valid])**2)/np.sum(vol[valid,None]*vectors[j][valid]**2)));complete=bool(valid.all());comparisons.append(dict(pair=[i,j],energy_relative=scalar,volume_centroid_quadrature_vector_relative_L2=vec,unmapped_points=int((~valid).sum()),unmapped_volume_mm3=float(vol[~valid].sum()),whole_domain_complete=complete,quadrature_converged=False,physical_spatial_gate_pass=False))
 np.savez_compressed(out/'volume_vectors.npz',material_points_mm=probes,volume_weight_mm3=vol,raw_vectors_mm=np.array(vectors));dump(out/'summary.json',dict(status='ACTUAL_P1_OBJECTIVE_CONTACT_STABLE_RIGID_TRANSFORM_AUDIT_UNQUALIFIED',candidate_reference=ref(cp),producer=ref(out/'producer.py'),rows=rows,all_local_checks_pass=all(all(r['checks'].values()) for r in rows),comparisons=comparisons,unmapped_per_mesh=unmapped,volume_vectors=ref(out/'volume_vectors.npz'),newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-start,rigid_transform_arithmetic='Form p+u in extendedprecision before rotation, preserving small elastic displacement; prior float64 preaddition failure preserved.',limitations=['Independent material IFT and actual Root BRep face/normalcones; objective StVK typical material, not sourced minimum.','One centroid per finest tetra is a whole-volume quadrature ATTEMPT, not a converged whole-domain vector norm. Every missingpoint/volume explicit; no dropping boundary-domain mismatch for PASS.','Actual Root/pin/slot/bolt/nut/preload and all83body coupling remain unsolved; no spatial/time/globalenergy/sourceallowable certification.']));print(json.dumps(dict(checks=[r['checks'] for r in rows],comparisons=comparisons)),flush=True);return 0 if all(all(r['checks'].values()) for r in rows) else 2
if __name__=='__main__':sys.exit(main())
