"""Build full actual Root boundary material inventory and finite Frame operators."""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import Union,boundary


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    candidate=ROOT/'cad/exports/primaryP1_ycapture24/summary.json'
    cad=json.loads(candidate.read_text())
    assert len(cad['part_references'])==78
    assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
    inputs={};arrays={};reports=[];rng=np.random.default_rng(2701)
    for level in [2,3]:
        src=ROOT/f'validation/integrated/primaryP1_ycapture_mesh{level}/summary.json'
        ms=json.loads(src.read_text());assert sha(REPO/ms['mesh']['path'])==ms['mesh']['SHA256']
        inputs[str(level)]=dict(summary=ref(src),mesh=ms['mesh'])
    dump(out/'inputs.json',dict(candidate=ref(candidate),meshes=inputs,
        producer=ref(out/'producer.py'),operator=ref(ROOT/'scripts/finite_face_union27.py'),
        model='Every Root boundary triangle: three degree2 fixed material points. All Frame boundary triangles. No force law.'))
    for level in [2,3]:
        data=np.load(REPO/inputs[str(level)]['mesh']['path'])
        rp,fp=(data[n+'_points_mm'] for n in ['F0_ROOT_BACK','OPEN_FRAME'])
        rf,ff=(boundary(data[n+'_points_mm'],data[n+'_tetra']) for n in ['F0_ROOT_BACK','OPEN_FRAME'])
        rt=rp[rf];area=np.linalg.norm(np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]),axis=1)/2
        weights=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])
        q=np.einsum('ab,tbc->tac',weights,rt).reshape(-1,3)
        material_area=np.repeat(area/3,3);union=Union(fp,ff)
        distance=[];owners=[];bary=[];differentiable=[];feature=[];pullback=[];maxwork=0.;maxforce=0.;maxmoment=0.;tested=0
        for i,point in enumerate(q):
            if i%256==0:assert not (ROOT/'runtime/STOP').exists()
            ev=union.query(point);distance.append(ev['distance_mm']);owners.append(ev['face']);bary.append(ev['weights']);differentiable.append(ev['differentiable']);feature.append(ev.get('feature','ZERO'))
            if ev['differentiable'] and tested<160 and i%max(1,len(q)//180)==0:
                t=union.triangles[ev['face']];D=rng.normal(size=(6,3))*.005
                rw=weights[i%3];dq=rw@D[:3]
                analytic=ev['point_gradient']@dq+np.sum(ev['owner_gradient']*D[3:])
                from finite_face_union27 import closest
                eps=1e-4
                # Fixed feature envelope derivative; independent global-owner checks are in audit.
                fd=(closest(point+eps*dq,(t+eps*D[3:])[None])[0][0]-closest(point-eps*dq,(t-eps*D[3:])[None])[0][0])/(2*eps)
                maxwork=max(maxwork,abs(fd-analytic));forces=np.vstack([rw[:,None]*ev['point_gradient'],ev['owner_gradient']])
                maxforce=max(maxforce,np.linalg.norm(forces.sum(axis=0)))
                maxmoment=max(maxmoment,np.linalg.norm(np.cross(np.vstack([rt[i//3],t]),forces).sum(axis=0)))
                tested+=1;pullback.append(dict(sample=i,virtualwork_error=abs(fd-analytic)))
        distance=np.array(distance);differentiable=np.array(differentiable)
        prefix=f'h{level}_'
        for name,value in dict(root_faces=rf,frame_faces=ff,material_points_mm=q,material_weights_mm2=material_area,
                owner_faces=np.array(owners),owner_weights=np.array(bary),distance_mm=distance,
                differentiable=differentiable,features=np.array(feature)).items():arrays[prefix+name]=value
        reports.append(dict(mesh_level=level,root_boundary_triangles=len(rf),frame_boundary_triangles=len(ff),
            material_samples=len(q),root_complete_boundary_area_mm2=float(area.sum()),integrated_area_mm2=float(material_area.sum()),
            minimum_distance_mm=float(distance.min()),maximum_distance_mm=float(distance.max()),
            zero_or_nonsmooth_samples=int((~differentiable).sum()),feature_counts={k:feature.count(k) for k in sorted(set(feature))},
            virtualwork_probes=tested,max_virtualwork_error=maxwork,max_force_error=maxforce,max_moment_error=maxmoment,
            every_material_sample_retained=len(q)==3*len(rf),physical_reaction_claimed=False))
    np.savez_compressed(out/'full_boundary_operator.npz',**arrays)
    checks=dict(full_material_inventory=all(r['every_material_sample_retained'] for r in reports),
        area_accounting=all(abs(r['root_complete_boundary_area_mm2']-r['integrated_area_mm2'])<1e-8 for r in reports),
        virtualwork=all(r['max_virtualwork_error']<1e-8 and r['virtualwork_probes']>50 for r in reports),
        action_reaction=all(r['max_force_error']<1e-10 and r['max_moment_error']<1e-8 for r in reports))
    dump(out/'summary.json',dict(status='ACTUAL_P1_FULL_BOUNDARY_FINITE_UNION_OPERATOR_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_FULL_BOUNDARY_FINITE_UNION_OPERATOR_FAIL',
        candidate=ref(candidate),inputs=ref(out/'inputs.json'),operator_data=ref(out/'full_boundary_operator.npz'),checks=checks,results=reports,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Unsigned distance envelope only: no signed solid nonpenetration/CCD/contact pressure or equilibrium. Zero-distance and distinct-nearest-face ties refuse a single Jacobian.',
        'Complete fixed Root material quadrature is not moving-overlap quadrature or exact curved CAD integration. Polygonal boundary, not smooth BRep fillet.',
        'No old sourcefield transferred; full same-revision fivebody assembly/axial connectors/loads/rigid modes still required. No mesh/time convergence or energy qualification.']))
    print(json.dumps(dict(checks=checks,results=reports)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
