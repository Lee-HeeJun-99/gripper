"""Independent saved physical traction reconstruction; no re-solving or state repair."""
import json,math,shutil
import numpy as np
from numpy.polynomial.legendre import leggauss
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated/primaryP1_pair50_saved';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated/primaryP1_actualface50/summary.json';d=json.loads(src.read_text());assert sha(REPO/d['journal']['path'])==d['journal']['SHA256'];rows=[json.loads(s) for s in (REPO/d['journal']['path']).read_text().splitlines()];q,w=leggauss(4);cols=[]
 for row in rows:
  force=np.zeros(3);moment=np.zeros(3);lo,hi=row['theta_range'];s=row['side']
  for j,p in enumerate(row['samples']):
   point=np.array(p['point_mm']);r=math.hypot(point[0]+59,point[1]+58);a=math.atan2(point[1]+58,point[0]+59);dr=np.array([math.cos(a),math.sin(a),s/math.sqrt(3)]);da=np.array([-r*math.sin(a),r*math.cos(a),.8/(2*math.pi)]);weight=np.linalg.norm(np.cross(dr,da))*.1*(hi-lo)/2*w[j//4]*w[j%4];df=np.array(p['actual_outward_normal'])*weight;force+=df;moment+=np.cross(point-np.array([-59,-58,57.65]),df)
  cols.append(np.r_[force,moment])
 A=np.array(cols).T;stored=np.array([r['wrench_per_MPa'] for r in rows]).T;errors=[];negative_controls=[]
 for c in d['cases']:
  if not c['feasible']:continue
  pressure=np.array(c['pressure_MPa']);target=np.array(c['target']);errors.append(float(max(abs(A@pressure-target))));bad=pressure.copy();bad[int(np.argmax(pressure))]=0.;negative_controls.append(float(max(abs(A@bad-target)))>1e-6)
 pair_sources=[ROOT/'validation/integrated'/f'primaryP1_pair50_combined_{i}/summary.json' for i in range(1,8)]+[ROOT/'validation/integrated/primaryP1_pair50_feed_0/summary.json',ROOT/'validation/integrated/primaryP1_pair50_axial_0/summary.json'];pairs=[json.loads(p.read_text()) for p in pair_sources];poses=[r for p in pairs for r in p['rows']];original=ROOT/'validation/integrated/primaryP1_axialroot50/journal.jsonl';root=[json.loads(x) for x in original.read_text().splitlines()];neg=[r for r in root if r['event']=='COMPLETE' and r['common_mm3']<0]
 checks=dict(all_face_map_checks=all(d['checks'].values()),saved_integrals_reconstructed=float(max(abs(A-stored).flat))<1e-10,saved_unit_balance=max(errors)<1e-9,perturbed_pressure_rejected=all(negative_controls),all8_pair_checks=all(all(p['checks'].values()) for p in pairs),completed_pose_count=len(poses)==88,failed_signed_volume_rejected=bool(neg) and not(ROOT/'validation/integrated/primaryP1_axialroot50/summary.json').exists())
 dump(out/'summary.json',dict(status='ACTUAL_P1_SAVED_PAIR_AND_TRACTION_RECONSTRUCTION_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_SAVED_RECONSTRUCTION_FAIL',candidate=d['candidate'],verifier=ref(out/'verifier.py'),traction=ref(src),pair_sources=[ref(p) for p in pair_sources],checks={k:bool(v) for k,v in checks.items()},reconstructed_patch_count=len(rows),actual_normal_point_count=sum(len(r['samples']) for r in rows),maximum_integral_reconstruction_error=float(max(abs(A-stored).flat)),maximum_unit_wrench_residual=max(errors),negative_controls=len(negative_controls),RH_feed_pose_count=sum(r['label']=='RH_screw_relative_feed' for r in poses),axial_probe_count=sum(r['label']=='fixed_relative_rotation_axial_probe' for r in poses),root_failed_negative_volumes=neg,root_attempts_completed=sum(r['event']=='COMPLETE' for r in root),accepted_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Independent local saved-data reconstruction,NOTinstalledjointloadsplit or source-backedcapacity','Oppositeflanks not assumed simultaneouslyactive;nut/head/key/pin/host equilibrium unqualified','Failedanalyticmap/classifier anomaly/Booleanroot preserved;no exactaxialstop certified']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},maxbalance=max(errors))),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
