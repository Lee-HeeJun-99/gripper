"""Independent exhaustive-distance, concave alternatives and transition audit."""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import Union,boundary


def independent_distance(q,t):
    # Plane distance accepted only when oriented area coordinates lie inside.
    n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    h=np.einsum('ij,ij->i',q-t[:,0],n);p=q-h[:,None]*n
    inside=np.ones(len(t),bool)
    for i,j in [(0,1),(1,2),(2,0)]:
        inside &= np.einsum('ij,ij->i',np.cross(t[:,j]-t[:,i],p-t[:,i]),n)>=-1e-12
    d=np.where(inside,abs(h),np.inf)
    for i,j in [(0,1),(1,2),(2,0)]:
        e=t[:,j]-t[:,i];a=np.sum((q-t[:,i])*e,axis=1)/np.sum(e*e,axis=1)
        a=np.maximum(0,np.minimum(1,a));v=t[:,i]+a[:,None]*e
        d=np.minimum(d,np.linalg.norm(q-v,axis=1))
    return d


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py')
    source=ROOT/'validation/integrated/primaryP1_face_union27/summary.json';s=json.loads(source.read_text())
    assert sha(REPO/s['operator_data']['path'])==s['operator_data']['SHA256']
    inventory=np.load(REPO/s['operator_data']['path']);edges=json.loads((ROOT/'validation/integrated/primaryP1_shoulder_edges26/edges.json').read_text())
    reports=[];probes=[];rng=np.random.default_rng(2702)
    for level in [2,3]:
        ms=json.loads((ROOT/f'validation/integrated/primaryP1_ycapture_mesh{level}/summary.json').read_text());data=np.load(REPO/ms['mesh']['path']);p=data['OPEN_FRAME_points_mm'];f=boundary(p,data['OPEN_FRAME_tetra']);u=Union(p,f)
        # Archived edge owner indices use their original ordering, with independent reconstruction.
        tet=data['OPEN_FRAME_tetra'];allf=np.concatenate([tet[:,v] for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);_,ix,c=np.unique(np.sort(allf,axis=1),axis=0,return_index=True,return_counts=True);oldf=allf[ix[c==1]]
        conc=conv=ties=branches=zero=0;maxedge=0.;maxglobal=0.;maxwork=0.;maxobjective=0.;min_branch_separation=np.inf
        for r in [r for r in edges if r['mesh_level']==level]:
            e=np.array(r['edge_mm']).mean(axis=0);q=e+.1*np.array(r['normal_cone_test_direction']);local=Union(p,oldf[r['owner_triangles']]);ev=local.query(q);reference=independent_distance(q,local.triangles).min();maxedge=max(maxedge,abs(ev['distance_mm']-reference))
            if r['local_convex']:conv+=1
            else:
                conc+=1
                assert ev['distance_mm']<.1-1e-8
                if not ev['differentiable']:ties+=1
                # Perturb toward each incident face, forcing an actual finite alternative.
                n=np.array(r['outward_normals']);direction=n[0]-n[1];direction/=np.linalg.norm(direction)
                a,b=local.query(q+.001*direction),local.query(q-.001*direction)
                if a['differentiable'] and b['differentiable'] and a['face']!=b['face']:branches+=1
                min_branch_separation=min(min_branch_separation,np.linalg.norm(a['point']-b['point']))
            atedge=local.query(e)
            if not atedge['differentiable'] and atedge['reason']=='ZERO_DISTANCE_OR_GRAZING':zero+=1
            probes.append(dict(mesh_level=level,convex=r['local_convex'],edge_nodes=r['edge_nodes'],distance_mm=ev['distance_mm'],edge_hull_distance_mm=.1,
                differentiable=ev['differentiable'],reason=ev['reason'],ties=ev['ties'],zero_distance_rejected=not atedge['differentiable']))
        Q=inventory[f'h{level}_material_points_mm'];indices=np.linspace(0,len(Q)-1,40,dtype=int)
        for i in indices:
            q=Q[i]+rng.normal(size=3)*.013;ev=u.query(q)
            exhaustive=independent_distance(q,u.triangles).min();maxglobal=max(maxglobal,abs(ev['distance_mm']-exhaustive))
            if ev['differentiable']:
                direction=rng.normal(size=3)*.005;eps=1e-4
                fd=(u.query(q+eps*direction)['distance_mm']-u.query(q-eps*direction)['distance_mm'])/(2*eps)
                maxwork=max(maxwork,abs(fd-ev['point_gradient']@direction))
            # Entire assembly rigid translation, including owner geometry.
            shift=np.array([1.,-2.,3.]);moved=Union(p+shift,f).query(q+shift)
            maxobjective=max(maxobjective,abs(ev['distance_mm']-moved['distance_mm']))
        # All full-boundary samples retained under finite translations, a subset is exhaustively checked.
        transitions=[]
        for shift in [np.array([0,.05,0]),np.array([.05,0,.05]),np.array([0,0,4.])]:
            # Inventory is a fixed material grid. Every sample is checked; no pressure is transferred.
            counts={};rejected=0;crossing_uncertified=0
            for i,q in enumerate(Q):
                ev=u.query(q+shift);k=ev.get('feature','ZERO');counts[k]=counts.get(k,0)+1
                rejected+=not ev['differentiable']
                # 1-Lipschitz distance gives only a sufficient non-crossing certificate.
                crossing_uncertified+=inventory[f'h{level}_distance_mm'][i]<=np.linalg.norm(shift)+1e-10
            transitions.append(dict(shift_mm=shift.tolist(),retained_samples=sum(counts.values()),feature_counts=counts,
                nonsmooth_rejections=int(rejected),uncertified_segment_samples=int(crossing_uncertified),physical_update_accepted=False))
        reports.append(dict(mesh_level=level,concave_edges=conc,convex_edges=conv,concave_ties_rejected=ties,concave_two_branch_switches=branches,
            zero_distance_rejections=zero,max_independent_edge_distance_error_mm=maxedge,max_exhaustive_global_distance_error_mm=maxglobal,
            max_global_envelope_virtualwork_error=maxwork,max_translation_objectivity_error_mm=maxobjective,
            min_perturbed_branch_point_separation_mm=float(min_branch_separation),exhaustive_probes=len(indices),transitions=transitions))
    checks=dict(independent_finite_distance=all(r['max_independent_edge_distance_error_mm']<1e-8 and r['max_exhaustive_global_distance_error_mm']<1e-8 for r in reports),
        concave_alternatives=all(r['concave_two_branch_switches']==r['concave_edges'] and r['concave_ties_rejected']==r['concave_edges'] for r in reports),
        grazing_rejected=all(r['zero_distance_rejections']==r['concave_edges']+r['convex_edges'] for r in reports),
        global_virtualwork=all(r['max_global_envelope_virtualwork_error']<1e-8 for r in reports),
        objectivity=all(r['max_translation_objectivity_error_mm']<1e-8 for r in reports),
        full_inventory_retained=all(t['retained_samples']==len(inventory[f'h{r["mesh_level"]}_distance_mm']) for r in reports for t in r['transitions']))
    dump(out/'edge_probes.json',probes)
    dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_UNION_INDEPENDENT_AUDIT_PASS' if all(checks.values()) else 'ACTUAL_P1_FINITE_UNION_INDEPENDENT_AUDIT_FAIL',candidate=s['candidate'],source=ref(source),verifier=ref(out/'verifier.py'),operator=ref(ROOT/'scripts/finite_face_union27.py'),
        probes=ref(out/'edge_probes.json'),checks=checks,results=reports,elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Material-point finite-union envelope and rejected ambiguity, not signed penetration/complete swept surface CCD or equilibrium.',
        'Positive endpoints cannot accept an uncertified path. No attached load update or fictitious force at tie/zero distance.','Mesh approximation of CAD fillet remains distinct.']))
    print(json.dumps(dict(checks=checks,results=reports)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
