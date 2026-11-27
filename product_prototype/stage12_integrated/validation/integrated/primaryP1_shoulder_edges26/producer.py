"""Actual mesh boundary edge cones; contrast only, no BRep smooth-surface certification."""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');results=[];rows=[]
 for level in [2,3]:
  src=ROOT/f'validation/integrated/primaryP1_ycapture_mesh{level}/summary.json';s=json.loads(src.read_text());d=np.load(REPO/s['mesh']['path']);p=d['OPEN_FRAME_points_mm'];tet=d['OPEN_FRAME_tetra'];fs=np.concatenate([tet[:,v] for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);op=np.concatenate([tet[:,i] for i in [3,2,1,0]]);key=np.sort(fs,axis=1);u,idx,c=np.unique(key,axis=0,return_index=True,return_counts=True);idx=idx[c==1];f=fs[idx];op=op[idx];X=p[f];norm=np.cross(X[:,1]-X[:,0],X[:,2]-X[:,0]);norm*=np.where(np.einsum('ni,ni->n',norm,p[op]-X.mean(1))>0,-1,1)[:,None];norm/=np.linalg.norm(norm,axis=1)[:,None];adj={}
  for fi,face in enumerate(f):
   for a,b in [(0,1),(1,2),(2,0)]:adj.setdefault(tuple(sorted([int(face[a]),int(face[b])])),[]).append(fi)
  for sign in [-1,1]:
   selected=set(np.where(np.all(abs(X[:,:,1]-sign*20.1)<1e-7,axis=1)&np.all((X[:,:,2]>=-7.000001)&(X[:,:,2]<=-2.999999),axis=1))[0]);edges=[]
   for edge,owners in adj.items():
    if sum(i in selected for i in owners)!=1:continue
    if not any(i in selected for i in owners):continue
    assert len(owners)==2
    ns=norm[owners];a,b=p[list(edge)];e=(a+b)/2;n=ns.sum(0);n/=np.linalg.norm(n);q=e+.1*n;force_error=np.linalg.norm(n-n);moment_error=np.linalg.norm(np.cross(q,n)-np.cross(e,n));delta=p[edge[1]]-p[edge[0]];u=delta/np.linalg.norm(delta);radial=q-(a+u*((q-a)@u));distance=np.linalg.norm(radial);gradient=radial/distance;dirs=np.array([[.003,-.002,.004],[-.001,.002,.003],[.004,.001,-.002]])
    def gap(qq,aa,bb):
     t=np.clip((qq-aa)@(bb-aa)/np.dot(bb-aa,bb-aa),0,1);return np.linalg.norm(qq-(aa+t*(bb-aa)))
    analytic=gradient@(dirs[0]-.5*dirs[1]-.5*dirs[2]);eps=1e-4;fd=(gap(q+eps*dirs[0],a+eps*dirs[1],b+eps*dirs[2])-gap(q-eps*dirs[0],a-eps*dirs[1],b-eps*dirs[2]))/(2*eps)
    # Convexity of local solid: neighbor opposite vertices should lie on inner side.
    convex=all(np.max((X[owners[1-k]]-e)@ns[k])<1e-7 for k in [0,1]);angle=float(np.arccos(np.clip(ns[0]@ns[1],-1,1)));record=dict(mesh_level=level,sign=sign,edge_nodes=list(edge),edge_mm=[a.tolist(),b.tolist()],owner_triangles=owners,outward_normals=ns.tolist(),dihedral_rad=angle,local_convex=bool(convex),distance_mm=distance,virtualwork_error=abs(fd-analytic),moment_error_Nmm=moment_error,normal_cone_test_direction=n.tolist(),physical_reaction_claimed=False);edges.append(record);rows.append(record)
   results.append(dict(mesh_level=level,sign=sign,boundary_edges=len(edges),convex_edges=sum(e['local_convex'] for e in edges),nonconvex_edges=sum(not e['local_convex'] for e in edges),min_dihedral_rad=min(e['dihedral_rad'] for e in edges),max_dihedral_rad=max(e['dihedral_rad'] for e in edges),max_virtualwork_error=max(e['virtualwork_error'] for e in edges),max_moment_error=max(e['moment_error_Nmm'] for e in edges)))
 checks=dict(all_edges_have_two_owners=True,all_sides_present=len(results)==4,virtualwork=all(r['max_virtualwork_error']<1e-8 for r in results),moment=all(r['max_moment_error']<1e-8 for r in results),convex_cones=all(r['nonconvex_edges']==0 for r in results));dump(out/'edges.json',rows);dump(out/'summary.json',dict(status='ACTUAL_P1_MESH_FINITE_EDGE_CONE_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_MESH_FINITE_EDGE_CONE_FAIL',candidate=s['candidate'],producer=ref(out/'producer.py'),edges=ref(out/'edges.json'),checks=checks,results=results,elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],whole_system_release=False,accepted_equilibria=0,limitations=['Piecewise linear tetra boundary normal-cone tests only. Fillet is smooth BRep, mesh crease angles are not exact CAD edge physics.','Mid-edge unit virtual-force/distance derivative probes do not implement corner/grazing/feature-transition coupled contact.','Concave edges, if any, reject convex-hull edge model. No reaction transfer or solver update.']));print(json.dumps(dict(checks=checks,results=results)));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
