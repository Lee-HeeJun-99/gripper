"""Whole AK Palm conditional P1 elasticity with finite partitioned washer load.
Gmsh OCC and separate scikit-fem process; never imports the OCP wheel.
No material, root boundary or local peak stress is promoted to whole-Palm proof.
"""
import argparse,json,math,time,shutil
from pathlib import Path
import numpy as np
import gmsh,skfem,scipy
from skfem import MeshTet,Basis,FacetBasis,ElementTetP1,ElementVector,LinearForm,asm,condense,solve
from skfem.models.elasticity import linear_elasticity,lame_parameters
from skfem.helpers import dot
from baseline_registry import ROOT,REPO,ref,dump,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--h-mm',type=float,required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/transmission'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py');start=time.monotonic()
    source=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(source.read_text());step=REPO/d['part_references']['PALM']['path'];assert sha(step)==d['part_references']['PALM']['SHA256'];dump(out/'inputs.json',dict(candidate=ref(source),STEP=ref(step),producer=ref(out/'producer.py'),criteria=dict(force_N=1e-8,moment_Nm=1e-10,residual=1e-8,energy=1e-8,volume_fraction=.01,min_quality=.01,response_convergence_fraction=.01)))
    gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('actual_tab')
    objects=gmsh.model.occ.importShapes(str(step));tool=gmsh.model.occ.addCylinder(127,-1,-12,0,0,5,4)
    support=gmsh.model.occ.addCylinder(0,0,-12,0,0,5,30);fragments,mapping=gmsh.model.occ.fragment(objects,[(3,tool),(3,support)]);keep=set(mapping[0])
    extra=[v for v in fragments if v[0]==3 and v not in keep]
    if extra:gmsh.model.occ.remove(extra,recursive=True)
    gmsh.model.occ.synchronize();fixed=[];loaded=[]
    for dim,tag in gmsh.model.getEntities(2):
        b=gmsh.model.getBoundingBox(dim,tag);area=gmsh.model.occ.getMass(dim,tag)
        if abs(b[2]+12)<1e-5 and abs(b[5]+12)<1e-5 and max(abs(b[0]),abs(b[1]),abs(b[3]),abs(b[4]))<30.00001:fixed.append(tag)
        if abs(b[2]+7)<1e-5 and abs(b[5]+7)<1e-5 and b[0]>122.999 and b[3]<131.001 and b[1]>-5.001 and b[4]<3.001:loaded.append(tag)
    assert fixed and len(loaded)==1,(fixed,loaded)
    gmsh.option.setNumber('Mesh.MeshSizeMax',a.h_mm);gmsh.option.setNumber('Mesh.MeshSizeMin',a.h_mm*.35);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',24);gmsh.option.setNumber('Mesh.Algorithm3D',1)
    gmsh_volume_mm3=sum(gmsh.model.occ.getMass(3,t) for _,t in gmsh.model.getEntities(3));gmsh.model.mesh.generate(3);tags,coords,_=gmsh.model.mesh.getNodes();order=np.argsort(tags);tags=np.array(tags)[order];coords=np.array(coords).reshape(-1,3)[order]*.001
    types,_,elements=gmsh.model.mesh.getElements(3);tetra=np.concatenate([np.array(e).reshape(-1,4) for t,e in zip(types,elements) if t==4]);tetra=np.searchsorted(tags,tetra)
    def triangles(faces):
        pieces=[]
        for face in faces:
            ts,_,es=gmsh.model.mesh.getElements(2,face)
            pieces.extend(np.searchsorted(tags,np.array(e).reshape(-1,3)) for t,e in zip(ts,es) if t==2)
        return np.concatenate(pieces)
    ft,lt=triangles(fixed),triangles(loaded);gmsh.finalize()
    used=np.unique(tetra);assert np.isin(ft,used).all() and np.isin(lt,used).all()
    coords=coords[used];tetra=np.searchsorted(used,tetra);ft=np.searchsorted(used,ft);lt=np.searchsorted(used,lt)
    m=MeshTet(coords.T,tetra.T);element=ElementVector(ElementTetP1());basis=Basis(m,element,intorder=2)
    def facet_ids(tris):
        keys={tuple(sorted(t)) for t in tris};return np.array([i for i,t in enumerate(m.facets.T) if tuple(sorted(t)) in keys])
    fixed_dofs=basis.get_dofs(facets=facet_ids(ft)).all();fb=FacetBasis(m,element,facets=facet_ids(lt),intorder=2)
    @LinearForm
    def load(v,w):return dot(np.array([np.zeros_like(w.x[0]),np.zeros_like(w.x[0]),-np.ones_like(w.x[0])]),v)
    f=asm(load,fb);split=np.array(basis.split_indices());f/=abs(f[split[2]].sum());x=basis.doflocs[:,split[0]].T
    E=70e9;nu=.33;lam,mu=lame_parameters(E,nu)
    # Reuse the bounded element-sum strategy of Stage2 shaft_fem.py;
    # identical element law/quadrature, no altered stiffness or criterion.
    from scipy.sparse import csr_matrix
    K=csr_matrix((basis.N,basis.N))
    for first in range(0,len(tetra),8000):
        subset=Basis(m,element,intorder=2,elements=np.arange(first,min(first+8000,len(tetra))))
        K=K+asm(linear_elasticity(lam,mu),subset)
    A,rhs,u,free=condense(K,f,D=fixed_dofs);u=solve(A,rhs,u,free);reaction=K@u-f
    balance=(reaction[split]+f[split]).sum(axis=1);moment=np.cross(x-np.array([0,0,0]),(reaction[split]+f[split]).T).sum(axis=0)
    energy=.5*float(u@K@u);work=.5*float(f@u);res=np.linalg.norm((K@u-f)[free])/np.linalg.norm(f[free])
    gradient=basis.interpolate(u).grad;eps=(gradient+np.swapaxes(gradient,0,1))/2;stress=2*mu*eps+lam*np.eye(3)[:,:,None,None]*np.einsum('iiek->ek',eps)
    dev=stress-np.eye(3)[:,:,None,None]*np.einsum('iiek->ek',stress)/3;vm=np.sqrt(1.5*np.einsum('ijek,ijek->ek',dev,dev)).max(axis=1)
    det=np.linalg.det(np.transpose(coords[tetra[:,1:]]-coords[tetra[:,0,None]],(0,2,1)));vol=abs(det)/6;mesh_volume=float(vol.sum())
    edge2=sum(np.sum((coords[tetra[:,i]]-coords[tetra[:,j]])**2,axis=1) for i in range(4) for j in range(i));quality=12*(3*vol)**(2/3)/edge2
    deformed=coords+u[basis.nodal_dofs].T;newdet=np.linalg.det(np.transpose(deformed[tetra[:,1:]]-deformed[tetra[:,0,None]],(0,2,1)));ratio=newdet/det
    checks=dict(force=bool(np.linalg.norm(balance)<1e-8),moment=bool(np.linalg.norm(moment)<1e-10),energy=abs(energy-work)/energy<1e-8,residual=bool(res<1e-8),quality=bool(quality.min()>.01),volume=abs(mesh_volume/(gmsh_volume_mm3*1e-9)-1)<.01,positive_signed_volume_ratio=bool(ratio.min()>0))
    np.savez_compressed(out/'field.npz',points_m=coords,tetra=tetra,displacement_m=u[basis.nodal_dofs].T,full_u=u,applied_f=f,fixed_dofs=fixed_dofs,vm_Pa=vm,signed_volume_ratio=ratio)
    np.savez_compressed(out/'verification.npz',force_balance=balance,moment_balance=moment,residual_free=reaction[free],force_free=f[free],energy=energy,work=work);result=dict(status='CONDITIONAL_WHOLE_PALM_PASS' if all(checks.values()) else 'CONDITIONAL_WHOLE_PALM_FAIL',scope='Actual entire AK Palm; hypothetical underside r20..30mm fixed annulus; actual outer mounting-hole r1.7..4mm unit pressure footprint; no assembly support or strength qualification',checks=checks,h_mm=a.h_mm,element='P1 tetrahedron, degree2 quadrature',assembly_element_block=8000,source=ref(source),STEP=ref(step),producer=ref(out/'producer.py'),gmsh_binary=ref(Path(gmsh.libpath)) if Path(gmsh.libpath).is_relative_to(REPO) else dict(SHA256=sha(Path(gmsh.libpath)),path=str(gmsh.libpath)),software=dict(gmsh=gmsh.__version__,skfem=skfem.__version__,scipy=scipy.__version__,numpy=np.__version__),
        material=dict(E_Pa=E,nu=nu,basis='ASSUMED sensitivity, not certified grade'),input_force_N=[0,0,-1],compliance_m_N=float(f@u),energy_J=energy,force_balance_N=balance.tolist(),moment_balance_Nm=moment.tolist(),linear_residual=float(res),mesh_volume_m3=mesh_volume,min_quality=float(quality.min()),minimum_signed_volume_ratio=float(ratio.min()),peak_unsmoothed_vm_Pa=float(vm.max()),nodes=len(coords),elements=len(tetra),DOF=int(basis.N),elapsed_s=time.monotonic()-start,field=ref(out/'field.npz'),
        limitations=['Central annular clamp is hypothetical; actual assembly base interface remains undefined','Finite washer pressure load, not actual bolt/contact/preload','Sharp clamp-edge stress cannot certify strength','No material/yield/fatigue or motor/limiter cap','Static linear test, no time convergence or powered operation'],whole_system_release=False)
    result['verification']=ref(out/'verification.npz');dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('field','limitations')},indent=2))
if __name__=='__main__':main()
