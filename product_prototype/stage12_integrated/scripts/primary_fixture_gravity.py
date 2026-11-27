"""Actual finite P1 fixture gravity sensitivity, not a material selection/certificate.
Earlier port-only reference is preserved. Module/hardware masses remain unknown.
"""
import json,sys,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from verify_primary_fixture_v3 import statics
def W(p,f):return np.r_[f,np.cross(np.array(p)*.001,f)]
def main():
 out=ROOT/'validation/integrated/primaryP1_fixture_gravity1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'cad/exports/primaryP1_fixture13/summary.json';cad=json.loads(src.read_text());joint=ROOT/'validation/integrated/primaryP1_fixture_verify3/summary.json';j=json.loads(joint.read_text());patches=json.loads((REPO/j['patches']['path']).read_text());tr=json.loads((REPO/j['tractions']['path']).read_text());ext=np.array(tr['levels'][0]['result']['applied_wrench_N_Nm']);props={}
 for name in ('GROUND_PLATE','TEST_BASE'):
  r=cad['part_references'][name];assert sha(REPO/r['path'])==r['SHA256'];g=GProp_GProps();BRepGProp.VolumeProperties_s(read(REPO/r['path']),g);p=g.CentreOfMass();props[name]=dict(STEP=r,volume_mm3=g.Mass(),centroid_mm=[p.X(),p.Y(),p.Z()])
 dump(out/'inputs.json',dict(candidate=ref(src),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/verify_primary_fixture_v3.py'),j['patches'],j['tractions'],ref(S1/'scripts/incremental_stage1.py')],gravity_m_s2=[0,0,-9.80665],density_scenarios_kg_m3=[dict(GROUND_PLATE=2700,TEST_BASE=2700),dict(GROUND_PLATE=7850,TEST_BASE=2700)],density_basis='Explicit engineering sensitivity constants only; neither guaranteed mass bounds nor material/source minima. Prior ground steel candidate versus producer11 proposedAl conflict is not silently resolved.',excluded_masses='Original motor/drive/finger/frame,all bolts/nuts/wire have no verified masses; omitted explicitly. This is not full product gravity or shock/handling certification.'))
 rows=[]
 for rho in (2700.,7850.):
  masses={n:p['volume_mm3']*1e-9*(rho if n=='GROUND_PLATE' else 2700.) for n,p in props.items()}
  weights={n:W(props[n]['centroid_mm'],[0,0,-m*9.80665]) for n,m in masses.items()};ground_ext=ext+weights['GROUND_PLATE'];levels=[]
  for div in (1,2,4):
   result=statics(patches[str(div)],ground_ext,'full');assert result['success'];groundW=np.zeros(6);baseW=np.zeros(6)
   for t in result['active_uniform_tractions']:
    f=t['pressure_MPa']*t['area_mm2']*np.array(t['normal_on_ground']);p=np.array(t['centroid_mm']);groundW+=W(p,f)
    if t['patch'].startswith('head'):p[2]=66
    baseW+=W(p,-f)
   base_with_weight=baseW+weights['TEST_BASE'];res=groundW+ground_ext
   levels.append(dict(divisions=div,result=result,independently_integrated_ground_residual_N_Nm=res.tolist(),base_receives_from_joint_N_Nm=baseW.tolist(),base_joint_plus_own_weight_N_Nm=base_with_weight.tolist(),required_external_base_grip_N_Nm=(-base_with_weight).tolist(),base_transfer_error=float(np.max(abs(baseW-ground_ext)))))
  mesh=[]
  for lo,hi in zip(levels[:-1],levels[1:]):
   delta=max(abs(lo['result'][k]/hi['result'][k]-1) for k in ('bolt_axial_total_N','minimum_total_reaction_objective_N'));mesh.append(dict(pair=[lo['divisions'],hi['divisions']],reaction_objective_or_axial_relative=delta,pass_1pct=delta<=.01))
  rows.append(dict(Ground_density_assumed_kg_m3=rho,Base_density_assumed_kg_m3=2700.,conditional_masses_kg=masses,conditional_weight_wrenches_N_Nm={n:w.tolist() for n,w in weights.items()},applied_ground_port_plus_weight_N_Nm=ground_ext.tolist(),levels=levels,mesh=mesh))
 checks=dict(all_six_conditional_gravity_states_feasible=all(l['result']['success'] for r in rows for l in r['levels']),all_saved_force_and_moment_integrations=all(max(abs(v) for v in l['independently_integrated_ground_residual_N_Nm'])<1e-9 and l['base_transfer_error']<1e-9 for r in rows for l in r['levels']),actual_Ground_and_Base_volume_positive=all(p['volume_mm3']>0 for p in props.values()),both_material_intents_exposed=True)
 r=dict(status='ACTUAL_P1_FINITE_FIXTURE_GRAVITY_SENSITIVITY_NOT_MATERIAL_OR_SYSTEM_QUALIFIED',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks=checks,actual_CAD_mass_properties=props,rows=rows,whole_system_release=False,newly_qualified_system_gate_ids=[],material_intent_disposition='Earlier material contract lists Ground steel; fixture11producer proposed6061-T6 for Ground/Base. NO assigned actual/guaranteed material. Both Ground density scenarios retained; Base2700 is a single conditional contrast,not an upper bound. Original geometry-only outputs do not certify either material.',limitations=['Not full product selfweight: original69part module and separate hardware masses unknown','No physical installed orientation/bench grip,material certificates or preload/source minima','Weight changes required Base force/couple; port-only0Fz external wrench is not complete product loading','All mesh1%failures remain failures; no source/protection/strength/Stage3 approval'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,rows=[dict(rho=x['Ground_density_assumed_kg_m3'],masses=x['conditional_masses_kg'],coarse_bolt_N=x['levels'][0]['result']['bolt_axial_total_N'],fine_bolt_N=x['levels'][-1]['result']['bolt_axial_total_N'],external_base=x['levels'][-1]['required_external_base_grip_N_Nm'],mesh=x['mesh']) for x in rows])));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
