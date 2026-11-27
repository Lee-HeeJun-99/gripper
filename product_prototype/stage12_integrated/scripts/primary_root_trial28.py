"""Actual P1 full Root material-row requery for bounded lateral trial motion.

Recompute every accepted finite chart and material pullback; unavailable rows
need independently proven exterior old-distance Lipschitz margin. This is a
kinematic proposed step, no force solve/pressure or accepted physical state.
"""
import sys,json,time,shutil
import numpy as np
from scipy.sparse import coo_matrix,save_npz
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import boundary
from signed_boundary27 import SignedBoundary


def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 up=ROOT/'validation/integrated/primaryP1_face_union27/summary.json';us=json.loads(up.read_text());a=np.load(REPO/us['operator_data']['path']);sp=ROOT/'validation/integrated/primaryP1_signed_boundary27v2/summary.json';ss=json.loads(sp.read_text());c=np.load(REPO/ss['chart_data']['path']);auditpath=ROOT/'validation/integrated/primaryP1_transaction_audit28/summary.json';audit=json.loads(auditpath.read_text());modelpath=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(modelpath.read_text());certpath=ROOT/'validation/integrated/primaryP1_inactive_certificate27bounded/summary.json';cert=json.loads(certpath.read_text());certs=np.load(REPO/cert['certificates']['path'])
 dump(out/'inputs.json',dict(candidate=us['candidate'],original_unsigned=ref(up),original_signed=ref(sp),independent_audit=ref(auditpath),root_exterior_guard=ref(certpath),fivebody=ref(modelpath),producer=ref(out/'producer.py'),operators=[ref(ROOT/'scripts/signed_boundary27.py'),ref(ROOT/'scripts/finite_face_union27.py')],actual_trial_rootY_mm=[.00001,-.00001],owner_frame_vertex_motion_mm=0,meaning='Proposed local kinematic steps only, recompute all finite oriented owners. No physical sourcefield transferred or equilibrium accepted.'))
 results=[];saved={}
 for mr,ar in zip(model['results'],audit['results']):
  h=mr['mesh_level'];pre=f'h{h}_';m=np.load(REPO/mr['reference_model']['path']);p=m['OPEN_FRAME_points_mm'];f=boundary(p,m['OPEN_FRAME_tetra']);owner=SignedBoundary(p,f);rootp=m['F0_ROOT_BACK_points_mm'];rootf=boundary(rootp,m['F0_ROOT_BACK_tetra']);rw=np.array([[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]])
  # Independently reconstruct actual source points, do not use an index transfer.
  q0=np.einsum('ab,tbc->tac',rw,rootp[rootf]).reshape(-1,3);assert np.max(abs(q0-a[pre+'material_points_mm']))<1e-10
  initialvalid=c[pre+'accepted'];initialgap=c[pre+'signed_gap_mm'] if pre+'signed_gap_mm' in c.files else c[pre+'gap_mm'];d0=a[pre+'distance_mm'];exterior=certs[pre+'inactive_certificate']|(initialvalid&(initialgap>1e-10));b=ar['common_actual_vertex_bound_mm_per_body']
  for sign,dy in [('plus',.00001),('minus',-.00001)]:
   assert abs(dy)<b;q=q0+[0,dy,0];valid=np.zeros(len(q),bool);safe=np.zeros(len(q),bool);gap=np.full(len(q),np.nan);dist=np.zeros(len(q));rows=[];cols=[];vals=[];reasons={};vw=0.;moment=0.;probes=0;maxdistchange=0
   for i,x in enumerate(q):
    if i%256==0:assert not(ROOT/'runtime/STOP').exists()
    ev=owner.chart(x);reasons[ev['reason']]=reasons.get(ev['reason'],0)+1
    if not ev['accepted']:
     dist[i]=owner.query(x)['distance_mm'];safe[i]=exterior[i] and d0[i]-abs(dy)>1e-10;continue
    valid[i]=True;gap[i]=ev['gap_mm'];dist[i]=abs(gap[i]);n=ev['point_gradient'];ww=ev['weights'];fi=ev['face'];oi=int(m['OPEN_FRAME_offset'])+3*f[fi,:,None]+np.arange(3);ri=int(m['F0_ROOT_BACK_offset'])+3*rootf[i//3,:,None]+np.arange(3)
    for ids,v in [(oi,(-ww[:,None]*n)),(ri,rw[i%3,:,None]*n)]:rows.extend([i]*9);cols.extend(ids.ravel().tolist());vals.extend(v.ravel().tolist())
    moment=max(moment,float(np.linalg.norm(np.cross(x,n)+np.cross(p[f[fi]],-ww[:,None]*n).sum(0))))
    if i%max(1,len(q)//32)==0 and abs(gap[i])>1e-5:
     direction=np.array([.001,-.002,.003]);eps=1e-4;ep=owner.chart(x+eps*direction);em=owner.chart(x-eps*direction)
     if ep['accepted'] and em['accepted']:vw=max(vw,abs((ep['gap_mm']-em['gap_mm'])/(2*eps)-n@direction));probes+=1
   maxdistchange=float(np.max(abs(dist-d0)));J=coo_matrix((vals,(rows,cols)),shape=(len(q),len(m['reference_coordinates_mm']))).tocsr();J.eliminate_zeros();save_npz(out/f'h{h}_{sign}_trial_gap_J.npz',J)
   for name,value in dict(recomputed_accepted=valid,certified_inactive=safe,trial_gap_mm=gap,trial_distance_mm=dist,unresolved=(~valid)&(~safe)).items():saved[f'h{h}_{sign}_{name}']=value
   results.append(dict(mesh_level=h,RootY_trial_mm=dy,Frame_trial_mm=0.,source_rows=len(q),recomputed_charts=int(valid.sum()),new_unavailable_rows=int((~valid).sum()),guarded_unavailable_rows=int(safe.sum()),remaining_unresolved_rows=int(np.sum((~valid)&(~safe))),
    negative_gap_rows=int(np.sum(gap<-1e-10)),minimum_recomputed_gap_mm=float(np.nanmin(gap)),maximum_distance_change_mm=maxdistchange,maximum_unit_action_reaction_moment_error_Nmm=moment,maximum_virtualwork_error=vw,virtualwork_probes=probes,chart_reasons=reasons,
    common_maximum_vertex_bound_mm=b,all_rows_retained=True,actual_force_solve=False,physical_step_accepted=False,full_model_trial_ready=False,trial_J=ref(out/f'h{h}_{sign}_trial_gap_J.npz')))
 np.savez_compressed(out/'trial_material_ledgers.npz',**saved)
 checks=dict(all_material_rows_retained=all(r['source_rows']==r['recomputed_charts']+r['guarded_unavailable_rows']+r['remaining_unresolved_rows'] for r in results),bounded_actual_motion=all(abs(r['RootY_trial_mm'])<r['common_maximum_vertex_bound_mm'] and r['maximum_distance_change_mm']<=abs(r['RootY_trial_mm'])+1e-8 for r in results),
  all_rejected_charts_safely_inactive=all(r['remaining_unresolved_rows']==0 for r in results),nominal_trial_nonpenetration=all(r['negative_gap_rows']==0 for r in results),finite_cotangent_work_moment=all(r['maximum_unit_action_reaction_moment_error_Nmm']<1e-8 and r['maximum_virtualwork_error']<1e-8 for r in results))
 dump(out/'summary.json',dict(status='ACTUAL_P1_ROOT_LATERAL_FINITE_TRIAL_REQUERY_VERIFIED_NOT_EQUILIBRIUM' if all(checks.values()) else 'ACTUAL_P1_ROOT_LATERAL_FINITE_TRIAL_REQUERY_REJECTED',candidate=us['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=results,trial_ledgers=ref(out/'trial_material_ledgers.npz'),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,limitations=['RootFrame sample rows only. Other adjacent pair coordinates unchanged; no new full support nonlinear transaction/line search or force equilibrium accepted.',
 'Continuous Root/Frame surfaces and both-side contact integration remain unqualified. Recomputed finite trial J is a geometry operator, never a pressure or reaction.',
 'Old sourcefield and pressure not transferred; free RootY is neither fixed nor artificially sprung. Trial .00001mm is not claimed operating deflection or convergence result.']))
 print(json.dumps(dict(checks=checks,results=results)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
