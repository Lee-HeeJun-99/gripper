"""Actual P1 common-refinement material quadrature; no equilibrium/reaction claim."""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from primary_yshoulder_contact import evaluate

def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def clip(poly,tri):
 if cross(tri[1]-tri[0],tri[2]-tri[0])<0:tri=tri[::-1]
 for a,b in zip(tri,np.roll(tri,-1,axis=0)):
  result=[]
  for p,q in zip(poly,np.roll(poly,-1,axis=0)):
   dp=cross(b-a,p-a);dq=cross(b-a,q-a)
   if dp>=-1e-12:result.append(p)
   if (dp>0 and dq<0) or (dp<0 and dq>0):result.append(p+dp/(dp-dq)*(q-p))
  poly=np.array(result)
  if len(poly)<3:return np.empty((0,2))
 return poly

def bary(q,t):
 u=np.linalg.lstsq((t[1:]-t[0]).T,q-t[0],rcond=None)[0];return np.r_[1-u.sum(),u]

def nearest(q,t):
 w=bary(q,t);p=w@t
 if w.min()>=0:return p,w,'FACE'
 options=[]
 for i,j in [(0,1),(1,2),(2,0)]:
  e=t[j]-t[i];a=np.clip((q-t[i])@e/(e@e),0,1);v=(1-a)*t[i]+a*t[j];w=np.zeros(3);w[i]=1-a;w[j]=a;options.append((np.linalg.norm(q-v),v,w,'VERTEX' if a==0 or a==1 else 'EDGE'))
 _,p,w,k=min(options,key=lambda x:x[0]);return p,w,k

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(src.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());results=[];records=[]
 inputs={n:ref(ROOT/f'validation/integrated/primaryP1_ycapture_mesh{n}/summary.json') for n in [2,3]};dump(out/'inputs.json',dict(candidate=ref(src),meshes=inputs,producer=ref(out/'producer.py'),operator=ref(ROOT/'scripts/primary_yshoulder_contact.py'),compiled=False))
 rng=np.random.default_rng(2601)
 for level in [2,3]:
  ms=json.loads((REPO/inputs[level]['path']).read_text());data=np.load(REPO/ms['mesh']['path']);pts={n:data[n+'_points_mm'] for n in ['F0_ROOT_BACK','OPEN_FRAME']};fac={}
  for n,p in pts.items():
   tet=data[n+'_tetra'];f=np.sort(np.concatenate([tet[:,v] for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]),axis=1);u,c=np.unique(f,axis=0,return_counts=True);fac[n]=u[c==1]
  for sign in [-1,1]:
   triangles={}
   for n,p in pts.items():
    f=fac[n];y=sign*(20 if n=='F0_ROOT_BACK' else 20.1);mask=np.all(abs(p[f,1]-y)<1e-7,axis=1)
    if n=='OPEN_FRAME':mask &= np.all((p[f,2]>=-7.000001)&(p[f,2]<=-2.999999),axis=1)
    triangles[n]=p[f[mask]]
   rt=triangles['F0_ROOT_BACK'];ft=triangles['OPEN_FRAME'];rows=[];area=0.;maxwork=0.;maxmoment=0.;maxforce=0.;m1=np.zeros(3);maxbary=0.
   for ri,r in enumerate(rt):
    for fi,f in enumerate(ft):
     poly=clip(r[:,[0,2]],f[:,[0,2]])
     if len(poly)<3:continue
     for k in range(1,len(poly)-1):
      t=poly[[0,k,k+1]];a=abs(cross(t[1]-t[0],t[2]-t[0]))/2
      if a<1e-13:continue
      # Three point degree2 quadrature. Reference material weights stay fixed.
      for weights in [[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]]:
       xz=np.array(weights)@t;q=np.array([xz[0],sign*20,xz[1]]);rw=bary(q,r);orient=-sign*np.sign(np.cross(f[1]-f[0],f[2]-f[0])[1]);ev=evaluate(q,f,orient);w=a/3;area+=w;m1+=w*q;maxbary=max(maxbary,float(-min(rw.min(),ev['barycentric'].min())))
       D=rng.normal(size=(6,3))*.005;dq=rw@D[:3];analytic=ev['point_gradient']@dq+np.sum(ev['triangle_gradient']*D[3:]);eps=1e-4;fd=(evaluate(q+eps*dq,f+eps*D[3:],orient)['gap_mm']-evaluate(q-eps*dq,f-eps*D[3:],orient)['gap_mm'])/(2*eps);maxwork=max(maxwork,abs(fd-analytic))
       forces=np.vstack([rw[:,None]*ev['point_gradient'],ev['triangle_gradient']]);maxforce=max(maxforce,np.linalg.norm(forces.sum(0)));maxmoment=max(maxmoment,np.linalg.norm(np.cross(np.vstack([r,f]),forces).sum(0)))
       rows.append(dict(root_triangle=ri,owner_triangle=fi,root_barycentric=rw.tolist(),owner_barycentric=ev['barycentric'].tolist(),root_point_mm=q.tolist(),area_mm2=w,gap_mm=ev['gap_mm']))
   # Finite owner transitions for every material sample, never discard points.
   transitions=[]
   for shift in [np.zeros(3),np.array([0,-sign*.05,0]),np.array([.1,-sign*.05,0]),np.array([0,0,4.])]:
    Q=np.array([row['root_point_mm'] for row in rows])+shift
    E1=ft[:,1]-ft[:,0];E2=ft[:,2]-ft[:,0];D=Q[:,None,:]-ft[None,:,0,:]
    aa=np.einsum('ij,ij->i',E1,E1);bb=np.einsum('ij,ij->i',E1,E2);cc=np.einsum('ij,ij->i',E2,E2);det=aa*cc-bb*bb
    de1=np.einsum('nfi,fi->nf',D,E1);de2=np.einsum('nfi,fi->nf',D,E2)
    u=(de1*cc-de2*bb)/det;v=(de2*aa-de1*bb)/det;inside=(u>=0)&(v>=0)&(u+v<=1)
    proj=ft[None,:,0,:]+u[:,:,None]*E1+v[:,:,None]*E2
    ds=np.sum((Q[:,None,:]-proj)**2,axis=2);ds[~inside]=np.inf
    # Vectorized exact finite segments; all material samples retained.
    kinds=np.zeros(ds.shape,dtype=int)
    for i,j in [(0,1),(1,2),(2,0)]:
     edge=ft[:,j]-ft[:,i];delta=Q[:,None,:]-ft[None,:,i,:];tt=np.clip(np.einsum('nfi,fi->nf',delta,edge)/np.einsum('fi,fi->f',edge,edge),0,1);pp=ft[None,:,i,:]+tt[:,:,None]*edge;dd=np.sum((Q[:,None,:]-pp)**2,axis=2);better=dd<ds;ds=np.minimum(ds,dd);kinds[better]=np.where((tt==0)|(tt==1),2,1)[better]
    own=np.argmin(ds,axis=1);kind=kinds[np.arange(len(Q)),own];counts={k:int(np.sum(kind==i)) for i,k in enumerate(['FACE','EDGE','VERTEX'])};largest=float(np.sqrt(ds.min(axis=1).max()));outside=int(np.sum(kind!=0))
    transitions.append(dict(translation_mm=shift.tolist(),retained_samples=len(rows),feature_counts=counts,max_distance_mm=largest,edge_vertex_samples=outside,accepted_physical_update=False))
   rootarea=sum(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))/2 for t in rt);ownerarea=sum(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))/2 for t in ft)
   result=dict(mesh_level=level,sign=sign,root_triangles=len(rt),owner_triangles=len(ft),root_full_face_area_mm2=rootarea,owner_area_mm2=ownerarea,clipped_overlap_area_mm2=area,root_area_outside_initial_overlap_mm2=rootarea-area,quadrature_points=len(rows),first_moment_mm3=m1.tolist(),max_barycentric_violation=maxbary,max_virtualwork_error=maxwork,max_force_error=maxforce,max_moment_error=maxmoment,transitions=transitions)
   results.append(result);records.append(dict(mesh_level=level,sign=sign,rows=rows,root_all_triangles_mm=rt.tolist(),owner_all_triangles_mm=ft.tolist(),outside_policy='Outside overlap root material retained in full face triangle ledger; not attached or assigned pressure. Remaining Frame/top/wall features require full-boundary integration.'))
 dump(out/'quadrature.json',records);checks=dict(full_overlap_both_meshes=all(abs(r['clipped_overlap_area_mm2']-27.2)<1e-8 for r in results),all_barycentric=all(r['max_barycentric_violation']<1e-8 for r in results),virtualwork=all(r['max_virtualwork_error']<1e-8 for r in results),force_moment=all(r['max_force_error']<1e-10 and r['max_moment_error']<1e-8 for r in results),all_samples_retained=all(t['retained_samples']==r['quadrature_points'] for r in results for t in r['transitions']),finite_escape_detected=all(r['transitions'][-1]['edge_vertex_samples']>0 for r in results))
 dump(out/'summary.json',dict(status='ACTUAL_P1_CLIPPED_MATERIAL_QUADRATURE_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_CLIPPED_MATERIAL_QUADRATURE_FAIL',candidate=ref(src),inputs=ref(out/'inputs.json'),quadrature=ref(out/'quadrature.json'),checks=checks,results=results,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Reference-area quadrature of complete initial planar shoulder overlap only, not entire Root/Frame boundary contact.','Nearest triangle edges include triangulation edges; adjacent physical face normal cones and nonsmooth derivative not implemented. Finite transitions are inventory, not certified reaction transfer.','Unit virtual forces test kinematics only. No pressure/stress/allowable/fullmodel or global energy certification.','All78 actual CAD parts unchanged; old sourcefield not transferred. Full fivebody rebuild and22gates remain.']));print(json.dumps(dict(checks=checks,results=results)));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
