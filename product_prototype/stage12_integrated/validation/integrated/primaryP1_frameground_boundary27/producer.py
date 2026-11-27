"""Full finite material contact blocks for adjacent actual P1 support bodies.

Actual Motor has rigid six-DOF kinematics, no invented case stiffness. Every
source boundary sample remains; unavailable oriented charts have NaN gaps.
"""
import sys,json,shutil,time
import numpy as np
from scipy.sparse import coo_matrix,save_npz
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import boundary
from signed_boundary27 import SignedBoundary


def motor_surface(cad):
    import gmsh
    gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('actual_stock_motor_boundary')
    gmsh.model.occ.importShapes(str(REPO/cad['part_references']['F0_MICRO_MOTOR']['path']));gmsh.model.occ.synchronize();gmsh.option.setNumber('Mesh.MeshSizeMax',2.);gmsh.option.setNumber('Mesh.MeshSizeMin',.2);gmsh.model.mesh.generate(2)
    nt,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.asarray(nt)[order];p=np.asarray(xyz).reshape(-1,3)[order];types,_,elements=gmsh.model.mesh.getElements(2);f=np.concatenate([np.searchsorted(nt,np.asarray(e).reshape(-1,3)) for typ,e in zip(types,elements) if typ==2]);gmsh.finalize();return p,f


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists();tag,first,second=sys.argv[1:4]
    allowed=[('OPEN_FRAME','GROUND_PLATE'),('GROUND_PLATE','TEST_BASE'),('Motor','OPEN_FRAME'),('Motor','MOTOR_CAP'),('MOTOR_CAP','OPEN_FRAME')];assert (first,second) in allowed
    out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(src.read_text());cad=json.loads((REPO/model['candidate']['path']).read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
    dump(out/'inputs.json',dict(candidate=model['candidate'],fivebody=ref(src),first=first,second=second,producer=ref(out/'producer.py'),operators=[ref(ROOT/f'scripts/{n}.py') for n in ['signed_boundary27','finite_face_union27']],
        physical_scope='Full fixed source material boundary, actual finite owner closed surface, rigid stock Motor, no pressure or new equilibrium.'))
    if first=='Motor':
        motorp,motorf=motor_surface(cad);np.savez_compressed(out/'actual_motor_surface.npz',points_mm=motorp,triangles=motorf)
    results=[];saved={}
    for mr in model['results']:
        level=mr['mesh_level'];assert sha(REPO/mr['reference_model']['path'])==mr['reference_model']['SHA256'];a=np.load(REPO/mr['reference_model']['path']);N=len(a['reference_coordinates_mm'])
        if first=='Motor':p,f=motorp,motorf
        else:p=a[first+'_points_mm'];f=boundary(p,a[first+'_tetra'])
        op=a[second+'_points_mm'];of=boundary(op,a[second+'_tetra']);owner=SignedBoundary(op,of);tri=p[f];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2;rw=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]]);Q=np.einsum('ab,tbc->tac',rw,tri).reshape(-1,3)
        valid=np.zeros(len(Q),bool);gap=np.full(len(Q),np.nan);distance=np.zeros(len(Q));rows=[];cols=[];values=[];reasons={};work=0.;moment=0.;probes=0
        for i,q in enumerate(Q):
            if i%256==0:assert not (ROOT/'runtime/STOP').exists()
            ev=owner.chart(q);reasons[ev['reason']]=reasons.get(ev['reason'],0)+1
            distance[i]=owner.query(q)['distance_mm'] if not ev['accepted'] else abs(ev['gap_mm'])
            if not ev['accepted']:continue
            valid[i]=True;gap[i]=ev['gap_mm'];n=ev['point_gradient'];w=ev['weights'];fi=ev['face']
            ids=(int(a[second+'_offset'])+3*of[fi,:,None]+np.arange(3)).reshape(-1);g=(-w[:,None]*n).reshape(-1);rows.extend([i]*len(ids));cols.extend(ids.tolist());values.extend(g.tolist())
            if first=='Motor':
                mo=int(a['motor_offset']);gv=np.r_[n,np.cross(q-[0,0,20],n)];rows.extend([i]*6);cols.extend(range(mo,mo+6));values.extend(gv.tolist())
            else:
                ids=(int(a[first+'_offset'])+3*f[i//3,:,None]+np.arange(3)).reshape(-1);g=(rw[i%3,:,None]*n).reshape(-1);rows.extend([i]*len(ids));cols.extend(ids.tolist());values.extend(g.tolist())
            moment=max(moment,float(np.linalg.norm(np.cross(q,n)+np.cross(op[of[fi]],-w[:,None]*n).sum(axis=0))))
            if i%max(1,len(Q)//60)==0 and abs(gap[i])>1e-5:
                direction=np.array([.002,-.003,.001]);eps=1e-4;plus=owner.chart(q+eps*direction);minus=owner.chart(q-eps*direction)
                if plus['accepted'] and minus['accepted']:
                    work=max(work,abs((plus['gap_mm']-minus['gap_mm'])/(2*eps)-n@direction));probes+=1
        J=coo_matrix((values,(rows,cols)),shape=(len(Q),N)).tocsr();J.eliminate_zeros();save_npz(out/f'h{level}_gap_J.npz',J)
        errors=[]
        for axis in np.eye(3):
            v=np.zeros(N)
            for body in ['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE']:
                pp=a[body+'_points_mm'];off=int(a[body+'_offset']);v[off:off+3*len(pp)]=np.tile(axis,len(pp))
            mo=int(a['motor_offset']);v[mo:mo+3]=axis;errors.append(float(np.max(abs(J@v))))
            v*=0
            for body in ['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE']:
                pp=a[body+'_points_mm'];off=int(a[body+'_offset']);v[off:off+3*len(pp)]=np.cross(np.broadcast_to(axis,pp.shape),pp).reshape(-1)
            v[mo:mo+3]=np.cross(axis,[0,0,20]);v[mo+3:mo+6]=axis;errors.append(float(np.max(abs(J@v))))
        pre=f'h{level}_'
        for name,value in dict(source_material_points_mm=Q,source_material_weights_mm2=np.repeat(area/3,3),source_faces=f,source_points_mm=p,gap_mm=gap,accepted=valid,unsigned_distance_mm=distance).items():saved[pre+name]=value
        results.append(dict(mesh_level=level,source=first,owner=second,material_samples=len(Q),source_boundary_triangles=len(f),owner_boundary_triangles=len(of),material_area_mm2=float(area.sum()),
            all_samples_retained=True,accepted_oriented_charts=int(valid.sum()),unavailable_charts=int((~valid).sum()),chart_reasons=reasons,
            negative_gap_samples=int(np.sum(gap<-1e-10)),maximum_penetration_mm=float(max(0,-np.nanmin(gap))),nominal_active_rows=int(np.sum(valid&(abs(gap)<=1e-10))),
            max_common_rigid_mode_error=max(errors),max_virtualwork_error=work,offcontact_virtualwork_probes=probes,max_unit_action_reaction_moment_error_Nmm=moment,
            full_row_J=ref(out/f'h{level}_gap_J.npz'),physical_model_ready=False))
    np.savez_compressed(out/'material_gap_ledger.npz',**saved)
    checks=dict(full_rows=all(r['all_samples_retained'] for r in results),rigid_and_virtualwork=all(r['max_common_rigid_mode_error']<1e-8 and r['max_virtualwork_error']<1e-8 and r['max_unit_action_reaction_moment_error_Nmm']<1e-8 for r in results),
        nominal_nonpenetration=all(r['negative_gap_samples']==0 for r in results))
    dump(out/'summary.json',dict(status='ACTUAL_P1_ADJACENT_FINITE_BOUNDARY_BLOCK_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_ADJACENT_FINITE_BOUNDARY_BLOCK_FAIL',candidate=model['candidate'],inputs=ref(out/'inputs.json'),material_ledger=ref(out/'material_gap_ledger.npz'),checks=checks,results=results,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Every material row retained; unavailable charts remain NaN and block solve pending per-step finite-domain resolution. Not pressure or equilibrium.',
        'Polyhedral source degree2 quadrature is not moving overlap/contact integration convergence or exact curved CAD. Actual Motor has rigid proxy kinematics, no source case stiffness/bearing rating qualification.',
        'No contact/friction/material/physical Baseanchor/globalenergy/full3Finger gate qualified.']))
    print(json.dumps(dict(checks=checks,results=results)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
