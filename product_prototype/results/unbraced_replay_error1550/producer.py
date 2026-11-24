"""New actual Guide motion versus old-parent-pose counterfactual replay."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/paired_mesh_hold1001534';dst=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);oldroot=ET.parse(src/'scene.scn').getroot();newroot=ET.parse(dst/'scene.scn').getroot();stats=[];hashes={}
 for i in range(3):
  old=read(src/f'finger{i}.csv');new=read(dst/f'finger{i}.csv');frames=read(src/f'guide_frames{i}.csv');n=len(new);assert n>0 and [r['time_s'] for r in old[:n]]==[r['time_s'] for r in new];t=np.array([float(r['time_s']) for r in new]);rigid=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in frames[:n]]);initial=np.fromstring(oldroot.find(f"Node[@name='guides{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
  for j in (0,1):
   path=f"Node[@name='guides{i}']/Node[@name='cable{j}']";on=oldroot.find(path);nn=newroot.find(path);delta=(np.fromstring(nn.find('MechanicalObject').get('position'),sep=' ')-np.fromstring(on.find('MechanicalObject').get('position'),sep=' ')).reshape(-1,3);owners=np.fromstring(on.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);prediction=np.array([np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in old[:n]])
   for k,owner in enumerate(owners):prediction[:,k]+=Rotation.from_quat(rigid[:,owner,3:]).apply(np.repeat(Rotation.from_quat(initial[owner,3:]).inv().apply(delta[k])[None],n,axis=0))
   actual=np.array([np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in new]);error=np.linalg.norm(actual-prediction,axis=2);idx=np.unravel_index(error.argmax(),error.shape);onset=int(np.argmin(abs(t-.3625)));stats.append(dict(finger=i,cable=j,maximum_replay_error_mm=float(error[idx]*1000),worst_time_s=float(t[idx[0]]),worst_guide_index=int(idx[1]),maximum_error_at_0_3625s_mm=float(error[onset].max()*1000)))
  for file in (f'finger{i}.csv',f'guide_frames{i}.csv'):hashes[f'old/{file}']=sha(src/file);hashes[f'new/{file}']=sha(dst/file)
 d=dict(status='ACTUAL_NEW_DYNAMICS_REPLAY_DIFFERENCE_MEASURED',case=a.case,statistics=stats,scope='OldacceptedRigidposes andnewchildrestoffsets predictpositions only;actualnewNativeGuideq compared atEXACTcommontimes. Differencequantifieschangedcoupleddynamics,notitsuniquecause,energyerror ortimeconvergence. Noobservedstatealtered.',input_hashes=hashes,source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
