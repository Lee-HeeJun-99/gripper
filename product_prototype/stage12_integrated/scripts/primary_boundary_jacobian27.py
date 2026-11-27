"""Full-row material gap Jacobian for actual Root/Frame, with unresolved NaNs.

Every physical node remains an independent variable. Unresolved rows remain in
the matrix shape and in the gap ledger; a mandatory readiness gate blocks solve.
"""
import sys,json,shutil,time
import numpy as np
from scipy.sparse import coo_matrix,save_npz
from baseline_registry import ROOT,REPO,ref,dump,sha


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    unsigned=ROOT/'validation/integrated/primaryP1_face_union27/summary.json';us=json.loads(unsigned.read_text())
    signed=ROOT/'validation/integrated/primaryP1_signed_boundary27v2/summary.json';ss=json.loads(signed.read_text())
    assert sha(REPO/us['operator_data']['path'])==us['operator_data']['SHA256']
    assert sha(REPO/ss['chart_data']['path'])==ss['chart_data']['SHA256']
    inv=np.load(REPO/us['operator_data']['path']);charts=np.load(REPO/ss['chart_data']['path']);rng=np.random.default_rng(2704);results=[]
    dump(out/'inputs.json',dict(candidate=us['candidate'],inventory=ref(unsigned),signed_charts=ref(signed),producer=ref(out/'producer.py'),
        requirement='All nodes independent, all material rows retained, unresolved gap NaNs block solve; no sourcefield transfer or physical regularization.'))
    for level in [2,3]:
        pre=f'h{level}_';ms=json.loads((ROOT/f'validation/integrated/primaryP1_ycapture_mesh{level}/summary.json').read_text());data=np.load(REPO/ms['mesh']['path']);rp,fp=(data[n+'_points_mm'] for n in ['F0_ROOT_BACK','OPEN_FRAME']);rf,ff=inv[pre+'root_faces'],inv[pre+'frame_faces'];q=inv[pre+'material_points_mm'];area=inv[pre+'material_weights_mm2'];gap=charts[pre+'gap_mm'];valid=charts[pre+'accepted'];owner=charts[pre+'owner_faces'];g=charts[pre+'point_gradient'];ow=charts[pre+'owner_weights'];ids=np.flatnonzero(valid);rw=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])
        rootnodes=rf[ids//3];framenodes=ff[owner[ids]]+len(rp)
        nodes=np.concatenate([rootnodes,framenodes],axis=1)
        rowgrad=np.concatenate([rw[ids%3,:,None]*g[ids,None,:],-ow[ids,:,None]*g[ids,None,:]],axis=1)
        rows=np.broadcast_to(ids[:,None,None],rowgrad.shape).reshape(-1)
        cols=(3*nodes[:,:,None]+np.arange(3)).reshape(-1)
        J=coo_matrix((rowgrad.reshape(-1),(rows,cols)),shape=(len(q),3*(len(rp)+len(fp)))).tocsr();J.eliminate_zeros()
        save_npz(out/f'h{level}_gap_J.npz',J)
        X=np.vstack([rp,fp]);translation=[];rotation=[]
        for axis in np.eye(3):
            translation.append(float(np.max(abs(J@np.tile(axis,len(X))))))
            rotation.append(float(np.max(abs(J@np.cross(np.broadcast_to(axis,X.shape),X).reshape(-1)))))
        # Independent row-by-row evaluation and dual virtual-work check; not a physical pressure solution.
        v=rng.normal(size=X.shape)*.005;lamb=rng.normal(size=len(q));lamb[~valid]=0
        direct=np.zeros(len(q));direct[ids]=np.einsum('nki,nki->n',rowgrad,v[nodes]);mapped=J@v.reshape(-1)
        vw=abs(lamb@mapped-(J.T@lamb)@v.reshape(-1));maxrow=float(np.max(abs(direct-mapped)))
        force=(J.T@lamb).reshape(-1,3);net=force.sum(axis=0);moment=np.cross(X,force).sum(axis=0)
        rootY=np.zeros_like(X);rootY[:len(rp),1]=1;dy=J@rootY.reshape(-1);active=valid&(abs(gap)<=1e-10)
        missing=int((~valid).sum());penetration=int(np.sum(valid&(gap<-1e-10)))
        results.append(dict(mesh_level=level,rows=J.shape[0],columns=J.shape[1],nonzero_entries=J.nnz,
            root_nodes=len(rp),frame_nodes=len(fp),independent_physical_DOFs=3*len(X),unresolved_rows=missing,
            all_rows_retained=J.shape[0]==3*len(rf),unresolved_gap_is_NaN=bool(np.all(np.isnan(gap[~valid]))),
            accepted_chart_rows=len(ids),negative_gap_rows=penetration,maximum_penetration_mm=float(max(0,-np.nanmin(gap))),
            active_nominal_rows=int(active.sum()),max_active_RootY_gap_derivative=float(np.max(abs(dy[active]))) if active.any() else None,
            rigid_translation_errors=translation,rigid_rotation_errors_mm=rotation,max_independent_row_error=maxrow,dual_virtualwork_error=vw,
            random_dual_net_force_error=float(np.linalg.norm(net)),random_dual_net_moment_error=float(np.linalg.norm(moment)),
            mandatory_solve_readiness=missing==0 and penetration==0,matrix=ref(out/f'h{level}_gap_J.npz')))
    checks=dict(full_rows_and_DOFs=all(r['all_rows_retained'] and r['unresolved_gap_is_NaN'] for r in results),
        rigid_invariance=all(max(r['rigid_translation_errors']+r['rigid_rotation_errors_mm'])<1e-8 for r in results),
        independent_row_and_duality=all(r['max_independent_row_error']<1e-10 and r['dual_virtualwork_error']<1e-8 for r in results),
        force_moment=all(r['random_dual_net_force_error']<1e-8 and r['random_dual_net_moment_error']<1e-8 for r in results))
    dump(out/'summary.json',dict(status='ACTUAL_P1_FULL_ROW_GAP_JACOBIAN_VERIFIED_SOLVE_BLOCKED' if all(checks.values()) else 'ACTUAL_P1_FULL_ROW_GAP_JACOBIAN_FAIL',candidate=us['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=results,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Actual Root/Frame two-body contact blocks only. Not complete fivebody stiffness, motorfront, 14 axial branches, loads or new equilibrium.',
        'Random signed dual tests are algebraic virtual-work controls, NOT physical nonnegative pressure or operating forces.',
        'Unresolved chart rows retain NaN gaps. Zero sparse storage in those rows is unavailable derivative, never a valid zero force/energy or permission to solve.',
        'Mandatory readiness must pass before any physical solve, alongside original finite-domain/cone/gap/fullforce/gauge/complementarity/localbound gates.']))
    print(json.dumps(dict(checks=checks,results=results)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
