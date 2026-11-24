"""Bounded Native test of one fully retained axial-setback guide candidate."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=(.6,1.2,2.),default=.6);p.add_argument('--pilot');p.add_argument('--pair-case');a=p.parse_args();src=BASE/'results/dispatch_finite_holding1586';design=BASE/'results/terminal_setback1683';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 d=json.loads((design/'summary.json').read_text());assert d['status']=='READY_FOR_BOUNDED_NATIVE_PILOT';root=ET.parse(design/'candidate_scene_NOT_RUN.scn').getroot();forecast=120.
 if a.duration>.6:
  assert a.pilot;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY';forecast=pr['process']['runtime_s']*a.duration/pr['duration_s']*2;assert forecast<420
  assert a.pair_case,'Explicit independent pair result required; do not copy into old Raw'
  pairs=json.loads((BASE/'results'/a.pair_case/'summary.json').read_text());assert pairs['case']==a.pilot and pairs['nonzero_rows']==0,'Pilot already braced: no expansion'
 for node in root.iter():
  for key,value in list(node.attrib.items()):node.set(key,value.replace(str(design),str(out)))
 pre=json.loads((src/'preflight.json').read_text());inter=dict(design_sha256=sha(design/'summary.json'),source_sha256=sha(Path(__file__)),scope='ONE actual terminal ring2mm proximal translation, Native cablepoint and actual support hull move together. Ring dimensions/features retained; support volume changed/inherited mass-inertia NOT calibrated; rigid attachment strength NOT MEASURED. Ideal CableConstraint only, not finite-wire sliding validation. No force/dt/friction/solver/buffer changes. Fresh functional exploration only.')
 (out/'intervention.json').write_text(json.dumps(inter,indent=2));run_three(root,out,src,pre['eyelet'],pre['parts'],round(a.duration/.0025),a.duration,forecast);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
if __name__=='__main__':main()
