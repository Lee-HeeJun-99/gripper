"""Independent seated-pose actual83 interference and original body wrench audit."""
import json,sys,shutil,math,itertools,time
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
from primary_keeper_coupled71 import wrench,pointdist
from primary_clocked62 import spin
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,bounds,overlap

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_boltseat74/summary.json';s=json.loads(sp.read_text());cp=REPO/s['candidate_reference']['path'];assert sha(cp)==s['candidate_reference']['SHA256'];cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());parts={n:read(REPO/r['path']) for n,r in cad['part_references'].items()};settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];x=np.array(s['pose_planar']);changed=['ROOT_SOCKET_KEEPER']+[q['bolt'] for q in settings];parts[changed[0]]=translate(spin(parts[changed[0]],60,0,math.degrees(x[2])),x[0],x[1],0)
 for i,q in enumerate(settings):
  off=3+3*i;parts[q['bolt']]=translate(spin(parts[q['bolt']],q['x'],q['y'],math.degrees(x[off+2])),x[off],x[off+1],0)
 bodies=[parts[n] for n in changed]+[parts['F0_ROOT_BACK']];columns=[];dist=[]
 for q in s['contacts']:
  i,j=q['body_i'],q['body_j'];p=np.array(q['point_mm']);n=np.array(q['normal_on_i']);col=np.zeros((4,6));col[i]=wrench(p,n);col[j]=-col[i];columns.append(col.ravel());dist.append(max(pointdist(bodies[i],p),pointdist(bodies[j],p)))
 A=np.column_stack(columns);P=np.zeros((24,6));P[-6:]=np.eye(6);AP=np.c_[A,P];v=np.r_[s['result']['normal_forces_N'],s['result']['host_external_wrench_N_Nmm']];ext=np.array(s['external_body_wrenches_N_Nmm']).ravel();res=AP@v+ext;common_work=float(abs(A.T@np.tile(np.array([.2,-.1,.3,-.4,.5,-.6]),4)).max());head=[i for i,q in enumerate(s['contacts']) if q['label']=='actual_finite_headseat_Root_patch'];nohead=[i for i in range(len(columns)) if i not in head];B=np.c_[A[:,nohead],P];without=linprog(np.zeros(B.shape[1]),A_eq=B,b_eq=-ext,bounds=[(0,None)]*len(nohead)+[(None,None)]*6,method='highs');free=linprog(np.zeros(A.shape[1]),A_eq=A,b_eq=-ext,bounds=(0,None),method='highs');altered=ext.copy();altered[8]-=.01;control=float(abs(AP@v+altered).max());bb={n:bounds(p) for n,p in parts.items()};queries=[];hits=[]
 for n,m in itertools.combinations(parts,2):
  assert not(ROOT/'runtime/STOP').exists()
  if n not in changed and m not in changed:continue
  if not overlap(bb[n],bb[m]):continue
  volume=common(parts[m],parts[n]);q=dict(a=n,b=m,intersection_mm3=volume);queries.append(q)
  if volume>1e-8:hits.append(q)
 checks=dict(all83_actual_hashes=True,all24_original_body_wrenches=float(abs(res).max())<1e-8,nonnegative_normal_forces=min(v[:A.shape[1]])>=-1e-9,all_actual_witnesses=max(dist)<1e-7,internal_common_twist_work=common_work<1e-10,without_headseats_rejected=not without.success,free_host_rejected=not free.success,altered_load_rejected=control>.009,full83_changed_pose_no_interference=not hits)
 dump(out/'summary.json',dict(status='ACTUAL_P1_HEADSEAT_FULL83_POSE_REFERENCE' if all(checks.values()) else 'ACTUAL_P1_HEADSEAT_FULL83_POSE_FAIL',candidate_reference=ref(cp),producer=ref(out/'producer.py'),source=ref(sp),checks={k:bool(v) for k,v in checks.items()},actual_parts=83,pose_changed_part_IDs=changed,all_changed_pair_queries=queries,interferences=hits,independent_all24_residual_N_Nmm=res.reshape(4,6).tolist(),maximum_residual=float(abs(res).max()),maximum_witness_distance_mm=max(dist),internal_common_twist_work_error=common_work,without_headseat_LP_message=without.message,free_host_LP_message=free.message,altered_load_residual_N=control,headseat_resultant_forces_N=[sum(v[i] for i in head if s['contacts'][i]['body_i']==bi) for bi in [1,2]],newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['All83 imported; only pairs touching3posedparts rechecked. Unchangedpairs retain originalnominal evidence, not independent newfullpaircertification.','RF fasteners are actual SMOOTH nominal envelopes, not helical threads; transverse bolt/nut envelope intersection is not a quantified realthread overlap. Necessary24resultants do not solve actual threadflank compatibility, elasticity, freebolt/keeper tilt or preload.','Headseatpatch necessarycontrast remains conditional gravity/leadtorque, no100g operation/sourceallowable/mesh/time/globalenergy/hardwarePASS.']));print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},hits=hits,residual=float(abs(res).max()))),flush=True);return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
