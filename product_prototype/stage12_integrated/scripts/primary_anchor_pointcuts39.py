"""Actual P1 two finite bodies + conditional axial connectors, no fixed nodes.
A variational contact sensitivity, NOT a certified support or installed bolt law.
Every source is an explicit actual-surface six-resultant Neumann functional.
"""
import sys,json,shutil,time,gc
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import qr
from scipy.optimize import minimize,linprog
import osqp
from types import SimpleNamespace
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_finite_body34 import meshpart
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,bounds
from primary_motor_bearing_wrenches import faces
from validate_base_anchor36 import props
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.gp import gp_Pnt

ST=[(-44,34),(86,34),(21,-53)]
I=np.eye(3)
def H(p):
 p=np.asarray(p);return np.r_[I,np.array([[0,-p[2],p[1]],[p[2],0,-p[0]],[-p[1],p[0],0]])]
def clip(poly,k,v,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[k]-v)*(1 if above else -1);db=(b[k]-v)*(1 if above else -1)
  if da>=-1e-12:out.append(a)
  if (da>0 and db<0) or (da<0 and db>0):out.append(a+(b-a)*da/(da-db))
 return out

def tri_shape(p):
 w=BRepBuilderAPI_MakePolygon()
 for q in p:w.Add(gp_Pnt(*map(float,q)))
 w.Close();return BRepBuilderAPI_MakeFace(w.Wire()).Face()
def planar_triangles(body,axis,value):
 p,tri=body['p'],body['tri'];ix=np.where(np.all(abs(p[tri,axis]-value)<1e-7,axis=1))[0]
 return [(tri[i],p[tri[i]]) for i in ix]
def bary(points,q):
 z=np.linalg.lstsq((points[1:]-points[0]).T,q-points[0],rcond=None)[0];return np.r_[1-z.sum(),z]
def add(F,nodes,bc,force,col):
 for j,node in enumerate(nodes):F[3*node:3*node+3,col]+=bc[j]*force

def common_faces(a,b,axis,v):
 result=[]
 for f in faces(a,axis,v):
  for g in faces(b,axis,v):
   c=BRepAlgoAPI_Common(f,g).Shape();ar,_=props(c,True)
   if ar>1e-8:result.append(c)
 return result

def patches(base,rail,shapes,n):
 defs=[(2,66,[0,0,-1],'topseat'),(0,-50,[1,0,0],'key0_xmin'),(0,-38,[-1,0,0],'key0_xmax'),(1,28,[0,1,0],'key_ymin'),(1,40,[0,-1,0],'key_ymax')]
 out=[]
 for ax,v,d,label in defs:
  other=[k for k in range(3) if k!=ax]
  for f in common_faces(shapes['TEST_BASE'],shapes['BENCH_ANCHOR_RAIL'],ax,v):
   bb=np.array(bounds(f));gr=[np.linspace(bb[k],bb[k+3],n+1) for k in other]
   for lo,hi in zip(gr[0][:-1],gr[0][1:]):
    for l2,h2 in zip(gr[1][:-1],gr[1][1:]):
     low=bb[:3].copy();size=bb[3:]-low;low[ax]-=.01;size[ax]=.02;low[other]=[lo,l2];size[other]=[hi-lo,h2-l2]
     patch=BRepAlgoAPI_Common(f,box(*map(float,low),*map(float,size))).Shape();ar,c=props(patch,True)
     if ar>1e-8:out.append(dict(label=label,axis=ax,value=v,d=np.array(d,float),face=patch,area=ar,centroid=c,body_faces=[(base,ax,v),(rail,ax,v)]))
 for i,(x,y) in enumerate(ST):
  fs=common_faces(shapes['TEST_BASE'],shapes[f'ANCHOR_BOLT_{i}'],2,60);gs=common_faces(shapes['BENCH_ANCHOR_RAIL'],shapes[f'ANCHOR_NUT_{i}'],2,74)
  assert len(fs)==len(gs)==1
  ah,ch=props(fs[0],True);an,cn=props(gs[0],True)
  out.append(dict(label=f'bolt{i}',axis=2,value=60,d=np.array([0,0,1.]),face=fs[0],area=ah,centroid=ch,rail_face=gs[0],rail_area=an,rail_centroid=cn,body_faces=[(base,2,60),(rail,2,74)]))
 return out

def map_patch(body,face,axis,value,d,col,F):
 """Exact BRep intersection with every planar FE boundary triangle.
 Constant traction is integrated at intersection centroid (P1 is affine).
 Finite chord-hole domain differences are measured, never called exact CAD.
 """
 total=0.;cent=np.zeros(3);journal=[];fb=np.array(bounds(face));other=[k for k in range(3) if k!=axis]
 for nodes,pts in planar_triangles(body,axis,value):
  if any(pts[:,k].max()<fb[k]-1e-8 or pts[:,k].min()>fb[k+3]+1e-8 for k in other):continue
  shape=BRepAlgoAPI_Common(face,tri_shape(pts)).Shape();area,q=props(shape,True)
  if area<1e-11:continue
  bc=bary(pts,q);assert bc.min()>-1e-7 and bc.max()<1+1e-7
  total+=area;cent+=area*q;journal.append(dict(nodes=nodes.tolist(),barycentric=bc.tolist(),point_mm=q.tolist(),area_mm2=area))
 assert total>1e-8
 for row in journal:add(F,row['nodes'],row['barycentric'],d*row['area_mm2']/total,col)
 return dict(integrated_area_mm2=total,centroid_mm=(cent/total).tolist(),normalized_direction=d.tolist(),quadrature=journal)

def body_mesh(part,path,h):
 start=time.monotonic();p,t,tri,V=meshpart(path,h,24);N=len(p)*3;m=MeshTet(p.T,t.T);la,mu=lame_parameters(69000.,.33);K=sparse.csr_matrix((N,N))
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,ElementVector(ElementTetP1()),intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 R=np.zeros((N,6));origin=p.mean(0);scale=100.
 for j,e in enumerate(I):R[:,j]=np.broadcast_to(e,p.shape).ravel();R[:,j+3]=(np.cross(e,p-origin)/scale).ravel()
 Q=R.T/len(p)
 if len(sys.argv)>6 and sys.argv[6]=='sparsegauge':
  # Algebraic anchoring factors the quotient, then restores ALL displacement
  # DOFs and the original six mean-rigid gauges. No physical fixation.
  _,_,pivot=qr(R.T,mode='economic',pivoting=True);anchors=np.sort(pivot[:6]);free=np.setdiff1d(np.arange(N),anchors);factor=splu((K[free][:,free]/69000.).tocsc(),permc_spec='MMD_AT_PLUS_A')
  return dict(name=part,p=p,t=t,tri=tri,K=K,R=R,Q=Q,factor=factor,CADV=V,start=start,free=free,algebraic_anchors=anchors)
 A=sparse.bmat([[K/69000.,sparse.csr_matrix(Q.T)],[sparse.csr_matrix(Q),None]],format='csc');factor=splu(A)
 return dict(name=part,p=p,t=t,tri=tri,K=K,R=R,Q=Q,factor=factor,CADV=V,start=start)

def surface_moment(shape):
 from OCP.GProp import GProp_GProps
 from OCP.BRepGProp import BRepGProp
 g=GProp_GProps();BRepGProp.SurfaceProperties_s(shape,g);area=g.Mass();q=g.CentreOfMass();q=np.array([q.X(),q.Y(),q.Z()]);mm=g.MatrixOfInertia();J=np.array([[mm.Value(i+1,j+1) for j in range(3)] for i in range(3)]);cov=np.eye(3)*np.trace(J)/2-J
 return area,q,cov

def source(body,shapes,profile):
 """Exactly affine six-resultant traction on a fixed actual CAD surface.
 Surface area/centroid/central second moments integrate N*H and H*H exactly.
 This avoids changing source shape when bulk triangles are refined.
 """
 N=3*len(body['p']);F=np.zeros((N,6));qs=[];part=body['name'];z=46 if part=='TEST_BASE' else 66
 actual=common_faces(shapes['TEST_BASE'],shapes['GROUND_PLATE'],2,z) if part=='TEST_BASE' else faces(shapes['BENCH_ANCHOR_RAIL'],2,z)
 if part!='TEST_BASE':
  actual=[BRepAlgoAPI_Common(f,box(lo,-64,65.99,10,109,.02)).Shape() for f in actual for lo in (-64,96)]
 deriv=[H(e)-H(np.zeros(3)) for e in I]
 for face in actual:
  for nodes,pts in planar_triangles(body,2,z):
   c=BRepAlgoAPI_Common(face,tri_shape(pts)).Shape()
   if profile=='ends' and part!='TEST_BASE':
    lo=BRepAlgoAPI_Common(c,box(-65,-64,65.99,172,20,.02)).Shape();hi=BRepAlgoAPI_Common(c,box(-65,24,65.99,172,21,.02)).Shape()
    # These disjoint strips define a different actual exposed support trace,
    # not a new material or a declared physical bench attachment.
    from build_stage1 import compound
    c=compound([lo,hi])
   ar,q,cov=surface_moment(c)
   if ar<1e-10:continue
   pinv=np.linalg.pinv((pts[1:]-pts[0]).T);grad=np.vstack([-pinv.sum(0),pinv])
   qs.append(dict(nodes=nodes.tolist(),barycentric=bary(pts,q).tolist(),point_mm=q.tolist(),area_mm2=ar,central_second_moment_mm4=cov.tolist(),shape_gradients_per_mm=grad.tolist()))
 assert len(qs)>6,(part,len(qs));M=np.zeros((6,6))
 for q in qs:
  hq=H(q['point_mm']);cov=np.array(q['central_second_moment_mm4']);M+=q['area_mm2']*hq@hq.T
  for i in range(3):
   for j in range(3):M+=cov[i,j]*deriv[i]@deriv[j].T
 inv=np.linalg.inv(M)
 for q in qs:
  hq=H(q['point_mm']);cov=np.array(q['central_second_moment_mm4']);grad=np.array(q['shape_gradients_per_mm'])
  for a,node in enumerate(q['nodes']):
   integral=q['area_mm2']*q['barycentric'][a]*hq.T
   for i in range(3):
    for j in range(3):integral+=grad[a,i]*cov[i,j]*deriv[j].T
   F[3*node:3*node+3,:]+=integral@inv
 return F,qs

def solve_body(body,F,out,journal):
 N=F.shape[0]
 if 'free' in body:
  R,Q=body['R'],body['Q'];dual=np.linalg.solve(R.T@Q.T,R.T@F);balanced=F-Q.T@dual;U=np.zeros_like(F);U[body['free']]=body['factor'].solve(balanced[body['free']]/69000.);U-=R@np.linalg.solve(Q@R,Q@U);sol=np.vstack([U,dual/69000.])
 else:sol=body['factor'].solve(np.vstack([F/69000.,np.zeros((6,F.shape[1]))]));U=sol[:N]
 projected_res=body['K']@U+body['Q'].T@(sol[N:]*69000.)-F
 fields=dict(points_mm=body['p'],tetra=body['t'],boundary_triangles=body['tri'],F=F,Q=body['Q'],R=body['R'],dual=sol[N:]*69000.)
 chunks=[]
 if U.nbytes>30_000_000:
  for first in range(0,U.shape[1],12):
   path=out/(body['name']+f'_U{first:03}.npz');np.savez_compressed(path,U=U[:,first:first+12]);chunks.append(dict(first_column=first,reference=ref(path)))
 else:fields['U']=U
 np.savez_compressed(out/(body['name']+'.npz'),**fields)
 result=dict(part=body['name'],nodes=N//3,tetra=len(body['t']),DOF=N,conditional_E_MPa=69000.,conditional_nu=.33,algebraic_factorization='sparse_quotient_restore' if 'free' in body else 'bordered_LU',algebraic_anchors_restored=body.get('algebraic_anchors',np.array([],int)).tolist(),all_elastic_DOF_retained=True,rigid_gauges=6,fixed_DOF=0,projected_stationarity_N=float(abs(projected_res).max()),unbalanced_columns_NOT_physical_equilibria=True,fields=ref(out/(body['name']+'.npz')),boundary_journal=journal,displacement_chunks=chunks)
 return U,F.T@U,result


def local_common_patches(base,rail,shapes,n):
 # Select actual loaded negative-gap triangles using immutable cycle37 fields.
 from anchor_gap_trace37 import prepare,locate,rigid
 prior=ROOT/'validation/integrated'/sys.argv[7];original=patches(base,rail,shapes,n);original_bounds=[np.array(bounds(p['face'])) for p in original]
 doc=json.loads((prior/'summary.json').read_text());geo=json.loads((REPO/doc['geometry']['path']).read_text());ops=np.load(REPO/doc['operators']['path']);eq=ops['equality'];scale=np.tile([1,1,1,.01,.01,.01],2)
 arrays=[dict(np.load(REPO/r['path'])) for r in doc['fields']]
 for k,a in enumerate(arrays):
  if 'U' not in a:a['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in doc['body_results'][k]['displacement_chunks']])
 # Same mesh identity is required; this is pressure enrichment, not bulk refinement.
 for a,b in zip(arrays,[base,rail]):assert np.array_equal(a['points_mm'],b['p']) and np.array_equal(a['tetra'],b['t'])
 prepared={};worst={}
 for row in doc['rows']:
  if 'equality_multiplier' not in row:continue
  p=np.array(row['contact_forces_N']);w=np.array(row['external_wrench_N_Nmm']);ae=np.array(row['reduced_equality_matrix']);lm=np.array(row['equality_multiplier']);T=ae@np.linalg.pinv(eq*scale[:,None],rcond=1e-10);r=(scale*(T.T@lm)).reshape(2,6);U=[(a['U']@np.r_[p,w if k==0 else -w]).reshape(-1,3) for k,a in enumerate(arrays)]
  for j,patch in enumerate(geo['patches'][:-3]):
   # After loaded-region correction, also activate locally penetrating
   # zero-resultant remainder cells; zero mean pressure does not permit overlap.
   direction=np.array(patch['direction']);axis=int(np.argmax(abs(direction)));value=patch['exact_CAD_centroid_mm'][axis];key=(axis,round(value,7))
   if key not in prepared:prepared[key]=prepare(arrays[1],axis,value)
   for qd in geo['body_quadrature'][0][j]['quadrature']:
    q=np.array(qd['point_mm']);hit=locate(q,prepared[key])
    if hit is None:continue
    nodes,bc=hit;u0=np.array(qd['barycentric'])@U[0][qd['nodes']];u1=bc@U[1][nodes];gap=float(direction@(u0-u1+rigid(q,r[0])-rigid(q,r[1])));owners=[ii for ii,pat in enumerate(original[:-3]) if pat['axis']==axis and abs(pat['value']-value)<1e-7 and np.linalg.norm(pat['d']-direction)<1e-10 and np.all(q>=original_bounds[ii][:3]-1e-7) and np.all(q<=original_bounds[ii][3:]+1e-7)];assert owners,(j,q);identity=(owners[0],tuple(qd['nodes']))
    if gap<min(-1e-8,worst.get(identity,dict(gap=0))['gap']):worst[identity]=dict(gap=gap,case=row['case'],point=q.tolist())
 previous=json.loads((REPO/doc['local_common_refinement']['path']).read_text());retained={(entry['original_patch'],tuple(cell['base_nodes'])) for entry in previous['patches'] for cell in entry['cells']};new=[]
 selected=list(sorted(retained))+new # Preserve all prior refined triangles; add exact separation points below
 for ident in retained:worst.setdefault(ident,dict(gap=None,case='RETAINED_PRIOR_REFINEMENT',point=None))
 out=[];journal=[]
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
 for j,pat in enumerate(original):
  picks=[k for k in selected if k[0]==j]
  if not picks:out.append(pat);continue
  remainder=pat['face'];total=0.;cells=[]
  for ident in picks:
   nodes=np.array(ident[1]);pts=base['p'][nodes];region=BRepAlgoAPI_Common(pat['face'],tri_shape(pts)).Shape();remainder=BRepAlgoAPI_Cut(remainder,region).Shape()
   rb=np.array(bounds(region));other=[k for k in range(3) if k!=pat['axis']]
   for rn,rp in planar_triangles(rail,pat['axis'],pat['value']):
    if any(rp[:,k].max()<rb[k]-1e-8 or rp[:,k].min()>rb[k+3]+1e-8 for k in other):continue
    cell=BRepAlgoAPI_Common(region,tri_shape(rp)).Shape();ar,c=props(cell,True)
    if ar<1e-8:continue
    q=dict(pat,face=cell,area=ar,centroid=c,label=pat['label']+'_common');out.append(q);total+=ar
    cells.append(dict(base_nodes=nodes.tolist(),receiver_nodes=rn.tolist(),area_mm2=ar,centroid_mm=c.tolist(),selected_source=worst[ident]))
  ar,c=props(remainder,True)
  if ar>1e-8:out.append(dict(pat,face=remainder,area=ar,centroid=c,label=pat['label']+'_remainder'));total+=ar
  journal.append(dict(original_patch=j,label=pat['label'],original_area_mm2=pat['area'],common_and_remainder_area_mm2=total,uncovered_area_mm2=pat['area']-total,cells=cells))
 # Discrete unilateral contact at common-polygon vertices. Each vertex force
 # acts at exactly the same material point on both P1 surface traces.
 # These are FE constraint multipliers, not physical point pressures.
 from OCP.TopExp import TopExp_Explorer
 from OCP.TopAbs import TopAbs_VERTEX
 from OCP.TopoDS import TopoDS
 from OCP.BRep import BRep_Tool
 converted=[];seen={}
 for pat in out:
  if not pat['label'].endswith('_common'):converted.append(pat);continue
  ex=TopExp_Explorer(pat['face'],TopAbs_VERTEX);vertices=[]
  while ex.More():
   pt=BRep_Tool.Pnt_s(TopoDS.Vertex_s(ex.Current()));q=np.array([pt.X(),pt.Y(),pt.Z()])
   if not any(np.linalg.norm(q-v)<1e-8 for v in vertices):vertices.append(q)
   ex.Next()
  for q in vertices:
   key=tuple(np.round(q,8))+tuple(pat['d'])
   if key in seen:converted[seen[key]]['area']+=pat['area']/len(vertices);continue
   supports=[]
   for b in [base,rail]:
    hit=[]
    for nd,pts in planar_triangles(b,pat['axis'],pat['value']):
     bc=bary(pts,q)
     if bc.min()>-1e-7 and np.linalg.norm(bc@pts-q)<1e-7:hit.append((nd,bc))
    assert hit;supports.append(hit[0])
   seen[key]=len(converted);converted.append(dict(pat,centroid=q,area=pat['area']/len(vertices),point_supports=supports,label=pat['label']+'_vertex'))
 global POINT_CUTS
 oracle=ROOT/'validation/integrated'/sys.argv[8]/'summary.json';od=json.loads(oracle.read_text());assert od['source']['SHA256']==sha(prior/'summary.json')
 POINT_CUTS=list(previous.get('retained_point_cuts',[]));known={tuple(np.round(c['point_mm'],8))+tuple(c['direction']) for c in POINT_CUTS};violations=[]
 for cell in od['cells']:
  for row in cell['states']:
   if row['continuous_affine_gap_lower_bound_mm'] < -1e-8:violations.append((row['continuous_affine_gap_lower_bound_mm'],cell,row))
 added=0
 for gap,cell,row in sorted(violations,key=lambda x:x[0]):
  pat=original[cell['original_patch']];q=np.array(row['minimum_witness_mm']);key=tuple(np.round(q,8))+tuple(pat['d'])
  if key in known:continue
  POINT_CUTS.append(dict(point_mm=q.tolist(),direction=pat['d'].tolist(),original_patch=cell['original_patch'],origin_case=row['case'],origin_gap_mm=gap,oracle=ref(oracle)));known.add(key);added+=1
  if added>=int(sys.argv[5]):break
 for cut in POINT_CUTS:
  pat=original[cut['original_patch']];q=np.array(cut['point_mm']);supports=[]
  for b in [base,rail]:
   hit=[]
   for nd,pts in planar_triangles(b,pat['axis'],pat['value']):
    bc=bary(pts,q)
    if bc.min()>-1e-7 and np.linalg.norm(bc@pts-q)<1e-7:hit.append((nd,bc))
   assert hit;supports.append(hit[0])
  converted.append(dict(pat,centroid=q,area=1.,point_supports=supports,label=pat['label']+'_oracle_point'))
 return converted,journal

def main():
 tag,h,n,profile=sys.argv[1:5];h=float(h);n=int(n);out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();cp=ROOT/'cad/exports/primaryP1_anchor36b/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==85 and all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());shapes={name:read(REPO/r['path']) for name,r in cad['part_references'].items() if name in ['TEST_BASE','BENCH_ANCHOR_RAIL','GROUND_PLATE'] or name.startswith('ANCHOR_')}
 bodies=[body_mesh(name,REPO/cad['part_references'][name]['path'],h) for name in ['TEST_BASE','BENCH_ANCHOR_RAIL']];patch,enrichment=local_common_patches(*bodies,shapes,n) if int(sys.argv[5]) else (patches(*bodies,shapes,n),[]);dump(out/'enrichment.json',dict(prior=ref(ROOT/'validation/integrated'/sys.argv[7]/'summary.json'),additional_triangle_budget=int(sys.argv[5]),selection='retain previous triangles AND exact separation points;append independent ALL-domain analytic minimum witnesses',retained_point_cuts=POINT_CUTS,patches=enrichment));nc=len(patch);F=[np.zeros((3*len(b['p']),nc+6)) for b in bodies];journals=[[],[]];meta=[]
 for j,pat in enumerate(patch):
  assert not(ROOT/'runtime/STOP').exists();row=dict(label=pat['label'],exact_CAD_area_mm2=pat['area'],exact_CAD_centroid_mm=pat['centroid'].tolist(),direction=pat['d'].tolist(),bodies=[])
  for k,b in enumerate(bodies):
   ax,v=pat['body_faces'][k][1:];face=pat.get('rail_face',pat['face']) if k else pat['face'];d=pat['d']*(-1 if k else 1)
   if 'point_supports' in pat:
    nd,bc=pat['point_supports'][k];add(F[k],nd,bc,d,j);m=dict(integrated_area_mm2=pat['area'],centroid_mm=pat['centroid'].tolist(),normalized_direction=d.tolist(),quadrature=[dict(nodes=nd.tolist(),barycentric=bc.tolist(),point_mm=pat['centroid'].tolist(),area_mm2=pat['area'])],discrete_vertex_constraint=True)
   else:m=map_patch(b,face,ax,v,d,j,F[k])
   journals[k].append(m);row['bodies'].append({key:value for key,value in m.items() if key!='quadrature'})
  meta.append(row)
 source_journal=[]
 for k,b in enumerate(bodies):
  S,qs=source(b,shapes,profile);F[k][:,nc:]=S;source_journal.append(qs)
 Us=[];Cs=[];bodyrows=[]
 for k,b in enumerate(bodies):
  U,C,row=solve_body(b,F[k],out,journals[k]);Us.append(U);Cs.append(C);bodyrows.append(row);del b['factor'];gc.collect()
 # World wrenches in N/Nmm; all relative rigid translations AND rotations
 # remain unknown and are enforced by equilibrium (six equality rows).
 Aw=[]
 for k,b in enumerate(bodies):
  W=np.column_stack([sum((H(q)@f for q,f in zip(b['p'],F[k][:,j].reshape(-1,3))),np.zeros(6)) for j in range(nc+6)]);Aw.append(W)
 A=Aw[0][:,:nc];source_error=max(abs(Aw[k][:,nc:]-np.eye(6)).max() for k in range(2));pair_error=float(abs(Aw[0][:,:nc]+Aw[1][:,:nc]).max())
 # Nonmatching linear FE rims have slightly different centroids. Preserve
 # actual mapped moments; use full two-body equality, not silently match them.
 eq=np.vstack([Aw[0][:,:nc],Aw[1][:,:nc]])
 loads=json.loads((ROOT/'validation/integrated/primaryP1_anchor36b_witness/tractions.json').read_text())['8'];rows=[];C=Cs[0][:nc,:nc]+Cs[1][:nc,:nc];C=(C+C.T)/2;spring=np.zeros(nc);spring[-3:]=14/(200000.*np.pi*2.5**2);C+=np.diag(spring)
 for name,l in loads.items():
  assert not(ROOT/'runtime/STOP').exists();w=np.array(l['external_wrench_N_Nm'])*[1,1,1,1000,1000,1000];f0=F[0][:,nc:]@w;f1=F[1][:,nc:]@(-w);d=Cs[0][:nc,nc:]@w-Cs[1][:nc,nc:]@w;rhs=np.r_[-w,w];scale=np.tile([1,1,1,.01,.01,.01],2);eqs=eq*scale[:,None];rs=rhs*scale
  # Remove ONLY algebraically redundant force equilibrium rows using SVD.
  uu,ss,vv=np.linalg.svd(eqs,full_matrices=False);rank=int(sum(ss>ss[0]*1e-10));ae=uu[:,:rank].T@eqs;be=uu[:,:rank].T@rs;compat=float(np.max(abs(rs-uu[:,:rank]@be)));feas=linprog(np.zeros(nc),A_eq=ae,b_eq=be,bounds=(0,None),method='highs')
  rr=dict(case=name,external_wrench_N_Nmm=w.tolist(),algebraic_equality_rank=rank,discarded_row_compatibility=compat,LP_feasible=bool(feas.success),status='NO_CONDITIONAL_SOLUTION')
  if feas.success and compat<1e-8:
   cscale=max(abs(C).max(),1e-12);qp=osqp.OSQP();qp.setup(P=sparse.csc_matrix(C/cscale),q=d/cscale,A=sparse.vstack([sparse.csc_matrix(ae),sparse.eye(nc)],format='csc'),l=np.r_[be,np.zeros(nc)],u=np.r_[be,np.full(nc,np.inf)],eps_abs=1e-10,eps_rel=1e-10,max_iter=200000,polishing=True,verbose=False);res=qp.solve();opt=SimpleNamespace(x=res.x,success=res.info.status_val==1,message=res.info.status,nit=res.info.iter);p=opt.x;g=C@p+d;active=p>max(p.max()*1e-8,1e-10);lm=np.linalg.lstsq(ae[:,active].T,-g[active],rcond=None)[0];# Active reactions may not span all six rigid modes. A minimum-norm
   # equality multiplier need not satisfy inactive inequalities. Select a
   # true dual witness by a separate scaled minimax LP; retain its residual.
   gs=max(abs(g).max(),1e-15);at=ae.T;ga=g/gs
   amat=np.vstack([np.c_[-at,-np.ones(nc)],np.c_[at[active],-np.ones(active.sum())]])
   bmat=np.r_[ga,-ga[active]];dual=linprog(np.r_[np.zeros(rank),1.],A_ub=amat,b_ub=bmat,bounds=[(None,None)]*rank+[(0,None)],method='highs')
   if dual.success:lm=dual.x[:rank]*gs
   gap=g+ae.T@lm;balanced=[];energy=[]
   for k,b in enumerate(bodies):
    coeff=np.r_[p,w if k==0 else -w];force=F[k]@coeff;u=Us[k]@coeff;balanced.append(dict(force_residual_N=float(abs((b['K']@u-force).reshape(-1,3)).max()),world_wrench_N_Nmm=(Aw[k]@coeff).tolist(),maximum_elastic_displacement_mm=float(np.linalg.norm(u.reshape(-1,3),axis=1).max())));energy.append(float(u@force))
   rr.update(status='CONDITIONAL_VARIATIONAL_SENSITIVITY_ONLY' if opt.success else 'QP_NUMERICAL_FAIL',optimizer_success=bool(opt.success),optimizer_message=str(opt.message),iterations=int(opt.nit),dual_feasible=bool(dual.success),dual_residual_mm=float(dual.x[-1]*gs) if dual.success else None,equality_multiplier=lm.tolist(),reduced_equality_matrix=ae.tolist(),contact_gap_mm=gap.tolist(),contact_forces_N=p.tolist(),force_per_tributary_area_MPa_NOT_pressure=[float(x/m['bodies'][0]['integrated_area_mm2']) for x,m in zip(p,meta)],bolt_tension_N=p[-3:].tolist(),nominal_major_shank_extension_mm=(p[-3:]*spring[-3:]).tolist(),maximum_negative_gap_mm=float(max(0,-gap.min())),active_stationarity_mm=float(abs(gap[active]).max()) if active.any() else 0.,maximum_complementarity_Nmm=float(abs(p*gap).max()),full_body_equilibrium=balanced,body_strain_work_Nmm=energy,bolt_strain_work_Nmm=float(np.dot(p*p,spring)),total_strain_work_Nmm=float(sum(energy)+np.dot(p*p,spring)),full_equality_residual_N_Nmm=(eq@p-rhs).tolist())
  rows.append(rr);print(json.dumps(dict(case=name,status=rr['status'],iterations=rr.get('iterations'))),flush=True)
 dump(out/'geometry_journal.json',dict(patches=meta,body_quadrature=journals,source_quadrature=source_journal));np.savez_compressed(out/'operators.npz',C=C,body_compliance=np.array(Cs),body_wrench=np.array(Aw),spring_mm_N=spring,equality=eq)
 dump(out/'inputs.json',dict(candidate=ref(cp),producer=ref(out/'producer.py'),mesh_dependency=ref(ROOT/'scripts/primary_finite_body34.py'),h_mm=h,curvature=24,patch_divisions=n,source_profile=profile,standard_dimensional_source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),conditional_body_material='E69000MPa nu.33 NOT source-backed minimum',conditional_bolt='E200000MPa nominal major diameter5mm L14mm axial spring only;unknown threadcore/flank,head/nut elasticity,rest/preload;NOT installed physical law',source_trace='Actual GroundPlate/Base common z46 face + actual exposed receiver underside outer x rims z66,exact affine six-resultant signed Neumann traces from surface second moments. No physical bench is present. No fixed nodes. Conditional loads re-express historical resultant ONLY;not solved gravity/contact field.',current_criteria=dict(force_N=1e-8,moment_Nm=1e-10,mesh_relative=.01,time_relative=.001)))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_ANCHOR_VARIATIONAL_CONDITIONAL_NOT_RELEASE',candidate=ref(cp),inputs=ref(out/'inputs.json'),contact_law='Mixed discrete common-vertex unilateral constraints and untouched finite-area P0 cells;vertex force/tributary area is NOT a physical pressure',actual_parts=85,local_common_refinement=ref(out/'enrichment.json'),actual_CAD_change_files=[],body_results=bodyrows,source_wrench_identity_max=source_error,opposite_pair_wrench_discrepancy_N_Nmm=pair_error,contact_variables=nc,rows=rows,fields=[ref(out/(b['name']+'.npz')) for b in bodies],operators=ref(out/'operators.npz'),geometry=ref(out/'geometry_journal.json'),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,hardware='NOT_MEASURED',limitations=['Finite actual full Base/receiver elasticity,not coupons. No elastic node fixed. Six gauges only;only balanced combined states may be physical sensitivities.','Signed source trace is an explicit conditional boundary functional,not actual positive bench contact,bolt clamp,external fixture or strength. No external receiver attachment exists.','Major-envelope axial springs are conditional upper-stiffness dimensions,not finite threadcore/flank/head/nut/preload/rest law.','Exact BRep common integrated over planar P1 mesh faces;facet-hole chord geometry/finite coverage and nonmatching centroid differences remain independent errors.','Frictionless nominal zero-gap planar contact sensitivity;no installed tolerance,source-backed material minima or operating Finger/root contact state.','All earlier LP/root/Beam/dt/globalenergy failures preserved. All22systemgates and fullsame-revision3Finger release blocked.']))
 print(json.dumps(dict(tag=tag,rows=len(rows),solved=sum(r.get('optimizer_success',False) for r in rows),pair_error=pair_error,source_error=source_error)),flush=True)
if __name__=='__main__':main()
