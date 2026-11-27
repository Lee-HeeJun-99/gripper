"""Actual P1 28hardware own-body axial gravity transfer on 28finite CAD patches.
Conditional thread axial action/reaction, no glue/shear/friction/preload invention.
No assembly support equilibrium, thread capacity or release claim.
"""
import sys,json,time,shutil
import numpy as np
from scipy.sparse import load_npz
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_axial_rebuild27 import specifications
from primary_gamma_attachment29 import cylinders
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read

def wrench(q,f):return np.r_[f,np.cross(np.array(q)*.001,f)]
def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
 hp=ROOT/'validation/integrated/primaryP1_hardware_gravity28/hardware_rigid_mass_loads.json';hw={r['part_ID']:r for r in json.loads(hp.read_text())};ap=ROOT/'validation/integrated/primaryP1_axial_rebuild27env/summary.json';ax=json.loads(ap.read_text());qp=REPO/ax['quadrature']['path'];patches=json.loads(qp.read_text());spec=specifications();mp=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(mp.read_text());assert len(hw)==28 and len(spec)==14
 dump(out/'inputs.json',dict(candidate=ref(cp),own_body_hardware_gravity=ref(hp),actual_28patches=ref(qp),axial_model=ref(ap),fivebody=ref(mp),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/f'scripts/{n}.py') for n in ['primary_axial_rebuild27','primary_gamma_attachment29']],assumptions='Conditional own CAD density7900; nominal ISO M3x.5/M5x.8 core and E200000MPa inherited. Scalar thread connector transmits axial force only at actual finite bolt/nut axial engagement. Unknown assembly nut setting/preload, friction/shear/tilt/flanks/allowable remain unavailable.'))
 branches=[];loads={};results=[]
 for s in spec:
  assert not(ROOT/'runtime/STOP').exists();pa=next(p for p in patches if p['branch']==s['name'] and p['side']=='a');pb=next(p for p in patches if p['branch']==s['name'] and p['side']=='b');ha=hw[s['head']];hb=hw[s['nut']];bolt=ha if 'BOLT' in ha['part_ID'] else hb;nut=hb if bolt is ha else ha
  bc=cylinders(read(REPO/bolt['STEP']['path']));nc=cylinders(read(REPO/nut['STEP']['path']));bf,bd=min(bc,key=lambda fd:fd[1]['radius_mm']);nf,nd=next((f,d) for f,d in nc if abs(d['radius_mm']-bd['radius_mm'])<1e-8);r=bd['radius_mm'];d=2*r;pitch=.5 if abs(d-3)<1e-8 else .8;assert abs(d-3)<1e-8 or abs(d-5)<1e-8
  lo=max(bd['bounds_mm'][2],nd['bounds_mm'][2]);hi=min(bd['bounds_mm'][5],nd['bounds_mm'][5]);eng=hi-lo;assert eng>0;core=d-1.226869*pitch;area=np.pi*core**2/4;threadQ=np.r_[s['center'],(lo+hi)/2]
  wa=-ha['gravity_wrench_about_world_origin_N_Nm'][2];wb=-hb['gravity_wrench_about_world_origin_N_Nm'][2];cases=[]
  for extra in [0.,1.,10.]:
   # extra is a free compression parameter, NOT an assigned operating preload.
   T=wb+extra;Na=wa+T;Nb=extra;qa=np.array(pa['material_points_mm']);qb=np.array(pb['material_points_mm']);aa=np.array(pa['normalized_positive_area_weights']);ab=np.array(pb['normalized_positive_area_weights']);Fa=aa[:,None]*np.array([0,0,Na]);Fb=ab[:,None]*np.array([0,0,-Nb]);WA=np.r_[Fa.sum(0),np.cross(qa*.001,Fa).sum(0)];WB=np.r_[Fb.sum(0),np.cross(qb*.001,Fb).sum(0)];threadW=wrench(threadQ,np.array([0,0,T]));ra=WA-threadW+ha['gravity_wrench_about_world_origin_N_Nm'];rb=WB+threadW+hb['gravity_wrench_about_world_origin_N_Nm'];pair=-WA-WB;grav=np.array(ha['gravity_wrench_about_world_origin_N_Nm'])+hb['gravity_wrench_about_world_origin_N_Nm'];err=np.max(abs(pair-grav))
   # Exact witness: axial-only normals/thread have zero X force for every coefficient.
   # Therefore 1N transverse test has residual >=1N; no least-squares fake support.
   cases.append(dict(additional_b_compression_parameter_N=extra,parameter_is_operating_preload=False,thread_tension_N=T,a_bearing_compression_N=Na,b_bearing_compression_N=Nb,hardware_a_residual_N_Nm=ra.tolist(),hardware_b_residual_N_Nm=rb.tolist(),max_own_body_residual_N_Nm=float(max(np.max(abs(ra)),np.max(abs(rb)))),pair_to_support_wrench_N_Nm=pair.tolist(),pair_gravity_transfer_error_N_Nm=float(err),nominal_core_stress_MPa=T/area,conditional_axial_extension_mm=T/s['k'],thread_rest_setting_needed=True,uniform_positive_a_pressure_MPa=Na/pa['CAD_area_mm2'],uniform_positive_b_pressure_MPa=Nb/pb['CAD_area_mm2']))
  branches.append(dict(branch=s['name'],hardware_a=s['head'],hardware_b=s['nut'],body_a=s['first'],body_b=s['second'],actual_thread_envelope_bolt=bd,actual_thread_envelope_nut=nd,nominal_diameter_mm=d,nominal_pitch_mm=pitch,conditional_core_diameter_mm=core,conditional_core_area_mm2=area,actual_axial_engagement_mm=eng,nominal_engaged_pitches=eng/pitch,thread_action_point_mm=threadQ.tolist(),actual_helical_flanks_present=False,thread_capacity_qualified=False,cases=cases,transverse_1N_case=dict(status='INFEASIBLE_AXIAL_ONLY_MODEL',unbalanced_force_N=[1,0,0],independent_left_null_vector=[1,0,0,0,0,0],minimum_force_residual_N=1.,physical_missing='Finite bore/shank contact and physical thread shear/tilt; do not substitute ties/friction/preload or balance at Base.')))
 for mr,ar in zip(model['results'],ax['results']):
  assert mr['mesh_level']==ar['mesh_level'];h=mr['mesh_level'];a=np.load(REPO/mr['reference_model']['path']);D=load_npz(REPO/ar['conditional_axial_D']['path']).toarray();N=len(a['reference_coordinates_mm']);names=['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'];X=np.zeros((N//3+1,3));masks={};offsets={}
  for n in names:
   p=a[n+'_points_mm'];o=int(a[n+'_offset']);offsets[n]=o;m=np.zeros(N,dtype=bool);m[o:o+3*len(p)]=True;masks[n]=m
  for ci,extra in enumerate([0.,1.,10.]):
   f=np.zeros(N);rows=[]
   for i,(s,b) in enumerate(zip(spec,branches)):
    c=b['cases'][ci];da=D[i]*masks[s['first']];db=D[i]*masks[s['second']];f-=c['a_bearing_compression_N']*da+c['b_bearing_compression_N']*db
    # Per body pullbacks are area quadrature, not point-lumped hardware gravity.
    for side,n,ds,Fsign in [('a',s['first'],da,-c['a_bearing_compression_N']),('b',s['second'],db,-c['b_bearing_compression_N'])]:
     o=offsets[n];p=a[n+'_points_mm'];fn=(Fsign*ds[o:o+3*len(p)]).reshape(-1,3);W=np.r_[fn.sum(0),np.cross(p*.001,fn).sum(0)];patch=next(q for q in patches if q['branch']==s['name'] and q['side']==side);q=np.r_[patch['center'],patch['z']];expected=wrench(q,[0,0,(-1 if side=='a' else 1)*(c['a_bearing_compression_N'] if side=='a' else c['b_bearing_compression_N'])]);rows.append(dict(branch=s['name'],side=side,body=n,force_moment_error_N_Nm=float(np.max(abs(W-expected))),nonzero_nodal_forces=int(np.count_nonzero(np.linalg.norm(fn,axis=1)))))
   W=np.zeros(6)
   for n in names:
    o=offsets[n];p=a[n+'_points_mm'];ff=f[o:o+3*len(p)].reshape(-1,3);W+=np.r_[ff.sum(0),np.cross(p*.001,ff).sum(0)]
   expected=sum((np.array(v['gravity_wrench_about_world_origin_N_Nm']) for v in hw.values()),np.zeros(6));loads[f'h{h}_compression{extra:g}_hardware_load_N']=f
   results.append(dict(mesh_level=h,additional_compression_parameter_N=extra,conditional_support_load_wrench_N_Nm=W.tolist(),independent_own28hardware_gravity_wrench_N_Nm=expected.tolist(),force_moment_error_N_Nm=float(np.max(abs(W-expected))),max_patch_pullback_error_N_Nm=max(q['force_moment_error_N_Nm'] for q in rows),actual_finite_patch_pullbacks=rows,no_Base_lumping=True,Base_only_receives_its_actual_fixture_nut_bearings=True,operating_preload_assigned=False,assembly_equilibrium_solved=False))
 np.savez_compressed(out/'finite_hardware_support_loads.npz',**loads);dump(out/'thread_bearing_own_body_equilibria.json',branches)
 checks=dict(all28_once={q for b in branches for q in [b['hardware_a'],b['hardware_b']]}==set(hw),all14_actual_positive_engagement=all(b['actual_axial_engagement_mm']>0 for b in branches),all84_own_body_gravity_equilibria=all(c['max_own_body_residual_N_Nm']<1e-10 for b in branches for c in b['cases']),all_finite_patch_forces=all(r['max_patch_pullback_error_N_Nm']<1e-10 for r in results),all_full_gravity_resultants=all(r['force_moment_error_N_Nm']<1e-10 for r in results),all_unilateral_bearing_and_thread=all(min(c['a_bearing_compression_N'],c['b_bearing_compression_N'],c['thread_tension_N'])>=0 for b in branches for c in b['cases']),transverse_FAILURE_preserved=all(b['transverse_1N_case']['minimum_force_residual_N']==1 for b in branches))
 dump(out/'summary.json',dict(status='ACTUAL_P1_28HARDWARE_CONDITIONAL_AXIAL_GRAVITY_TRANSFER_VERIFIED_TRANSVERSE_BLOCKED' if all(checks.values()) else 'ACTUAL_P1_HARDWARE_GRAVITY_TRANSFER_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),checks=checks,own_body_results=ref(out/'thread_bearing_own_body_equilibria.json'),results=results,loads=ref(out/'finite_hardware_support_loads.npz'),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,failures=[dict(branch=b['branch'],**b['transverse_1N_case']) for b in branches],limitations=['Hardware own-body gravity is now transferred through actual finite bearing quadrature with equal-opposite axial thread actions. This is a reference-pose conditional family, not assigned preload or complete assembly equilibrium.','CAD bolt/nut envelopes meet on nominal cylindrical thread radii, no actual helical flanks. Engagement and ISO basic core geometry recorded; thread/flank/shear/tilt/material source minima, rest setting and strength unqualified.','14 transverse 1N sensitivities are deliberately infeasible axial-only model counterexamples, not actual operating demand. No fictitious lateral ties or friction.','No support field, artificial Base force, strength/mesh/time/energy/full3Finger/anchor/all22 gates release. Loads must be recomputed on each accepted finite pose, not transferred as fixed historical field.']))
 print(json.dumps(dict(checks=checks,results=[{k:v for k,v in r.items() if k!='actual_finite_patch_pullbacks'} for r in results])));return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
