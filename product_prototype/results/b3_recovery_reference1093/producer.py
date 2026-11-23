"""Recovery vs independent actual gravity reference,not stress-free zero sag."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
def read(path):return list(csv.DictReader(path.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();ref=BASE/'results/b3_gravity_reference1092';src=BASE/'results/b3_lift_release1081';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);pre=json.loads((ref/'preflight.json').read_text());records=[];hashes={};tree=ET.parse(ref/'scene.scn')
 if json.loads((ref/'summary.json').read_text())['status']!='NATIVE_GRAVITY_REFERENCE_RUN_NOT_EQUILIBRIUM_CERTIFIED':raise ValueError('complete gravity reference required')
 for f in range(3):
  rp=ref/f'finger{f}.csv';sp=src/f'finger{f}.csv';r=read(rp);s=read(sp);refq=np.fromstring(r[-1]['q_m'],sep=' ').reshape(-1,3);final=np.fromstring(s[-1]['q_m'],sep=' ').reshape(-1,3)-np.array([0,0,.005]);rest=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);v=np.fromstring(r[-1]['v_m_s'],sep=' ').reshape(-1,3);start=np.fromstring(r[-20]['q_m'],sep=' ').reshape(-1,3);disp=refq-rest;actual=final-rest;den=max(float(np.linalg.norm(disp)),float(np.linalg.norm(actual)));error=float(np.linalg.norm(final-refq));rel=error/den if den>0 else None;velocity=float(np.linalg.norm(v,axis=1).max()*1000)
  records.append(dict(finger=f,reference_final_time_s=float(r[-1]['time_s']),reference_maximum_node_speed_mm_s=velocity,reference_last20_output_maximum_displacement_drift_mm=float(np.linalg.norm(refq-start,axis=1).max()*1000),maximum_recovery_vs_reference_difference_mm=float(np.linalg.norm(final-refq,axis=1).max()*1000),relative_distributed_displacement_error=rel,reference_stability=velocity<=pre['reference_stability_max_node_speed_mm_s'],relative_gate=bool(rel is not None and rel<=pre['comparison_relative_displacement_limit']),reference_actual_tendon_command_N=float(r[-1]['command_N'])))
  hashes[str(rp.relative_to(BASE))]=sha(rp);hashes[str(sp.relative_to(BASE))]=sha(sp)
 d=dict(status='PASS_GRAVITY_REFERENCE_RECOVERY_COMPARISON_ONLY' if all(r['reference_stability'] and r['relative_gate'] for r in records) else 'FAIL_GRAVITY_REFERENCE_RECOVERY_COMPARISON',records=records,relative_gate=pre['comparison_relative_displacement_limit'],absolute_floor=None,physical_validation='NOT QUALIFIED',full_recovery='NOT CERTIFIED_MATERIAL_TIME_MESH_ENERGY_GATES_OPEN',scope='Actual independent zero-tendon/no-object damped Native reference vs post-release geometry after subtracting measured prescribed5mmRoot translation. Gravity sag is not plastic residual. Low velocity is a stability diagnostic,not a full force-equilibrium or fatigue test.',input_hashes=hashes,producer_sha256=sha(Path(__file__)))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
