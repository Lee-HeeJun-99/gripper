"""Coupled six-body finite takeup samples on actual installed P1 joint.
An admissible kinematic candidate is not a quasistatic/dynamic load history.
"""
import sys,json,shutil,math,os
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common
from validate_nutseat46c import rotate
from primary_installed51 import X,Y,NAMES
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

def main():
 out=ROOT/'validation/integrated/primaryP1_sequence51';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_installed51/summary.json';d=json.loads(sp.read_text());plan=json.loads((REPO/d['plan']['path']).read_text());cp=REPO/d['candidate']['path'];assert sha(cp)==d['candidate']['SHA256'];cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/refs[n]['path'])==refs[n]['SHA256'] for n in NAMES);parts={n:read(REPO/refs[n]['path']) for n in NAMES};c=d['thread_clearance_mm'];op=d['opening_mm'];angles=d['pose_yaw_rad'];rows=[]
 # Open head-seat/receiver together,not bolt through a stationary head plane.
 # Stage1 consumes thread axial slack;stage2 consumes three rotational gaps.
 poses=[('axial_slack',u,0.,c*u) for u in [0.,.5,1.]]+[('screw_and_rotational_slack',t,t,c+(op-c)*t) for t in [.25,.5,.75,1.]]
 pairs=[(0,4),(1,5),(2,0),(2,4),(2,3),(3,4)]
 for label,u,t,z in poses:
  assert not(ROOT/'runtime/STOP').exists();aa=[v*t for v in angles];zz=[z,0,z,z,z,0];posed={n:translate(rotate(parts[n],X,Y,a),0,0,dz) for n,a,dz in zip(NAMES,aa,zz)};pr=[]
  for i,j in pairs:
   v=common(posed[NAMES[i]],posed[NAMES[j]]);dist=BRepExtrema_DistShapeShape(posed[NAMES[i]],posed[NAMES[j]]);dist.Perform();row=dict(stage=label,parameter=u,rotation_fraction=t,opening_mm=z,a=NAMES[i],b=NAMES[j],intersection_mm3=v,distance_mm=dist.Value());pr.append(row)
   with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
  # Thread's exact helical normal gap phase relation;alltranslations/rotations explicit.
  k=.8/(2*math.pi);phase=z-k*(aa[0]-aa[1]);phase_gap=c-phase
  row=dict(stage=label,parameter=u,rotation_fraction=t,opening_mm=z,pose_yaw_rad=aa,pose_z_mm=zz,thread_axial_phase_mm=phase,loaded_flank_phase_gap_mm=phase_gap,pairs=pr);rows.append(row);print(json.dumps(dict(stage=label,u=u,max_intersection=max(r['intersection_mm3'] for r in pr))),flush=True)
 # At initial/intermediate configuration no torque-stop contact is active.
 # Do not apply final endpoint multipliers to open socket/cage gaps.
 A=np.array([r['column'] for r in d['contacts']]).T;F=np.array(d['external_load_vector_N_Nmm']);cases=[]
 for label,activeprefix in [('initial_seats_only',['headseat','nutseat']),('thread_before_torque_stops',['headseat','nutseat','thread']),('all_stops_endpoint_pure_axial',['headseat','nutseat','thread','socket','nutcage','keycage'])]:
  ix=[j for j,r in enumerate(d['contacts']) if any(r['label'].startswith(p) for p in activeprefix)];s=linprog(np.ones(len(ix)),A_eq=A[:,ix],b_eq=-F,bounds=(0,None),method='highs');cases.append(dict(configuration=label,feasible=bool(s.success),residual=None if not s.success else float(max(abs(A[:,ix]@s.x+F))),note='Endpoint-wrench algebra on active-contact subset;not intermediate nonlinear equilibrium or dynamics'))
 checks=dict(all_sampled_nonthread_pairs_clear=all(-1e-8<r['intersection_mm3']<1e-8 for row in rows for r in row['pairs']),loaded_flank_phase_nonpenetrating=all(r['loaded_flank_phase_gap_mm']>=-1e-12 for r in rows),thread_engaged_during_rotation=all(abs(r['loaded_flank_phase_gap_mm'])<1e-12 for r in rows if r['stage']=='screw_and_rotational_slack'),open_stops_not_treated_as_loadbearing=not cases[0]['feasible'] and not cases[1]['feasible'],endpoint_pure_axial_free_screw_failure_preserved=not cases[2]['feasible'])
 dump(out/'summary.json',dict(status='ACTUAL_P1_COUPLED_FINITE_TAKEUP_SAMPLES_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_COUPLED_FINITE_TAKEUP_SAMPLES_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),installed_endpoint=ref(sp),journal=ref(out/'journal.jsonl'),checks={k:bool(v) for k,v in checks.items()},pose_count=len(rows),actual_nonthread_pair_queries=sum(len(r['pairs']) for r in rows),poses=rows,contact_subsets=cases,newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0,whole_system_release=False,limitations=['Seven finitecoupledposes;not continuous collision/complete helicalCCD/contact sequence certification','Thread phase gap derived from exact declared helicoid;not a new Boolean root or continuous edge certification','Simultaneous rotary takeup is admissible candidate coordinates,not unique motion or quasistatic equilibrium','Pureaxial load cannot be statically supported even at torquestops without receiver/support relative antiyaw;requiredportcouple separately explicit;takeup inertia/impact unqualified','Other seven mountpairs/full128part global equilibrium,elasticpressure/strength/host/100g/time/globalenergy not solved']))
 print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},cases=cases)),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
