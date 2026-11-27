"""Seeded same-product finite terminal contact continuation, no CAD changes."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,ref,dump
import primary_finger_equilibrium_v6 as m
out=ROOT/'validation/finger'/sys.argv[1];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
source=ROOT/'validation/finger/primaryP1_operating4/cases.json';old=json.loads(source.read_text());n=int(sys.argv[2]);seed=next(r for r in old if r['n']==n and r['T_N']==1.)
deps=[ROOT/'scripts/primary_finger_equilibrium_v6.py',ROOT/'scripts/primary_finger_tangent_v6.py',ROOT/'scripts/rod_point_jacobian.py',ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py',source,ROOT/'cad/exports/primaryP1_open9/summary.json']
dump(out/'inputs.json',dict(candidate=ref(deps[-1]),inputs=[ref(p) for p in deps],criteria=dict(force_equivalent_N_max=1e-8,gap_m_min=-1e-9,overlap_mm3_max=1e-8,mesh_relative_max=.01),solver_target_gap_m=-1e-12,physical_model='Same77mm Rail,86.2mm sliding PET,typical moduli,rigid grips,frictionless planar material witnesses and20mm fixed spatial X stop; no physical criterion change'))
rows=[]
for T in map(float,sys.argv[3:] or ['1']):
 assert not(ROOT/'runtime/STOP').exists();r=m.solve(n,T,.020,np.array(seed['state']));rows.append(r);dump(out/'cases.json',rows);seed=r
result=dict(status='ACTUAL_P1_FINITE_TERMINAL_CONTACT_RESULTS_NOT_RELEASE',task_id='goal_primary_terminal_feature_contact',candidate=ref(deps[-1]),inputs=ref(out/'inputs.json'),cases=ref(out/'cases.json'),rows=len(rows),conditional_equilibria=sum(r['status']=='CONDITIONAL_EQUILIBRIUM' for r in rows),whole_system_release=False,newly_qualified_system_gate_ids=[])
dump(out/'summary.json',result);print(json.dumps(result))
