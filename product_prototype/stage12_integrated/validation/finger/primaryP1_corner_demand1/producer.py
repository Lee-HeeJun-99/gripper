"""Conditional100g shared-three-Finger,mu.8 demand on SAME actual P1 corner branch.
Scalar root is not a free-grasp,payload or capacity certificate.
"""
import json,sys,shutil
from scipy.optimize import brentq
from baseline_registry import ROOT,ref,dump
import primary_terminal_corner_v2 as model
out=ROOT/'validation/finger'/sys.argv[1];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
source=ROOT/'validation/finger/primaryP1_corner1/cases.json';old=json.loads(source.read_text());target=.1*9.80665/(3*.8);deps=[ROOT/'scripts/primary_terminal_corner_v2.py',ROOT/'scripts/primary_finger_equilibrium_v5.py',ROOT/'scripts/primary_finger_tangent_v5.py',source,ROOT/'cad/exports/primaryP1_open9/summary.json']
dump(out/'inputs.json',dict(candidate=ref(deps[-1]),inputs=[ref(p) for p in deps],target_normal_N=target,basis='100g*9.80665/(3*assumed_mu.8),equal sharing and ideal Coulomb only; no measured friction or3Finger force closure. fixed X stop20mm inward,typical moduli,rigid grips and same frictionless planar finite-body model',criteria=dict(force_N_max=1e-8,gap_m_min=-1e-9,overlap_mm3_max=1e-8,mesh_relative_max=.01),bracket_tendon_N=[1,1.1]))
rows=[];trials=[]
for seed in old:
 cache={}
 def fn(T):
  assert not(ROOT/'runtime/STOP').exists()
  if T not in cache:
   r=model.solve(seed,T);cache[T]=r;trials.append(dict(n=seed['n'],T_N=T,normal_N=r['normal_N'],status=r['status'],force_N=r['KKT_force_equivalent_N'],gap_m=r['minimum_dense_gap_m']));dump(out/'root_trials.json',trials)
  return cache[T]['normal_N']-target
 T=brentq(fn,1,1.1,xtol=1e-12);fn(T);r=cache[T];r['conditional_target_normal_N']=target;r['conditional_target_error_N']=r['normal_N']-target;rows.append(r);dump(out/'cases.json',rows)
 print(json.dumps(dict(n=seed['n'],T_N=T,normal_N=r['normal_N'],status=r['status'])),flush=True)
dump(out/'summary.json',dict(status='ACTUAL_P1_CONDITIONAL_NORMAL_DEMAND_CANDIDATES_NOT_PAYLOAD_RELEASE',candidate=ref(deps[-1]),task_id='goal_primary_terminal_feature_contact',cases=ref(out/'cases.json'),inputs=ref(out/'inputs.json'),root_trials=ref(out/'root_trials.json'),target_normal_N=target,rows=len(rows),whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Ideal equal sharing/assumedmu.8 only; actual3Finger/free100mm grasp andfriction/contact/material/time/strength unqualified','Actual deformed BRep and independent force checks mandatory','No physical overload protector or motor continuous/source-minimum acceptance']))
