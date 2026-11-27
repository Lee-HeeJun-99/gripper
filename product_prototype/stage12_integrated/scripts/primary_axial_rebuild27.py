"""Fresh actual CAD bearing footprints for fourteen conditional axial branches.

Only geometric material quadrature and new-mesh pullback. No thread, preload,
bearing strength or complete model solve. A missing finite owner rejects a row.
"""
import sys,json,shutil,time
import numpy as np
import gmsh
from scipy.sparse import csr_matrix,save_npz
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import Union,boundary


def specifications():
    dc3=3-1.226869*.5;A3=np.pi*dc3**2/4;dc5=5-1.226869*.8;A5=np.pi*dc5**2/4
    rows=[]
    for i,y in enumerate([-16,16]):rows.append(dict(name=f'RF{i}',first='F0_ROOT_BACK',second='OPEN_FRAME',head=f'F0_RF{i}_BOLT',nut=f'F0_RF{i}_NUT',za=-3,zb=-12,center=[64,y],k=200000*A3/10.2))
    for x in [-7,7]:
        for y in [-29.5,-13.5]:rows.append(dict(name=f'CAP{x}_{y}',first='MOTOR_CAP',second='OPEN_FRAME',head=f'MOTOR_CAP_BOLT_{x}_{y}',nut=f'MOTOR_CAP_NUT_{x}_{y}',za=29,zb=11,center=[x,y],k=200000*A3/19.2))
    for i,xy in enumerate([[-25,-28],[-25,14],[60,-28],[60,0]]):rows.append(dict(name=f'GROUND{i}',first='GROUND_PLATE',second='OPEN_FRAME',head=f'GROUND_NUT_{i}',nut=f'GROUND_BOLT_{i}',za=46,zb=34,center=xy,k=200000*A5/14.35))
    for i,xy in enumerate([[-44,-30],[-44,10],[86,-30],[86,10]]):rows.append(dict(name=f'FIXTURE{i}',first='TEST_BASE',second='GROUND_PLATE',head=f'FIXTURE_NUT_{i}',nut=f'FIXTURE_BOLT_{i}',za=66,zb=40,center=xy,k=200000/(13/(np.pi*25/4)+(13+2.2)/A5)))
    return rows


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(src.read_text());spec=specifications();names=sorted(set(n for r in spec for n in [r['first'],r['second'],r['head'],r['nut']]))
    assert all(sha(REPO/cad['part_references'][n]['path'])==cad['part_references'][n]['SHA256'] for n in names)
    modelsrc=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(modelsrc.read_text())
    dump(out/'inputs.json',dict(candidate=ref(src),parts={n:cad['part_references'][n] for n in names},fivebody=ref(modelsrc),producer=ref(out/'producer.py'),operator=ref(ROOT/'scripts/finite_face_union27.py'),
        proven_architecture=ref(ROOT/'scripts/primary_front_compliance.py'),specifications=spec,pressure_model='Positive area-weighted axial mean footprint, no physical flank/thread law or lateral tie. Conditional E200000 and ISO basic minor-core compliance unchanged.',gap_tolerance_mm=1e-10))
    gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('P1_axial_fresh_actual_footprints')
    objects=[]
    for name in names:
        v=gmsh.model.occ.importShapes(str(REPO/cad['part_references'][name]['path']));assert len(v)==1;objects+=v
    frag,mapping=gmsh.model.occ.fragment(objects,[]);gmsh.model.occ.synchronize()
    ss={n:set(abs(t) for d,t in gmsh.model.getBoundary(mapping[i],combined=True,oriented=False) if d==2) for i,n in enumerate(names)}
    patches=[]
    for r in spec:
        for side,n,hw,z in [('a',r['first'],r['head'],r['za']),('b',r['second'],r['nut'],r['zb'])]:
            faces=[]
            for t in ss[n]&ss[hw]:
                bb=gmsh.model.getBoundingBox(2,t)
                if abs(bb[2]-z)<1e-5 and abs(bb[5]-z)<1e-5:faces.append(t)
            assert faces,(r['name'],side,n,hw,z)
            patches.append(dict(branch=r['name'],side=side,body=n,hardware=hw,z=z,center=r['center'],faces=faces,CAD_area_mm2=sum(gmsh.model.occ.getMass(2,t) for t in faces)))
    gmsh.option.setNumber('Mesh.MeshSizeMax',1.5);gmsh.option.setNumber('Mesh.MeshSizeMin',.2);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',24);gmsh.model.mesh.generate(2)
    nt,xyz,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.asarray(nt)[order];xyz=np.asarray(xyz).reshape(-1,3)[order]
    for patch in patches:
        tris=[]
        for face in patch['faces']:
            types,_,es=gmsh.model.mesh.getElements(2,face)
            tris.extend(np.searchsorted(nt,np.asarray(e).reshape(-1,3)) for typ,e in zip(types,es) if typ==2)
        t=xyz[np.concatenate(tris)];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
        bary=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])
        q=np.einsum('ab,tbc->tac',bary,t).reshape(-1,3);w=np.repeat(area/3,3);raw_centroid=w@q/w.sum()
        H=np.vstack([np.ones(len(q)),q[:,:2].T]);target=np.r_[1.,patch['center']];w/=w.sum();w+=w*(H.T@np.linalg.solve((H*w)@H.T,target-H@w));assert w.min()>0
        patch.update(material_points_mm=q.tolist(),normalized_positive_area_weights=w.tolist(),polygonal_area_mm2=float(area.sum()),raw_area_centroid_mm=raw_centroid.tolist(),centroid_correction_mm=float(np.linalg.norm(raw_centroid[:2]-patch['center'])),corrected_axis_error=float(np.linalg.norm(w@q[:,:2]-patch['center'])))
    gmsh.finalize();dump(out/'actual_bearing_material_quadrature.json',patches)
    reports=[];mapping_records=[]
    for m in model['results']:
        level=m['mesh_level'];a=np.load(REPO/m['reference_model']['path']);N=len(a['reference_coordinates_mm']);namesbody=['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'];unions={n:Union(a[n+'_points_mm'],boundary(a[n+'_points_mm'],a[n+'_tetra'])) for n in namesbody};D=np.zeros((14,N));mapped_patches=[];miss=0;maxdistance=0.;maxcentroid=0.
        for patch in patches:
            n=patch['body'];p=unions[n].points;w=np.array(patch['normalized_positive_area_weights']);q=np.array(patch['material_points_mm']);nodal=np.zeros(len(p));errors=[];failed=[]
            for i,point in enumerate(q):
                ev=unions[n].query(point);errors.append(ev['distance_mm'])
                if ev['distance_mm']>1e-10:
                    failed.append(dict(sample=i,point_mm=point.tolist(),nearest_distance_mm=ev['distance_mm']));continue
                np.add.at(nodal,unions[n].faces[ev['face']],w[i]*ev['weights'])
            complete=not failed;miss+=len(failed);maxdistance=max(maxdistance,max(errors));centroid=nodal@p;centroid_error=float(np.linalg.norm(centroid-np.r_[patch['center'],patch['z']])) if complete else None
            if complete:maxcentroid=max(maxcentroid,centroid_error)
            bi=next(i for i,r in enumerate(spec) if r['name']==patch['branch']);sign=1 if patch['side']=='a' else -1
            # Incomplete pullback is NEVER used as a connector. Entire branch remains unavailable.
            if complete:D[bi,int(a[n+'_offset'])+3*np.arange(len(p))+2]+=sign*nodal
            mapped_patches.append(dict(branch=patch['branch'],side=patch['side'],body=n,material_samples=len(q),missing_finite_owners=len(failed),complete=complete,max_owner_distance_mm=max(errors),nodal_weight_sum=float(nodal.sum()),centroid_error_mm=centroid_error))
            if failed:mapping_records.append(dict(mesh_level=level,branch=patch['branch'],side=patch['side'],failed_samples=failed))
        available=np.array([all(r['complete'] for r in mapped_patches if r['branch']==s['name']) for s in spec]);D[~available]=0
        save_npz(out/f'h{level}_axial_D.npz',csr_matrix(D));np.savez_compressed(out/f'h{level}_axial_availability.npz',available=available,k_N_mm=np.array([r['k'] for r in spec]))
        reports.append(dict(mesh_level=level,branches=14,material_patches=28,complete_branches=int(available.sum()),unavailable_branches=int((~available).sum()),missing_finite_owner_samples=miss,max_material_owner_distance_mm=maxdistance,max_complete_patch_centroid_error_mm=maxcentroid,patches=mapped_patches,
            conditional_axial_D=ref(out/f'h{level}_axial_D.npz'),availability=ref(out/f'h{level}_axial_availability.npz'),physical_model_ready=bool(available.all())))
    dump(out/'missing_owner_samples.json',mapping_records)
    checks=dict(actual_14branches_28positive_footprints=len(patches)==28 and all(min(r['normalized_positive_area_weights'])>0 and r['corrected_axis_error']<1e-8 for r in patches),
        finite_material_owners=all(r['missing_finite_owner_samples']==0 and r['complete_branches']==14 for r in reports),
        complete_patch_pullback_centroids=all(r['max_complete_patch_centroid_error_mm']<1e-8 for r in reports))
    dump(out/'summary.json',dict(status='ACTUAL_P1_FRESH_AXIAL_FOOTPRINT_PULLBACK_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_FRESH_AXIAL_FOOTPRINT_PULLBACK_FAIL',candidate=ref(src),inputs=ref(out/'inputs.json'),quadrature=ref(out/'actual_bearing_material_quadrature.json'),missing=ref(out/'missing_owner_samples.json'),checks=checks,results=reports,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Fresh common CAD faces and positive quadrature, not exact curved boundary integration or convergence. CAD area vs polygonal area recorded independently.',
        'Smooth hardware envelopes and conditional axial compliance do not certify thread flank/core/engagement/preload/material bearing strength.',
        'Incomplete branches are explicitly unavailable and block solve, not deleted or treated as zero stiffness. No fictitious lateral restraint or sourcefield transfer.']))
    print(json.dumps(dict(checks=checks,results=[{k:v for k,v in r.items() if k!='patches'} for r in reports])));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
