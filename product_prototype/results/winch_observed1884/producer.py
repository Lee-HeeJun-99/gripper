"""Reuse frozen observers to resolve new mechanism Cable/contact row ownership."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def read(path):return list(csv.DictReader(path.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());src=BASE/'results/winch_finger1882';root=ET.parse(src/'scene.scn').getroot()
 for j in range(2):ET.SubElement(root,'NativeCablePhase',body=f'@winch{j}/ports/points',rigidBody=f'@winch{j}/frames',solver='@constraints',cable=f'@winch{j}/ports/input',filename=str(out/f'winch{j}_input_phases.csv'))
 ET.SubElement(root,'NativeResponseRows',manager='@nativeResponses',body='@guides0/frames',solver='@constraints',filename=str(out/'contact_provenance.csv'));ET.SubElement(root,'NativeDetectionPairs',narrow='@nativeNarrow',filename=str(out/'detector.csv'))
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',out/'scene.scn'],out/'process',120);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));purity=None
 if process['exit_code']==0 and '[ERROR]'not in logs:
  purity=0.
  for name,fields in [('skin.csv',('q','v')),('guide_frames0.csv',('rigid_q','rigid_v')),('winch0_states.csv',('rigid_q','rigid_v')),('winch1_states.csv',('rigid_q','rigid_v')),('constraints.csv',('impulses_Ns',))]:
   old=read(src/name);new=read(out/name);assert len(old)==len(new)==100
   for x,y in zip(old,new):
    for key in fields:purity=max(purity,float(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')).max()))
 d=dict(status='PASS_FROZEN_OBSERVER_PREFIX_PURITY_ONLY' if purity==0 else 'FAIL_OBSERVER_PURITY_OR_EXECUTION',process=process,maximum_q_v_impulse_difference=purity,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),scope='No reimplemented observer: existing frozen NativeCablePhase/ResponseRows/DetectionPairs. Exact100step q/v/allmultipliers compared, not relaxed. NativeResponseRows Guide-body impulse aggregation is not a per-guide or root bearing reaction. Extra actual contacts are to be classified, not discarded. No actuation/grasp/physics scope promotion.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
