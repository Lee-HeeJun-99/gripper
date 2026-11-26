"""Linear 3D tetrahedral torsion controls, actual STEP or analytic cylinder.
Actual shaft: pin bore fixed by IDEAL RIGID TEST FIXTURE, input end torque.
This is a local coupon, NOT bearing/contact/coupling qualification.
Gmsh's own OCC is used in this process; do NOT import the separate OCP wheel.
"""
import argparse,hashlib,json,shutil,time
from pathlib import Path
import numpy as np
import gmsh,skfem,scipy
from skfem import MeshTet,Basis,FacetBasis,ElementTetP1,ElementTetP2,ElementVector,LinearForm,asm,condense,solve
from skfem.models.elasticity import linear_elasticity,lame_parameters
from skfem.helpers import dot
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['reference','shaft'],required=True)
    ap.add_argument('--h-mm',type=float,required=True);ap.add_argument('--order',type=int,choices=[1,2],default=1);ap.add_argument('--solver',choices=['direct','amg'],default='direct');ap.add_argument('--tag',required=True);a=ap.parse_args()
    out=ROOT/'validation/shaft'/a.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py');start=time.monotonic()
    step=ROOT.parent/'stage1_manufacturing/cad/parts/revAA_mbd1/F0_SHAFT.step'
    gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1)
    build=gmsh.option.getString('General.BuildInfo');gmsh.model.add('torsion')
    if a.mode=='shaft':
        gmsh.model.occ.importShapes(str(step));low=-18.;high=18.5
    else:
        gmsh.model.occ.addCylinder(80,-18,20,0,20,0,2.2);low=-18.;high=2.
    gmsh.model.occ.synchronize();fixed_surfaces=[];loaded_surfaces=[];faces=[]
    for dim,tag in gmsh.model.getEntities(2):
        b=np.array(gmsh.model.getBoundingBox(dim,tag));typ=gmsh.model.getType(dim,tag)
        faces.append(dict(tag=tag,type=typ,bounds_mm=b.tolist()))
        if abs(b[1]-low)<1e-5 and abs(b[4]-low)<1e-5:loaded_surfaces.append(tag)
        if a.mode=='reference':
            if abs(b[1]-high)<1e-5 and abs(b[4]-high)<1e-5:fixed_surfaces.append(tag)
        elif typ=='Cylinder' and b[3]-b[0]>7 and 1.7<b[1]<1.8 and 3.2<b[4]<3.3 and b[5]-b[2]<1.6:
            fixed_surfaces.append(tag)
    assert fixed_surfaces and loaded_surfaces,(fixed_surfaces,loaded_surfaces,faces)
    gmsh.option.setNumber('Mesh.MeshSizeMax',a.h_mm);gmsh.option.setNumber('Mesh.MeshSizeMin',a.h_mm*.35)
    gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',20);gmsh.option.setNumber('Mesh.Algorithm3D',1)
    gmsh.model.mesh.generate(3)
    tags,coords,_=gmsh.model.mesh.getNodes();order=np.argsort(tags);tags=np.array(tags)[order]
    coords=np.array(coords).reshape(-1,3)[order]*.001
    types,_,elems=gmsh.model.mesh.getElements(3)
    tetra=np.concatenate([np.array(e).reshape(-1,4) for t,e in zip(types,elems) if t==4]);tetra=np.searchsorted(tags,tetra)
    fnodes=[];fixed_tris=[]
    for face in fixed_surfaces:
        _,_,es=gmsh.model.mesh.getElements(2,face)
        for es1 in es:
            ids=np.searchsorted(tags,es1);fnodes.extend(ids.tolist());fixed_tris.extend(ids.reshape(-1,3).tolist())
    gmsh.finalize()
    m=MeshTet(coords.T,tetra.T);element=ElementVector(ElementTetP1() if a.order==1 else ElementTetP2());basis=Basis(m,element)
    keys={tuple(sorted(t)) for t in fixed_tris}
    fixed_facets=np.array([i for i,t in enumerate(m.facets.T) if tuple(sorted(t)) in keys])
    fixed=basis.get_dofs(facets=fixed_facets).all()
    facets=m.facets_satisfying(lambda x:abs(x[1]-low*.001)<1e-10,boundaries_only=True)
    fb=FacetBasis(m,element,facets=facets)
    @LinearForm
    def unit_load(v,w):
        f=np.array([w.x[2]-.020,np.zeros_like(w.x[0]),-(w.x[0]-.080)])
        return dot(f,v)
    split=np.array(basis.split_indices());dofcoords=basis.doflocs[:,split[0]].T
    f=asm(unit_load,fb);nodalf=f[split]
    input_torque=float(np.sum((dofcoords[:,2]-.020)*nodalf[0]-(dofcoords[:,0]-.080)*nodalf[2]))
    target=.001;f*=target/input_torque
    E=193e9;nu=.3;lam,mu=lame_parameters(E,nu)
    K=asm(linear_elasticity(lam,mu),basis)
    A,rhs,initial,free=condense(K,f,D=fixed);iterations=[]
    if a.solver=='direct':u=solve(A,rhs,initial,free)
    else:
        import pyamg
        from scipy.sparse.linalg import cg
        B=np.zeros((basis.N,6))
        for j in range(3):B[split[j],j]=1
        x,y,z=(dofcoords-np.array([.080,0,.020])).T
        B[split[1],3]=-z;B[split[2],3]=y
        B[split[0],4]=z;B[split[2],4]=-x
        B[split[0],5]=-y;B[split[1],5]=x
        B=B[free];B/=np.linalg.norm(B,axis=0)
        mg=pyamg.smoothed_aggregation_solver(A,B=B,symmetry='symmetric',max_coarse=200)
        def callback(v):
            iterations.append(float(np.linalg.norm(A@v-rhs)/np.linalg.norm(rhs)))
        solution,info=cg(A,rhs,M=mg.aspreconditioner(),rtol=1e-10,atol=0,maxiter=3000,callback=callback)
        assert info==0,('CG failure',info,iterations[-1])
        u=initial;u[free]=solution
    linear_relative_residual=float(np.linalg.norm((K@u-f)[free])/np.linalg.norm(f[free]))
    reaction=K@u-f
    rf=reaction[split];forces=f[split]
    balance=np.sum(rf+forces,axis=1)
    torque_balance=float(np.sum((dofcoords[:,2]-.020)*(rf[0]+forces[0])-(dofcoords[:,0]-.080)*(rf[2]+forces[2])))
    # Element strain/stress, no smoothing or deleting high-stress elements.
    grad=basis.interpolate(u).grad;eps=(grad+np.swapaxes(grad,0,1))/2
    trace=np.einsum('iiek->ek',eps);stress=2*mu*eps+lam*np.eye(3)[:,:,None,None]*trace
    dev=stress-np.eye(3)[:,:,None,None]*np.einsum('iiek->ek',stress)/3
    vm=np.sqrt(1.5*np.einsum('ijek,ijek->ek',dev,dev)).max(axis=1)
    det=np.linalg.det(np.transpose(coords[tetra[:,1:]]-coords[tetra[:,0,None]],(0,2,1)))
    volumes=abs(det)/6;vol=float(volumes.sum())
    edge2=sum(np.sum((coords[tetra[:,i]]-coords[tetra[:,j]])**2,axis=1) for i in range(4) for j in range(i))
    quality=12*(3*volumes)**(2/3)/edge2
    energy=.5*float(u@K@u);work=.5*float(f@u);twist=float(f@u/target)
    analytic=(target*.020/(mu*np.pi*.0022**4/2)) if a.mode=='reference' else None
    err=abs(twist/analytic-1) if analytic else None
    checks=dict(linear_residual=linear_relative_residual<1e-8,force_balance=bool(np.linalg.norm(balance)<1e-8),torque_balance=abs(torque_balance)<1e-10,
        energy=abs(energy-work)/energy<1e-8,quality=bool(quality.min()>.01),reference=(err<.01 if err is not None else True))
    np.savez_compressed(out/'field.npz',points_m=coords,tetra=tetra,displacement_m=u[basis.nodal_dofs].T,vm_Pa=vm,volume_m3=volumes)
    result=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        case='revAA_heel_relief2' if a.mode=='shaft' else 'analytic-cylinder-control',mode=a.mode,h_mm=a.h_mm,order=a.order,
        scope='STATIC LOCAL TORSION COUPON; NOT ACTUAL PIN CONTACT OR SHAFT STRENGTH RELEASE',
        material=dict(E_Pa=E,nu=nu,basis='assumed linear elasticity, not certified lot properties'),
        input_torque_Nm=target,twist_rad=twist,analytic_twist_rad=analytic,reference_relative_error=err,
        force_balance_N=balance.tolist(),torque_balance_Nm=torque_balance,energy_J=energy,
        energy_relative_error=abs(energy-work)/energy,mesh_volume_m3=vol,min_quality=float(quality.min()),
        peak_unsmoothed_vm_Pa=float(vm.max()),p95_vm_Pa=float(np.quantile(vm,.95)),
        nodes=len(coords),elements=len(tetra),elapsed_s=time.monotonic()-start,
        linear_relative_residual=linear_relative_residual,solver=a.solver,iteration_relative_residuals=iterations,
        fixed_surface_tags=fixed_surfaces,loaded_surface_tags=loaded_surfaces,face_inventory=faces,
        source_SHA256=sha(Path(__file__)),STEP_SHA256=sha(step) if a.mode=='shaft' else None,
        binary_SHA256=sha(Path(gmsh.libpath)),gmsh_build=build,scikit_fem=skfem.__version__,scipy=scipy.__version__,numpy=np.__version__,
        field_SHA256=sha(out/'field.npz'),command='PYTHONPATH=/tmp/regrip_stage2_fem OPENBLAS_NUM_THREADS=1 python scripts/shaft_fem.py --mode '+a.mode+' --h-mm '+str(a.h_mm)+' --order '+str(a.order)+' --solver '+a.solver+' --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='face_inventory'},indent=2))
if __name__=='__main__':main()
