"""Assemble actual same-revision finite blocks without solving incomplete physics."""
import sys,json,shutil,time
import numpy as np
from scipy.sparse import load_npz,save_npz,coo_matrix,vstack
from baseline_registry import ROOT,REPO,ref,dump,sha


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    b=ROOT/'validation/integrated';names=['primaryP1_fivebody_rebuild27','primaryP1_face_union27','primaryP1_signed_boundary27v2','primaryP1_boundary_jacobian27','primaryP1_inactive_certificate27bounded','primaryP1_axial_rebuild27env','primaryP1_axial_operator27','primaryP1_frameground_boundary27','primaryP1_groundbase_boundary27','primaryP1_motorframe_boundary27','primaryP1_motorcap_boundary27','primaryP1_capframe_boundary27'];s={n:json.loads((b/n/'summary.json').read_text()) for n in names};candidate=s[names[0]]['candidate'];assert all(x['candidate']==candidate for x in s.values())
    dump(out/'inputs.json',dict(candidate=candidate,producer=ref(out/'producer.py'),blocks={n:ref(b/n/'summary.json') for n in names},status='FROZEN_PRE_SOLVE_BLOCKS_NO_EQUILIBRIUM',no_old_sourcefield_transfer=True))
    rootdata=np.load(REPO/s['primaryP1_signed_boundary27v2']['chart_data']['path']);rootinv=np.load(REPO/s['primaryP1_face_union27']['operator_data']['path']);inactive=np.load(REPO/s['primaryP1_inactive_certificate27bounded']['certificates']['path']);results=[]
    for i,mr in enumerate(s[names[0]]['results']):
        level=mr['mesh_level'];a=np.load(REPO/mr['reference_model']['path']);N=len(a['reference_coordinates_mm']);rj=s['primaryP1_boundary_jacobian27']['results'][i];Jr=load_npz(REPO/rj['matrix']['path']).tocoo();nr=len(a['F0_ROOT_BACK_points_mm']);nf=len(a['OPEN_FRAME_points_mm']);assert Jr.shape[1]==3*(nr+nf)
        permutation=np.r_[int(a['F0_ROOT_BACK_offset'])+np.arange(3*nr),int(a['OPEN_FRAME_offset'])+np.arange(3*nf)];J=coo_matrix((Jr.data,(Jr.row,permutation[Jr.col])),shape=(Jr.shape[0],N)).tocsr();blocks=[J];gaps=[rootdata[f'h{level}_gap_mm']];available=[rootdata[f'h{level}_accepted']];weights=[rootinv[f'h{level}_material_weights_mm2']];rootinactive=inactive[f'h{level}_inactive_certificate'];certificates=[rootinactive];labels=['Root_Frame']*J.shape[0];blockreports=[]
        for name in names[7:]:
            bs=s[name];r=bs['results'][i];Bj=load_npz(REPO/r['full_row_J']['path']);assert Bj.shape[1]==N;ledger=np.load(REPO/bs['material_ledger']['path']);assert Bj.shape[0]==len(ledger[f'h{level}_gap_mm']);blocks.append(Bj);gaps.append(ledger[f'h{level}_gap_mm']);available.append(ledger[f'h{level}_accepted']);weights.append(ledger[f'h{level}_source_material_weights_mm2']);certificates.append(np.zeros(Bj.shape[0],bool));labels.extend([r['source']+'_'+r['owner']]*Bj.shape[0]);blockreports.append(dict(pair=labels[-1],rows=Bj.shape[0],unavailable=int((~ledger[f'h{level}_accepted']).sum()),negative_gap_samples=r['negative_gap_samples']))
        JJ=vstack(blocks,format='csr');gap=np.concatenate(gaps);valid=np.concatenate(available);weight=np.concatenate(weights);certified=np.concatenate(certificates);assert JJ.shape[0]==len(gap)==len(labels);D=load_npz(REPO/s['primaryP1_axial_rebuild27env']['results'][i]['conditional_axial_D']['path']);assert D.shape==(14,N)
        save_npz(out/f'h{level}_full_contact_J.npz',JJ);save_npz(out/f'h{level}_14axial_D.npz',D)
        np.savez_compressed(out/f'h{level}_full_row_ledger.npz',gap_mm=gap,chart_available=valid,material_area_weights_mm2=weight,certified_inactive_next_root_step=certified,pair_labels=np.array(labels),unresolved=(~valid)&(~certified))
        errors=[]
        for axis in np.eye(3):
            for rotate in [False,True]:
                v=np.zeros(N)
                for body in ['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE']:
                    X=a[body+'_points_mm'];o=int(a[body+'_offset']);v[o:o+3*len(X)]=(np.cross(np.broadcast_to(axis,X.shape),X) if rotate else np.broadcast_to(axis,X.shape)).reshape(-1)
                mo=int(a['motor_offset']);v[mo:mo+3]=np.cross(axis,[0,0,20]) if rotate else axis
                if rotate:v[mo+3:mo+6]=axis
                errors.append(float(max(np.max(abs(JJ@v)),np.max(abs(D@v)))))
        unknown=int(np.sum((~valid)&(~certified)));negative=int(np.sum(valid&(gap<-1e-10)));step=s['primaryP1_inactive_certificate27bounded']['results'][i]['geometry_derived_bound_mm_per_body']
        results.append(dict(mesh_level=level,physical_coordinates=N,contact_material_rows=JJ.shape[0],axial_branches=14,contact_pairs=6,
            unavailable_derivatives=int((~valid).sum()),certified_inactive_Root_Frame_rows=int(certified.sum()),remaining_unresolved_rows=unknown,negative_gap_samples=negative,
            all_rows_retained=True,unavailable_gap_NaNs_retained=bool(np.all(np.isnan(gap[~valid]))),common_rigid_mode_max_error=max(errors),upstream_freeY_column_unrestrained=bool(JJ[:,int(a['upstream_freeY_offset'])].nnz==0 and D[:,int(a['upstream_freeY_offset'])].nnz==0),
            original_local_limit_mm=.05,Root_Frame_next_step_geometry_bound_mm=step,other_pairs_next_step_geometry_bound_mm=None,
            blocks=blockreports,sourcefield_transferred=False,physical_Base_fixation_added=False,physical_Base_counterload_added=False,physical_model_solve_ready=False,
            contact_J=ref(out/f'h{level}_full_contact_J.npz'),axial_D=ref(out/f'h{level}_14axial_D.npz'),row_ledger=ref(out/f'h{level}_full_row_ledger.npz')))
    checks=dict(same_actual_candidate=True,all_material_rows_and_unknowns_preserved=all(r['all_rows_retained'] and r['unavailable_gap_NaNs_retained'] for r in results),
        all14_axial_blocks=all(r['axial_branches']==14 for r in results),no_artificial_restraint=all(r['upstream_freeY_column_unrestrained'] and not r['physical_Base_fixation_added'] and not r['physical_Base_counterload_added'] for r in results),
        full_common_rigid_invariance=all(r['common_rigid_mode_max_error']<1e-8 for r in results))
    dump(out/'summary.json',dict(status='ACTUAL_P1_SAME_REVISION_FINITE_BLOCKS_ASSEMBLED_SOLVE_BLOCKED' if all(checks.values()) else 'ACTUAL_P1_SAME_REVISION_FINITE_BLOCK_ASSEMBLY_FAIL',candidate=candidate,inputs=ref(out/'inputs.json'),checks=checks,results=results,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,stage3_authorized=False,
        mandatory_missing_before_solve=['Resolve signed/finite-domain transactions for every adjacent pair, including unavailable charts and any negative gaps; retain all material rows.',
            'Complete same-revision fresh coupled Finger/string/freeY equation and exact remaining hardware gravity without Base residual cancellation.',
            'Original fullforce1e-8N/gap1e-10mm/local.05mm/rad/conesign/gauge/complementarity/Armijo and finite-owner checks before attached load update.'],
        limitations=['Five elastic bodies, rigid Motor, independent upstream freeY scalar. Assembled finite blocks are NOT a complete qualified coupled physical model.',
            'Root/Frame inactive certificate only applies to its derived next local step. Other pair certificates absent, so no global search/update is authorized.',
            'No physical force solution/mesh1%/time.1%/globalenergy/materialminimum/thread/physicalanchor/full3Finger gate passed.']))
    print(json.dumps(dict(checks=checks,results=results)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
