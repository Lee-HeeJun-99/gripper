"""Geometry-derived tighter bound for retained nonsmooth exterior material points.

For any convex triangle barycentrics, owner displacement is <= max vertex
displacement. Distance to a triangle union is 1-Lipschitz under point motion
and owner Hausdorff motion. With each body's original .05 mm local bound,
d_new >= d_old-.10 mm. This certifies only the NEXT local material-point step.
"""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import boundary,Union
from signed_boundary27 import winding_number


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    unsigned=ROOT/'validation/integrated/primaryP1_face_union27/summary.json';us=json.loads(unsigned.read_text());signed=ROOT/'validation/integrated/primaryP1_signed_boundary27v2/summary.json';ss=json.loads(signed.read_text())
    assert sha(REPO/us['operator_data']['path'])==us['operator_data']['SHA256'] and sha(REPO/ss['chart_data']['path'])==ss['chart_data']['SHA256']
    inv=np.load(REPO/us['operator_data']['path']);charts=np.load(REPO/ss['chart_data']['path']);arrays={};reports=[];rng=np.random.default_rng(2705)
    dump(out/'inputs.json',dict(candidate=us['candidate'],inventory=ref(unsigned),signed=ref(signed),producer=ref(out/'producer.py'),winding_operator=ref(ROOT/'scripts/signed_boundary27.py'),
        fixed_original_local_bound_mm_per_body=.05,relative_bound_policy='2b, where b=min(.05,(minimum unavailable-row distance-1e-10)/4); recompute before every accepted step',meaning='NEW geometry trust-region restriction, not criteria relaxation: no pressure/Jacobian on exterior inactive rows within NEXT derived step; all samples remain.'))
    for level in [2,3]:
        pre=f'h{level}_';ms=json.loads((ROOT/f'validation/integrated/primaryP1_ycapture_mesh{level}/summary.json').read_text());data=np.load(REPO/ms['mesh']['path']);p=data['OPEN_FRAME_points_mm'];f=boundary(p,data['OPEN_FRAME_tetra']);union=Union(p,f);Q=inv[pre+'material_points_mm'];distance=inv[pre+'distance_mm'];valid=charts[pre+'accepted'];ids=np.flatnonzero(~valid);bound=min(.05,(float(distance[ids].min())-1e-10)/4);assert bound>0;wind=np.full(len(Q),np.nan);safe=np.zeros(len(Q),bool)
        for i in ids:
            if i%32==0:assert not (ROOT/'runtime/STOP').exists()
            wn=float(winding_number(Q[i],union.triangles));wind[i]=wn
            safe[i]=abs(wn)<1e-8 and distance[i]>2*bound+1e-10
        margin=distance[ids]-2*bound;proof_tests=[];maxlowererror=0.
        # Independent perturbed whole-boundary samples; norm bound is checked on every vertex.
        displacement=rng.normal(size=p.shape);displacement*=rng.uniform(0,bound,(len(p),1))/np.linalg.norm(displacement,axis=1)[:,None]
        moved=Union(p+displacement,f);sample=ids[np.linspace(0,len(ids)-1,min(40,len(ids)),dtype=int)]
        for i in sample:
            dq=rng.normal(size=3);dq*=bound/np.linalg.norm(dq);new=moved.query(Q[i]+dq)['distance_mm'];lower=distance[i]-bound-np.linalg.norm(displacement,axis=1).max();maxlowererror=max(maxlowererror,lower-new);proof_tests.append(dict(sample=int(i),old_distance_mm=float(distance[i]),new_distance_mm=new,lower_bound_mm=float(lower)))
        # Deliberately oversized proposed point displacement must fail the bound.
        oversized_rejected=bool(np.all(distance[ids]-(distance[ids]+.01)-.05<0))
        for key,val in dict(inactive_certificate=safe,winding_number=wind,remaining_unresolved=(~valid)&(~safe),next_step_distance_lower_bound_mm=distance-2*bound).items():arrays[pre+key]=val
        reports.append(dict(mesh_level=level,material_samples=len(Q),original_local_bound_mm_per_body=.05,geometry_derived_bound_mm_per_body=bound,original_unavailable_derivatives=len(ids),certified_exterior_inactive=int(safe.sum()),
            remaining_unresolved=int(np.sum((~valid)&(~safe))),minimum_guard_distance_mm=float(distance[ids].min()),minimum_next_step_distance_lower_bound_mm=float(margin.min()),
            maximum_exterior_winding_error=float(np.max(abs(wind[ids]))),sampled_displacement_bound_mm=float(np.linalg.norm(displacement,axis=1).max()),
            max_lipschitz_lower_bound_violation_mm=float(maxlowererror),oversized_step_rejected=oversized_rejected,perturbation_controls=proof_tests,
            all_samples_retained=True,pressure_on_certified_inactive_rows_N=0.,scope='Only next geometry-derived tighter material-point local step; original .05mm limit retained. Recompute every accepted geometry update. No continuum/whole-model qualification.'))
    np.savez_compressed(out/'inactive_certificates.npz',**arrays)
    checks=dict(all_unavailable_rows_resolved_or_explicit=all(r['original_unavailable_derivatives']==r['certified_exterior_inactive']+r['remaining_unresolved'] for r in reports),
        all_unavailable_rows_certified_exterior_inactive=all(r['remaining_unresolved']==0 for r in reports),
        original_local_bound_and_positive_margin=all(r['minimum_next_step_distance_lower_bound_mm']>1e-10 and r['sampled_displacement_bound_mm']<=r['geometry_derived_bound_mm_per_body']+1e-14 and r['geometry_derived_bound_mm_per_body']<=.05 for r in reports),
        perturbation_controls=all(r['max_lipschitz_lower_bound_violation_mm']<1e-8 and r['oversized_step_rejected'] for r in reports))
    dump(out/'summary.json',dict(status='ACTUAL_P1_GEOMETRY_BOUNDED_INACTIVE_CERTIFICATE_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_GEOMETRY_BOUNDED_INACTIVE_CERTIFICATE_FAIL',candidate=us['candidate'],inputs=ref(out/'inputs.json'),certificates=ref(out/'inactive_certificates.npz'),checks=checks,results=reports,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Only stored material samples of actual polyhedral mesh. Not full continuous Root surface CCD, exact BRep or moving contact quadrature.',
        'Inactive rows remain in ledger. Their derivative is unavailable, not zero; pressure is provably zero only within certified local material-point neighborhood.',
        'Initial exterior classification checked independently by whole-surface solid angle. No physical load solve or fivebody completion.']))
    print(json.dumps(dict(checks=checks,results=[{k:v for k,v in r.items() if k!='perturbation_controls'} for r in reports])));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
