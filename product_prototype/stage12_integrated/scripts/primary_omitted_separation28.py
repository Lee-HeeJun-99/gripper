"""Conservative whole-solid AABB certificates for omitted P1 support pairs.

Any point in a linear tetra mesh lies inside its nodal AABB. Disjoint inflated
boxes prove whole solid separation, including surface interiors, without
relabeling material sampling as CCD. Overlap is inconclusive, never PASS.
"""
import sys,json,time,shutil,itertools
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha


def main():
    start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';s=json.loads(src.read_text());motorpath=ROOT/'validation/integrated/primaryP1_motorframe_boundary27/actual_motor_surface.npz';motor=np.load(motorpath)['points_mm']
    adjacent={frozenset(x) for x in [('F0_ROOT_BACK','OPEN_FRAME'),('OPEN_FRAME','GROUND_PLATE'),('GROUND_PLATE','TEST_BASE'),('Motor','OPEN_FRAME'),('Motor','MOTOR_CAP'),('MOTOR_CAP','OPEN_FRAME')]}
    dump(out/'inputs.json',dict(candidate=s['candidate'],fivebody=ref(src),motor_surface=ref(motorpath),producer=ref(out/'producer.py'),scope='Only six modeled support bodies, not all78parts. Polyhedral solid envelopes; no BRep approximation error bound claimed. Bound is maximum ACTUAL vertex displacement, including rigid rotation.'))
    rows=[]
    for mr in s['results']:
        file=REPO/mr['reference_model']['path'];assert sha(file)==mr['reference_model']['SHA256'];a=np.load(file);points={n:a[n+'_points_mm'] for n in ['F0_ROOT_BACK','OPEN_FRAME','MOTOR_CAP','GROUND_PLATE','TEST_BASE']};points['Motor']=motor
        for n,m in itertools.combinations(points,2):
            if frozenset((n,m)) in adjacent:continue
            p,q=points[n],points[m];lo1,hi1=p.min(0),p.max(0);lo2,hi2=q.min(0),q.max(0);axis=np.maximum(np.maximum(lo1-hi2,lo2-hi1),0);d=float(np.linalg.norm(axis));b=.05;lower=max(0,d-2*b)
            # Direct independent scalar interval test confirms each separating axis.
            scalar=np.array([max(0,float(lo1[i]-hi2[i]),float(lo2[i]-hi1[i])) for i in range(3)])
            assert np.max(abs(axis-scalar))<1e-12
            rows.append(dict(mesh_level=mr['mesh_level'],first=n,second=m,first_AABB_mm=[lo1.tolist(),hi1.tolist()],second_AABB_mm=[lo2.tolist(),hi2.tolist()],axis_separation_mm=axis.tolist(),whole_solid_distance_lower_mm=d,
                maximum_actual_vertex_step_mm_per_body=b,next_step_whole_solid_lower_mm=lower,whole_polyhedral_solid_certified_separated=bool(lower>1e-10),state='CERTIFIED_NEXT_BOUNDED_STEP' if lower>1e-10 else 'INCONCLUSIVE_BOX_OVERLAP',
                not_general_surface_CCD=True))
    checks=dict(all_nine_omitted_pairs_per_mesh=len(rows)==18,all_omitted_polyhedral_solids_separated=all(r['whole_polyhedral_solid_certified_separated'] for r in rows))
    dump(out/'summary.json',dict(status='ACTUAL_P1_OMITTED_SUPPORT_SOLID_SEPARATION_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_OMITTED_SUPPORT_SOLID_SEPARATION_INCOMPLETE',candidate=s['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=rows,elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Certificates cover nine omitted pairs among six support bodies only. All remaining72parts/bolts/wire/Finger still require their physical owners and load model.',
        'AABB encloses complete linear tetrahedral solid, not exact original curved BRep. Local nextstep bounds require continuous path to stay inside displacement envelope; endpoint alone insufficient.',
        'No adjacent-contact surface coverage, equilibrium, anchor or stress/energy qualification.']))
    print(json.dumps(dict(checks=checks,minimum_next_step_whole_solid_lower_mm=min(r['next_step_whole_solid_lower_mm'] for r in rows))));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
