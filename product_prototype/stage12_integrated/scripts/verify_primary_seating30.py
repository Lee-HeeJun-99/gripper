"""Independent own-body wrench reconstruction and exact finite-footprint membership.
No reused LP matrix or solver; verifies necessary conditional point resultants only.
"""
import sys,json,time,shutil
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_bore_seating30 import planar
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.TopAbs import TopAbs_IN,TopAbs_ON
from OCP.gp import gp_Pnt

def wrench(q,f):return np.r_[f,np.cross(q*.001,f)]
def inside(fs,q):return any(BRepClass_FaceClassifier(f,gp_Pnt(*q),1e-10).State() in [TopAbs_IN,TopAbs_ON] for f in fs)
def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py')
 src=ROOT/'validation/integrated/primaryP1_bore_seating30e/summary.json';s=json.loads(src.read_text());inp=json.loads((REPO/s['inputs']['path']).read_text());cad=json.loads((REPO/s['candidate']['path']).read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values());hw={x['part_ID']:x for x in json.loads((REPO/inp['hardware']['path']).read_text())};branches={b['branch']:b for b in json.loads((REPO/inp['branches']['path']).read_text())};rows=json.loads((REPO/s['geometry']['path']).read_text());cases=json.loads((REPO/s['numerical_cases']['path']).read_text());shapes={n:read(REPO/r['path']) for n,r in cad['part_references'].items() if n in hw or n in {f['body'] for r in rows for f in r['bearing_footprints']}}
 dump(out/'inputs.json',dict(candidate=s['candidate'],source=ref(src),verifier=ref(out/'verifier.py'),dependencies=[ref(ROOT/'scripts/primary_bore_seating30.py')]))
 membership=[];answers=[];failures=[]
 for r in rows:
  shift=np.array(r['parallel_seating_translation_mm']);b=branches[r['branch']];bolt=next(n for n in [b['hardware_a'],b['hardware_b']] if 'BOLT' in n)
  for f in r['bearing_footprints']:
   z=f['actual_shifted_overlap_centroid_mm'][2];hf=planar(shapes[f['hardware']],z);sf=planar(shapes[f['body']],z);q=np.array(f['actual_interior_point_force_sites_mm']);valid=[inside(hf,p-shift) and inside(sf,p) for p in q];membership.append(dict(branch=r['branch'],sign=r['sign'],side=f['side'],finite_sites=len(q),outside_count=sum(not a for a in valid),all_in_actual_hardware_and_support_faces=all(valid)))
  for c in [c for c in cases if c['branch']==r['branch'] and c['sign']==r['sign']]:
   R=Rotation.from_rotvec([c['common_X_rotation_rad'],0,0]).as_matrix();axis=R[:,2];a=hw[b['hardware_a']];bb=hw[b['hardware_b']];grav=[wrench(R@(np.array(h['centroid_mm'])+shift),np.array([0.,0.,-h['conditional_mass_kg']*9.80665])) for h in [a,bb]];local_g=R.T@grav[0][:3];downhill=c['common_X_rotation_rad']*r['sign']<0
   if not c['LP_success']:
    if c['model']=='AXIAL_THREAD_ONLY':
     nut=bb if b['hardware_a']==bolt else a;witness=nut['conditional_mass_kg']*9.80665*abs(np.sin(c['common_X_rotation_rad']));reason='Nut transverse own force cannot be balanced by axial bearing/thread; bore contacts act on bolt only.'
    else:
     witness=abs((R.T@(grav[0][:3]+grav[1][:3]))[1]);reason='Wrong-side bore normals and transverse gravity have same sign; sum of pair own-body transverse equations cannot vanish with nonnegative bore reactions.'
     assert not downhill
    failures.append(dict(branch=r['branch'],sign=r['sign'],model=c['model'],continuum_transverse_force_witness_N=witness,reason=reason,downhill_seating=downhill));continue
   assert c['model']=='FREE_THREAD_WRENCH_NECESSARY_RELAXATION' and downhill;x=np.array(c['solution']);res=[v.copy() for v in grav];support=np.zeros(6);k=0;positive=[]
   for f in r['bearing_footprints']:
    off=0 if f['side']=='a' else 1
    for q in f['actual_interior_point_force_sites_mm']:
     force=x[k]*axis*(1 if off==0 else -1);w=wrench(R@q,force);res[off]+=w;support-=w;positive.append(float(x[k]));k+=1
   boff=0 if b['hardware_a']==bolt else 1;bore_sum=np.zeros(3)
   for ct in r['bore_contacts']:
    if ct['active']:
     for q in ct['line_endpoints_mm']:
      force=x[k]*(R@ct['force_on_bolt_normal']);w=wrench(R@q,force);res[boff]+=w;support-=w;bore_sum+=force;positive.append(float(x[k]));k+=1
   tw=x[k:];assert len(tw)==6;res[0]-=tw;res[1]+=tw;qt=R@b['thread_action_point_mm'];local_force=R.T@tw[:3];local_moment=R.T@(tw[3:]-np.cross(qt*.001,tw[:3]));total=grav[0]+grav[1]
   answers.append(dict(branch=r['branch'],sign=r['sign'],own_body_residual_N_Nm=float(max(np.max(abs(v)) for v in res)),positive_force_min_N=min(positive),support_gravity_wrench_error_N_Nm=float(np.max(abs(support-total))),thread_force_local_N=local_force.tolist(),thread_moment_about_nominal_engagement_local_Nm=local_moment.tolist(),thread_transverse_force_N=float(np.linalg.norm(local_force[:2])),thread_bending_moment_Nm=float(np.linalg.norm(local_moment[:2])),bore_total_transverse_error_N=float(abs((R.T@bore_sum)[1]+(R.T@total[:3])[1])),finite_pressure=False,thread_constitutive_law=False,physical_equilibrium_qualified=False))
 dump(out/'finite_membership.json',membership);dump(out/'reconstructed_own_body_wrenches.json',answers);dump(out/'independent_failure_witnesses.json',failures)
 checks=dict(all56actual_finite_footprints=len(membership)==56 and all(m['outside_count']==0 for m in membership),all28conditional_own_body_reconstructions=len(answers)==28 and all(a['own_body_residual_N_Nm']<1e-8 and a['support_gravity_wrench_error_N_Nm']<1e-8 and a['positive_force_min_N']>=-1e-10 for a in answers),all84infeasible_cases_have_continuum_transverse_witness=len(failures)==84 and all(f['continuum_transverse_force_witness_N']>1e-8 for f in failures),all_conditional_bore_forces_balance_pair_transverse=all(a['bore_total_transverse_error_N']<1e-8 for a in answers))
 dump(out/'summary.json',dict(status='ACTUAL_P1_SHIFTED_FINITE_FOOTPRINT_AND_THREAD_SHEAR_NECESSARY_RESULTANTS_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_SHIFTED_SEATING_INDEPENDENT_AUDIT_FAIL',candidate=s['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=answers,failures=failures,membership=ref(out/'finite_membership.json'),newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Positive point-force static measures and unrestricted thread wrenches are not finite pressure, thread shear/tilt law, actual assembly preload/rest setting or elastic equilibrium. Independent transverse witnesses validate specific model failures only.','No pin compliance/load split or physical Base anchoring solved. All22 system gates remain unqualified; no hardware measurement or Stage3.']))
 print(json.dumps(dict(checks=checks,max_thread_transverse_force_N=max(a['thread_transverse_force_N'] for a in answers),max_thread_bending_moment_Nm=max(a['thread_bending_moment_Nm'] for a in answers))));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
