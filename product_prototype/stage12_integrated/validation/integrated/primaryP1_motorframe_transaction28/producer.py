"""Per-proposed-step unavailable-row guard on actual P1 finite support pairs.

This is a geometry transaction prerequisite, never a contact force/equilibrium
or full surface certificate. Keep original NaN gaps and every material row.
"""
import sys,json,time,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import boundary,Union
from signed_boundary27 import winding_number


def guarded_inactive(distance, exterior, source_step, owner_step, frozen_hash, current_hash):
    """Distances in mm; actual maximum vertex motion bounds whole triangles."""
    if frozen_hash!=current_hash: return np.zeros(len(distance),bool),'STALE_GEOMETRY'
    if not np.isfinite([source_step,owner_step]).all() or min(source_step,owner_step)<0:
        return np.zeros(len(distance),bool),'INVALID_STEP'
    return exterior & (distance-source_step-owner_step>1e-10),'BOUNDED_MATERIAL_POINTS_ONLY'


def main():
    start=time.monotonic();assert not(ROOT/'runtime/STOP').exists()
    tag,pair=sys.argv[1:];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/f'validation/integrated/primaryP1_{pair}_boundary27/summary.json';s=json.loads(src.read_text());ledger=REPO/s['material_ledger']['path'];assert sha(ledger)==s['material_ledger']['SHA256'];a=np.load(ledger)
    modelpath=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(modelpath.read_text())
    dump(out/'inputs.json',dict(candidate=s['candidate'],source_summary=ref(src),source_ledger=ref(ledger),fivebody=ref(modelpath),producer=ref(out/'producer.py'),
        operators=[ref(ROOT/'scripts/finite_face_union27.py'),ref(ROOT/'scripts/signed_boundary27.py')],original_local_limit_mm=.05,gap_limit_mm=1e-10,
        policy='Check exterior by whole closed owner solid angle, retain all rows. b=min(.05,(minimum unavailable distance-1e-10)/4). Evaluate actual nodal motion, including rigid Motor rotation. Recompute after each geometry change.'))
    arrays={};reports=[];rng=np.random.default_rng(2801)
    for r,mr in zip(s['results'],model['results']):
        h=r['mesh_level'];pre=f'h{h}_';mfile=REPO/mr['reference_model']['path'];assert sha(mfile)==mr['reference_model']['SHA256'];m=np.load(mfile);owner=r['owner'];p=m[owner+'_points_mm'];f=boundary(p,m[owner+'_tetra']);u=Union(p,f)
        q=a[pre+'source_material_points_mm'];d=a[pre+'unsigned_distance_mm'];valid=a[pre+'accepted'];ids=np.flatnonzero(~valid);wind=np.full(len(q),np.nan)
        for k,i in enumerate(ids):
            if k%32==0:assert not(ROOT/'runtime/STOP').exists()
            wind[i]=winding_number(q[i],u.triangles)
        exterior=np.zeros(len(q),bool);exterior[ids]=abs(wind[ids])<1e-8
        b=min(.05,(float(d[ids].min())-1e-10)/4) if len(ids) else .05
        frozen=sha(mfile);safe,why=guarded_inactive(d,exterior,b,b,frozen,sha(mfile))
        original,_=guarded_inactive(d,exterior,.05,.05,frozen,frozen)
        stale,_=guarded_inactive(d,exterior,0,0,frozen,'deliberately stale')
        oversize,_=guarded_inactive(d,exterior,float(d.max()+1),0,frozen,frozen)
        invalid,_=guarded_inactive(d,exterior,-1,0,frozen,frozen)
        # Numerical falsification controls use ALL owner vertices and finite triangles.
        delta=rng.normal(size=p.shape);delta*=rng.uniform(0,b,(len(p),1))/np.linalg.norm(delta,axis=1)[:,None];maxmove=float(np.linalg.norm(delta,axis=1).max());moved=Union(p+delta,f);tests=[]
        for i in ids[np.linspace(0,len(ids)-1,min(24,len(ids)),dtype=int)]:
            dq=rng.normal(size=3);dq*=b/np.linalg.norm(dq);dist=moved.query(q[i]+dq)['distance_mm'];lower=float(d[i]-b-maxmove)
            tests.append(dict(row=int(i),old_distance_mm=float(d[i]),new_distance_mm=dist,lower_mm=lower,violation_mm=max(0,lower-dist)))
        for name,value in dict(retained_accepted=valid,unavailable_exterior=exterior,winding=wind,inactive=safe,remaining_unresolved=(~valid)&(~safe),next_lower_distance_mm=d-2*b).items():arrays[pre+name]=value
        reports.append(dict(mesh_level=h,source=r['source'],owner=owner,rows=len(q),original_unavailable_rows=len(ids),exterior_unavailable_rows=int(exterior.sum()),inside_or_unresolved_rows=int(len(ids)-exterior.sum()),
            tighter_bound_mm_per_body=b,minimum_unavailable_distance_mm=float(d[ids].min()),minimum_next_step_lower_mm=float((d[ids]-2*b).min()),original_05mm_bound_rejected_rows=int(np.sum((~valid)&(~original))),
            certified_inactive_rows=int(safe.sum()),remaining_unresolved_rows=int(np.sum((~valid)&(~safe))),retained_NaN_gaps=int(np.isnan(a[pre+'gap_mm']).sum()),
            max_exterior_winding_error=float(np.max(abs(wind[ids][exterior[ids]]))) if exterior.any() else None,
            stale_geometry_rejected=not stale.any(),oversized_step_rejected=not oversize.any(),invalid_step_rejected=not invalid.any(),
            max_owner_vertex_motion_mm=maxmove,perturbation_controls=tests,maximum_lower_bound_violation_mm=max(t['violation_mm'] for t in tests),all_material_rows_retained=True,
            scope='Unavailable source samples only. Not accepted-chart continuation, reverse surface coverage, fullsurface CCD, contact pressure or equilibrium.'))
    np.savez_compressed(out/'transaction_guard.npz',**arrays)
    checks=dict(all_rows_retained=all(r['rows']==r['retained_NaN_gaps']+s['results'][i]['accepted_oriented_charts'] for i,r in enumerate(reports)),
        all_unavailable_exterior=all(r['inside_or_unresolved_rows']==0 for r in reports),all_unavailable_locally_inactive=all(r['remaining_unresolved_rows']==0 for r in reports),
        strict_positive_bound=all(0<r['tighter_bound_mm_per_body']<=.05 and r['minimum_next_step_lower_mm']>1e-10 for r in reports),
        rejection_controls=all(r['stale_geometry_rejected'] and r['oversized_step_rejected'] and r['invalid_step_rejected'] for r in reports),
        finite_perturbation_controls=all(r['maximum_lower_bound_violation_mm']<1e-8 and r['max_owner_vertex_motion_mm']<=r['tighter_bound_mm_per_body']+1e-14 for r in reports))
    dump(out/'summary.json',dict(status='ACTUAL_P1_PAIR_MATERIAL_TRANSACTION_PREREQUISITE_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_PAIR_MATERIAL_TRANSACTION_PREREQUISITE_FAIL',candidate=s['candidate'],inputs=ref(out/'inputs.json'),guard=ref(out/'transaction_guard.npz'),checks=checks,results=reports,elapsed_s=time.monotonic()-start,
        newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,limitations=['Guard only for unchanged reference and bounded proposed actual vertex displacements, including rigid Motor induced point motion.',
        'All accepted chart transitions must still be re-evaluated; no frozen Jacobian is certified by this guard. All unavailable gaps stay NaN.',
        'Material quadrature samples are not continuous surfaces. Fresh coupled Finger/string/freeY, hardware masses and physical Baseanchor still absent.']))
    print(json.dumps(dict(checks=checks,results=[{k:v for k,v in r.items() if k!='perturbation_controls'} for r in reports])));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
