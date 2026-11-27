"""Actual P1 oriented finite gap charts, independently checked by winding."""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import boundary
from signed_boundary27 import SignedBoundary,winding_number


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'validation/integrated/primaryP1_face_union27/summary.json';source=json.loads(src.read_text());inventory=np.load(REPO/source['operator_data']['path'])
    assert sha(REPO/source['operator_data']['path'])==source['operator_data']['SHA256']
    dump(out/'inputs.json',dict(source=ref(src),operator=ref(ROOT/'scripts/signed_boundary27.py'),unsigned_operator=ref(ROOT/'scripts/finite_face_union27.py'),producer=ref(out/'producer.py')))
    reports=[];arrays={};rng=np.random.default_rng(2703)
    for level in [2,3]:
        ms=json.loads((ROOT/f'validation/integrated/primaryP1_ycapture_mesh{level}/summary.json').read_text());data=np.load(REPO/ms['mesh']['path']);p=data['OPEN_FRAME_points_mm'];f=boundary(p,data['OPEN_FRAME_tetra']);u=SignedBoundary(p,f)
        # Independent topological manifold/orientation checks, mandatory for signs.
        edges={}
        for face in f:
            for a,b in zip(face,np.roll(face,-1)):edges.setdefault(tuple(sorted((int(a),int(b)))),[]).append(1 if a<b else -1)
        closed=all(len(v)==2 and sum(v)==0 for v in edges.values())
        Q=inventory[f'h{level}_material_points_mm'];gap=np.full(len(Q),np.nan);accepted=np.zeros(len(Q),bool);owner=np.full(len(Q),-1,int);grad=np.zeros((len(Q),3));weights=np.zeros((len(Q),3));counts={}
        for i,q in enumerate(Q):
            if i%256==0:assert not (ROOT/'runtime/STOP').exists()
            ev=u.chart(q);counts[ev['reason']]=counts.get(ev['reason'],0)+1
            if ev['accepted']:
                accepted[i]=True;gap[i]=ev['gap_mm'];owner[i]=ev['face'];grad[i]=ev['point_gradient'];weights[i]=ev['weights']
        offsign=0;offtested=0;maxwinding=0.;maxwork=0.;maxmoment=0.;negative=0;positive=0;zero_charts=0;maxzero=0.;zero_reject=0
        # Both sides of actual Frame faces, including internal cavity surfaces, all global triangles included.
        indices=np.linspace(0,len(f)-1,80,dtype=int)
        for fi in indices:
            t=u.triangles[fi];c=t.mean(axis=0);n=u.normals[fi]
            atzero=u.chart(c)
            if atzero['accepted']:
                zero_charts+=1;maxzero=max(maxzero,abs(atzero['gap_mm']))
                forces=np.vstack([atzero['point_gradient'], -atzero['weights'][:,None]*atzero['point_gradient']])
                maxmoment=max(maxmoment,np.linalg.norm(np.cross(np.vstack([c,t]),forces).sum(axis=0)))
                # Two-sided oriented normal perturbation: at zero the unsigned chart was deliberately unavailable.
                plus,minus=u.chart(c+1e-5*n),u.chart(c-1e-5*n)
                if plus['accepted'] and minus['accepted']:
                    maxwork=max(maxwork,abs((plus['gap_mm']-minus['gap_mm'])/(2e-5)-1.))
            else:zero_reject+=1
            for sign in [-1,1]:
                q=c+sign*.01*n;ev=u.chart(q)
                if not ev['accepted']:continue
                wn=winding_number(q,u.triangles);inside=abs(wn)>.5
                maxwinding=max(maxwinding,min(abs(wn),abs(abs(wn)-1)))
                offsign+=bool((ev['gap_mm']<0)!=inside);offtested+=1;negative+=inside;positive+=not inside
        # Real closed nominal shoulder: no reaction at original open .1mm gap.
        shoulder=[]
        records=json.loads((ROOT/'validation/integrated/primaryP1_clipped_shoulder26correct/quadrature.json').read_text())
        for rec in [x for x in records if x['mesh_level']==level]:
            for row in rec['rows'][::max(1,len(rec['rows'])//24)]:
                q=np.array(row['root_point_mm']);sign=rec['sign'];vals=[]
                for dy in [0,.05,.1,.101]:
                    ev=u.chart(q+np.array([0,sign*dy,0]));vals.append(dict(dy_mm=dy,accepted=ev['accepted'],gap_mm=ev.get('gap_mm'),reason=ev['reason']))
                shoulder.append(vals)
        arrays.update({f'h{level}_'+k:v for k,v in dict(gap_mm=gap,accepted=accepted,owner_faces=owner,point_gradient=grad,owner_weights=weights).items()})
        reports.append(dict(mesh_level=level,closed_oriented_two_manifold=closed,retained_samples=len(Q),accepted_signed_charts=int(accepted.sum()),
            rejected_samples=int((~accepted).sum()),chart_counts=counts,negative_initial_samples=int(np.sum(gap<-1e-10)),
            winding_probes=offtested,independent_winding_sign_disagreements=offsign,max_winding_integer_error=maxwinding,
            winding_inside_probes=negative,winding_outside_probes=positive,zero_face_charts_verified=zero_charts,zero_face_charts_rejected=zero_reject,
            max_zero_chart_gap_mm=maxzero,max_zero_chart_normal_derivative_error=maxwork,max_unit_force_moment_error=maxmoment,
            shoulder_open_close_penetration=shoulder))
    np.savez_compressed(out/'signed_charts.npz',**arrays)
    checks=dict(closed_oriented_manifold=all(r['closed_oriented_two_manifold'] for r in reports),
        independent_signed_inside_outside=all(r['independent_winding_sign_disagreements']==0 and r['winding_inside_probes']>0 and r['winding_outside_probes']>0 and r['max_winding_integer_error']<1e-8 for r in reports),
        zero_gap_chart=all(r['zero_face_charts_verified']>50 and r['max_zero_chart_gap_mm']<1e-10 and r['max_zero_chart_normal_derivative_error']<1e-8 for r in reports),
        force_moment=all(r['max_unit_force_moment_error']<1e-8 for r in reports),
        shoulder_gap_sequence=all(all(v['accepted'] and abs(v['gap_mm']-(.1-v['dy_mm']))<1e-8 for v in row) for r in reports for row in r['shoulder_open_close_penetration']))
    dump(out/'summary.json',dict(status='ACTUAL_P1_ORIENTED_GAP_CHARTS_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_ORIENTED_GAP_CHARTS_FAIL',candidate=source['candidate'],source=ref(src),inputs=ref(out/'inputs.json'),chart_data=ref(out/'signed_charts.npz'),checks=checks,results=reports,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Closed polyhedral mesh local charts. Winding probes are independent finite tests, not exact curved CAD/continuous collision certification.',
        'Unaccepted samples remain in inventory with NaN gap; no row deletion, zero-energy substitution or fictitious tie. Complete contact transactions must resolve them before equilibrium.',
        'No pressure assigned to open shoulders. No old sourcefield transfer, new physical load equilibrium or complete fivebody rebuild.']))
    print(json.dumps(dict(checks=checks,results=[{k:v for k,v in r.items() if k!='shoulder_open_close_penetration'} for r in reports])));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
