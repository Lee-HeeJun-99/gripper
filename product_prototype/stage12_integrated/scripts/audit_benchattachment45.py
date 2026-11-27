"""Actual bench interface independent continuous approach envelopes and yaw force work.
No hypothetical tie or signed moment connector substitutes for a contact.
"""
import sys,json,shutil,math
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,box,cyl,fuse,cut
from mechanisms_stage1 import hex_axis
PORTS=[(-65,-35),(107,-35),(-65,15),(107,15)]
def main():
 out=ROOT/'validation/integrated/primaryP1_benchattachment45_independent';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_benchattachment45/summary.json';d=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values());s={n:read(REPO/r['path']) for n,r in d['part_references'].items()};bb={n:bounds(v) for n,v in s.items()};sweeps=[]
 def hits(sh,exclude):
  b=bounds(sh);return [dict(part_ID=n,common_mm3=v) for n in s if n not in exclude and overlap(b,bb[n]) and (v:=common(sh,s[n]))>1e-8]
 for i,(x,y) in enumerate(PORTS):
  assert not(ROOT/'runtime/STOP').exists()
  # Supersets of every intermediate pose for entire30mm bolt insertion.
  # Filling socket only enlarges envelope. Exclude mating nut because real
  # helical insertion is unsupported;do NOT count sweep as thread evidence.
  envelope=fuse(cyl(4.25,(x,y,-124),35),cyl(2.5,(x,y,-144),50))
  sweeps.append(dict(operation='continuous30mm_bolt_translation_superset',station=i,hits=hits(envelope,{f'BENCH_THROUGH_BOLT_{i}',f'BENCH_THROUGH_NUT_{i}'})))
  # Exact union for axial translation of nominal nut envelope20mm.
  envelope=cut(hex_axis((x,y,-162.7),(0,0,1),8,24.7),cyl(2.5,(x,y,-162.8),24.9))
  sweeps.append(dict(operation='continuous20mm_nominal_nut_translation',station=i,hits=hits(envelope,{f'BENCH_THROUGH_NUT_{i}'})))
  # Conservative19x4.2mm enclosing wrench envelope,130mm supplier length.
  # Union of every pose on30mm outboard straight entry;tip void remains open.
  envelope=cut(box(x-160 if x<20 else x-9.5,y-9.5,-142.45,169.5,19,4.2),box(x-9.6,y-4.1,-142.55,19.2,8.2,4.4))
  sweeps.append(dict(operation='continuous30mm_outboard_wrench_envelope',station=i,hits=hits(envelope,set())))
 # Reconstruct engaged yaw corner coordinates directly from rotated material
 # rectangle;surface normals are actual +/-Y pocket planes. Equal positive
 # magnitudes supply one torque couple,not an arbitrary moment DOF.
 validation=json.loads((ROOT/'validation/integrated/primaryP1_benchattachment45_validation2/summary.json').read_text());torques=[]
 for row in validation['key_yaw_stops']:
  a=row['zero_contact_angle_rad'];sn=math.sin(a);c=math.cos(a);sign=row['sign'];positions=[];forces=[];residuals=[]
  for center in [-25,65]:
   candidates=[]
   for dx in [-6,6]:
    for dy in [-8,8]:
     x=20+c*(center+dx-20)-sn*dy;y=-5+sn*(center+dx-20)+c*dy
     candidates.append((abs(abs(y+5)-8.1),x,y))
   g,x,y=min(candidates);positions.append([x,y,-132]);normal=[0,-math.copysign(1,y+5),0];forces.append(normal);residuals.append(g)
  moment=sum(np.cross(np.array(p)-[20,-5,-132],f)[2] for p,f in zip(positions,forces));N=1/abs(moment);F=np.array(forces)*N;moment_actual=sum(np.cross(np.array(p)-[20,-5,-132],f)[2] for p,f in zip(positions,F))
  # Work of actualforces for unit rigid yaw equals moment,independent direct
  # velocities omega cross position. Reaction opposes angle sign.
  work=sum(np.dot(f,np.cross([0,0,1],np.array(p)-[20,-5,-132])) for p,f in zip(positions,F))
  torques.append(dict(angle_rad=a,contact_points_mm=positions,normal_vectors=forces,wall_gap_residual_mm=max(residuals),normal_per_unit_Nmm=N,net_force_N=F.sum(axis=0).tolist(),reaction_moment_Nmm=moment_actual,contact_work_Nmm=work,work_error_Nmm=abs(work-moment_actual),reaction_opposes_yaw=moment_actual*sign<0,corner_pressure_strength_qualified=False))
 # Whole free product resultant:internal key forces and plate forces cancel
 # exactly. This cannot balance a nonzero applied external operating wrench.
 checks=dict(continuous_envelopes_clear=all(not r['hits'] for r in sweeps),actual_yaw_contact_on_walls=all(r['wall_gap_residual_mm']<1e-10 for r in torques),yaw_positive_contact_reactions=all(r['normal_per_unit_Nmm']>0 and r['reaction_opposes_yaw'] for r in torques),yaw_force_and_work=all(max(abs(np.array(r['net_force_N'])))<1e-12 and r['work_error_Nmm']<1e-12 and abs(abs(r['reaction_moment_Nmm'])-1)<1e-12 for r in torques))
 result=dict(status='ACTUAL_BENCH_CONTINUOUS_ENVELOPE_AND_LOCAL_YAW_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_BENCH_INDEPENDENT_AUDIT_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,continuous_translation_sweeps=sweeps,yaw_contact_unit_work=torques,physical_operating_sourcefield=None,accepted_physical_equilibria=0,whole_system_release=False,limitations=['Continuous bounds cover only specified addedfastener/toolstraighttranslations;notwholeassembly/helicalthreads or realjawprofile','Yaw zeroarea corner contact does not certify finitepressure,elasticity or strength','Throughbolt uplift/core/flank/preload/locking and externalbench-to-ground attachment unresolved','OldchangedstandFE/mass/contact invalid;all22systemgates remain unqualified'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,hits=[r for r in sweeps if r['hits']],yaw=torques)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
