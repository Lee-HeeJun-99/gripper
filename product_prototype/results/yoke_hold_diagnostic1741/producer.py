"""Full Hold DIAGNOSTIC, not a promotion past the zero-internal-row gate.
Known transient15prefix hardware rows remain a whole-motion failure. Measure
whether they recur in actual Hold, not infer that from a1.2s prefix.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/capillary_hold1700';design=BASE/'results/yoke_union1728';prefix=BASE/'results/yoke_union_prefix1734';pilot=BASE/'results/yoke_union_pilot1730';records=[json.loads((s/'summary.json').read_text()) for s in (pilot,prefix)];d=json.loads((design/'summary.json').read_text());pairs=json.loads((BASE/'results/yoke_prefix_internal1738/summary.json').read_text());clear=json.loads((BASE/'results/yoke_prefix_clearance1740/summary.json').read_text());material=json.loads((BASE/'results/yoke_prefix_material1739/summary.json').read_text());mass=json.loads((BASE/'results/yoke_inertia1729/summary.json').read_text());inputs=json.loads((BASE/'results/yoke_inputs1737/summary.json').read_text())
 assert all(r['status']=='VALID_BOUNDED_EXPLORATION_ONLY' for r in records)
 assert pairs['nonzero_rows']==15 and pairs['case']==prefix.name
 assert clear['minimum_hardware_object_triangle_gap_mm']>.2 and all(x['status']=='SEPARATED' for x in clear['first_uncleared'])
 assert material['status']=='NO_POSITIVE_SAMPLED_NEW_MATERIAL_FEM_INTERSECTION' and mass['status']=='PASS_ACTUAL_YOKE_INITIAL_TENSOR_ASSEMBLY_ONLY' and inputs['status']=='PASS_DECLARED_YOKE_INPUT_CHANGES_ONLY'
 # Phase-informed wall estimate: measured early prefix + DOUBLE measured
 # incremental withdrawal cost for remaining duration, not2x whole-prefix.
 early=records[0]['process']['runtime_s'];elapsed=records[1]['process']['runtime_s'];late=(elapsed-early)/.6;forecast=elapsed+2*late*.8;assert 0<forecast<420
 root=ET.parse(design/'scene.scn').getroot()
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(design),str(out)))
 intervention=dict(classification='FULL_HOLD_DIAGNOSTIC_WITH_KNOWN_TRANSIENT_INTERNAL_CONTACT',design_case=design.name,unchanged_physics='Same1728world geometry/mass/COM/inertia, all collisions, six1.5N inputs, dt, solver, object100g and support. Only duration expanded1.2to2s.',prefix_internal_rows=15,whole_motion_unbraced='ALREADY FAIL; no prior gate reclassification',predeclared_Hold_window_s=[1.6,2.],Hold_assessment='Original2mm/5mm_s/support5mm/1e-5N gates unchanged; report internal rows separately. No global UNBRACED claim if any transient row exists.',forecast_s=forecast,forecast_basis=dict(early_0_6s_wall_s=early,prefix_1_2s_wall_s=elapsed,late_wall_s_per_sim_s=late,remaining_sim_s=.8,remaining_cost_multiplier=2),hard_child_limit_s=420,memory_GiB=4,source_sha256=sha(Path(__file__)),geometry_summary_sha256=sha(design/'summary.json'),prefix_pairs_sha256=sha(BASE/'results/yoke_prefix_internal1738/summary.json'),input_contract_sha256=sha(BASE/'results/yoke_inputs1737/summary.json'),actual_tensor_contract_sha256=sha(BASE/'results/yoke_inertia1729/summary.json'))
 (out/'intervention.json').write_text(json.dumps(intervention,indent=2));pre=json.loads((src/'preflight.json').read_text());run_three(root,out,src,pre['eyelet'],d['all_parts'],800,2.,forecast,configuration_source=design);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 purity=0.
 for file,fields in [('object.csv',['rigid_q','rigid_v'])]+[(f'guide_frames{i}.csv',['rigid_q','rigid_v']) for i in range(3)]+[(f'finger{i}.csv',['q_m','v_m_s']) for i in range(3)]:
  for x,y in zip(csv.DictReader((out/file).open()),csv.DictReader((prefix/file).open())):
   assert x['time_s']==y['time_s']
   for f in fields:purity=max(purity,float(abs(np.fromstring(x[f],sep=' ')-np.fromstring(y[f],sep=' ')).max()))
 (out/'prefix_replay_contract.json').write_text(json.dumps(dict(status='PASS_SAME_MODEL_PREFIX_REPRODUCTION_ONLY' if purity==0 else 'FAIL_PREFIX_REPRODUCTION',maximum_qv_difference=purity,scope='Actual full2s versus actual1.2s common prefix; reproducibility NOT time convergence or physical accuracy.'),indent=2));print('Actual common-prefix q/v difference:',purity)
if __name__=='__main__':main()
