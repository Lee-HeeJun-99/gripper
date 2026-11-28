"""Full actual footed P1 plate frictional incremental local reference.
Actual finite upper faces carry explicitly affine Neumann wrench references
from required cut reactions. This is NOT actual83body/upperthread equilibrium.
Floor normal contact active set; tangential stick admitted ONLY if reactions
satisfy measured-or-assumed friction cone. A failed cone stays FAIL.
"""
import sys,json,time,shutil,resource
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import cg, splu
import pyamg
import osqp
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_finite_body34 import meshpart,wrenchmat
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate
from primary_anchor_contact38 import common_faces,surface_moment
started=time.monotonic();h=float(sys.argv[1]);nd=int(sys.argv[3]);angles=np.arange(nd)*2*np.pi/nd;directions=np.c_[np.cos(angles),np.sin(angles)];friction_facets=np.c_[np.cos(angles+np.pi/nd),np.sin(angles+np.pi/nd)]/np.cos(np.pi/nd);out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
def phase(n,**kw):print(json.dumps(dict(phase=n,elapsed_s=time.monotonic()-started,RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**kw)),flush=True)
cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());step=REPO/cad['part_references']['EXTERNAL_BENCH_PLATE']['path'];assert sha(step)==cad['part_references']['EXTERNAL_BENCH_PLATE']['SHA256'];src=ROOT/'validation/integrated/primaryP1_floor65c';sd=json.loads((src/'summary.json').read_text());assert all(sd['checks'].values());ld=json.loads((src/'load_ledger.json').read_text());fields=json.loads((src/'contact_fields.json').read_text());case=next(q for q in fields['rows'] if q['ground_mu_ASSUMED']==.3);ray=np.array(case['full_ray_coefficients']);patches=json.loads((REPO/ld['source_upper_patches']['path']).read_text());ports=json.loads((REPO/ld['source_ports']['path']).read_text())['ports'];sourceports=[];j=0
# Reconstruct actual prescribed wrench on each plate interface, without changing partDOFs.
for q in patches:
 target=np.zeros(6);tang=[i for i in range(3) if i!=q['axis']]
 for c in q['cells']:
  for a,sign in [(tang[0],1),(tang[0],-1),(tang[1],1),(tang[1],-1)]:
   f=np.array(q['normal_on_i'],float);f[a]+=.3*sign
   if q['body_i']=='EXTERNAL_BENCH_PLATE':target+=ray[j]*wrenchmat(np.array(c['point_mm'])[None])[0]@f
   if q['body_j']=='EXTERNAL_BENCH_PLATE':target-=ray[j]*wrenchmat(np.array(c['point_mm'])[None])[0]@f
   j+=1
 if 'EXTERNAL_BENCH_PLATE' in [q['body_i'],q['body_j']]:sourceports.append(dict(label=q['label'],axis=q['axis'],value=q['value_mm'],target_N_Nmm=target,other='BENCH_SUPPORT'))
for q in ports:
 if q['body_j']=='EXTERNAL_BENCH_PLATE':
  target=-ray[j]*wrenchmat(np.array(q['point_mm'])[None])[0]@np.array(q['direction']);sourceports.append(dict(label=q['label'],axis=2,value=-138.,target_N_Nmm=target,other=q['part_IDs'][1]))
 j+=1
phase('before_mesh');p,t,tri,V=meshpart(step,h,8);phase('after_mesh',nodes=len(p),tetra=len(t));N=3*len(p);m=MeshTet(p.T,t.T);E=200000.;nu=.3;la,mu=lame_parameters(E,nu);K=sparse.csr_matrix((N,N));el=ElementVector(ElementTetP1())
for first in range(0,len(t),8000):
 assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
phase('after_assembly',nnz=K.nnz);det=np.linalg.det(np.transpose(p[t[:,1:]]-p[t[:,0,None]],(0,2,1)));vol=abs(det)/6;lump=np.zeros(len(p))
for a in range(4):np.add.at(lump,t[:,a],vol/4)
F=np.zeros((len(p),3));F[:,2]=-lump*7900e-9*9.80665;inputjournal=[];floortri=tri[np.all(abs(p[tri,2]+170)<1e-7,axis=1)];floornodes=np.unique(floortri);nodearea=np.zeros(len(p))
for ns in floortri:
 ar=np.linalg.norm(np.cross(p[ns[1]]-p[ns[0]],p[ns[2]]-p[ns[0]]))/2;nodearea[ns]+=ar/3
plate=read(step);support=translate(read(REPO/cad['part_references']['BENCH_SUPPORT']['path']),.1,0,0)
# Finite face source quadrature; actualCADcommonfaces select genuine contact footprint.
# Analytic point classification limits triangles. Source is affine reference, not
# the nonunique constant-cell LP pressure and never claimed as solved uppercontact.
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN,TopAbs_ON,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
def flatten_faces(shapes):
 result=[]
 for shape in shapes:
  ex=TopExp_Explorer(shape,TopAbs_FACE)
  while ex.More():result.append(TopoDS.Face_s(ex.Current()));ex.Next()
 return result
qbc=np.array([[1/3,1/3,1/3],[.059715871789770,.470142064105115,.470142064105115],[.470142064105115,.059715871789770,.470142064105115],[.470142064105115,.470142064105115,.059715871789770],[.797426985353087,.101286507323456,.101286507323456],[.101286507323456,.797426985353087,.101286507323456],[.101286507323456,.101286507323456,.797426985353087]])
qw=np.array([.225]+[.132394152788506]*3+[.125939180544827]*3)
assert abs(qw.sum()-1)<1e-13
upperpoints=[]
for port in sourceports:
 other=support if port['other']=='BENCH_SUPPORT' else read(REPO/cad['part_references'][port['other']]['path']);fs=flatten_faces(common_faces(plate,other,port['axis'],port['value']));assert fs,(port['label'],'noactualCADsource');facets=tri[np.all(abs(p[tri,port['axis']]-port['value'])<1e-7,axis=1)];qs=[];M=np.zeros((6,6))
 for ns in facets:
  pts=p[ns];ar=np.linalg.norm(np.cross(pts[1]-pts[0],pts[2]-pts[0]))/2
  for bc,weight_fraction in zip(qbc,qw):
   x=bc@pts
   if not any(BRepClass_FaceClassifier(face,gp_Pnt(*map(float,x)),1e-7).State() in [TopAbs_IN,TopAbs_ON] for face in fs):continue
   H=wrenchmat(x[None])[0];M+=ar*weight_fraction*(H@H.T);qs.append((ns,bc,ar*weight_fraction,H,x))
 target=port['target_N_Nmm'];coeff=np.linalg.solve(M,target);local=np.zeros_like(F)
 for ns,bc,weight,H,x in qs:
  f=H.T@coeff
  for node,b in zip(ns,bc):local[node]+=weight*b*f
 upperpoints.append(dict(label=port['label'],axis=port['axis'],value_mm=port['value'],target_N_Nmm=target.tolist(),points_mm=[q[4].tolist() for q in qs],weights_mm2=[float(q[2]) for q in qs],integrated_force_N=[(q[2]*q[3].T@coeff).tolist() for q in qs]))
 F+=local;W=wrenchmat(p).transpose(1,0,2).reshape(6,-1)@local.ravel();inputjournal.append(dict(label=port['label'],actual_finite_CAD_face_area_mm2=sum(surface_moment(f)[0] for f in fs),FE_quadrature_area_mm2=sum(q[2] for q in qs),target_N_Nmm=target.tolist(),applied_N_Nmm=W.tolist(),reference='Affine traction with exact6wrench; sourcepressurefield/uppercontact NOT certified'))

dump(out/'upper_points.json',upperpoints)
dump(out/'summary.json',dict(status='ACTUAL_P1_FROZEN_UPPER7POINT_AFFINE_REFERENCE_GEOMETRY',candidate=ref(cp),STEP=ref(step),producer=ref(out/'producer.py'),points=ref(out/'upper_points.json'),source_ports=inputjournal,h_mm=h,scope='Frozen physical finiteCADface affine traction samples from declared5mm mesh; same pointforces pulled back to both targetmeshes. NOT actual thread/keeper contact.',newly_qualified_system_gate_ids=[],whole_system_release=False))
print(json.dumps(dict(ports=len(upperpoints),points=sum(len(q['points_mm']) for q in upperpoints))))
