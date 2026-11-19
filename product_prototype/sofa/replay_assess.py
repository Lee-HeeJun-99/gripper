"""Strict saved-scene state replay check;does not mutate original/replay Raw."""
import argparse,csv,json,hashlib
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--scene',required=True);a=p.parse_args();scene=BASE/'sofa/scenes'/a.scene;identity=json.loads((scene/'identity.json').read_text());source=BASE/'results'/identity['source_case'];out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name,keys in [(f'finger{i}.csv',('q_m','v_m_s','guide0_q_m','guide1_q_m')) for i in range(3)]+[('object.csv',('rigid_q','rigid_v'))]+[(f'guide_frames{i}.csv',('rigid_q','rigid_v')) for i in range(3)]+[('support.csv',('q','v'))]:
  old=read(source/name);new=read(scene/'records'/name)
  if len(old)!=len(new):raise ValueError('incomplete replay;row-count mismatch')
  for key in keys:
   absolute=max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(old,new));records.append(dict(file=name,quantity=key,maximum_component_difference=absolute,status='PASS' if absolute<=1e-12 else 'FAIL'))
 result=dict(status='PASS' if all(x['status']=='PASS' for x in records) else 'FAIL',scope='strict actual saved-scene q/v replay ONLY,NOT grasp/physics convergence',gate=1e-12,identity_sha256=sha(scene/'identity.json'),source_sha256=sha(Path(__file__)),records=records);(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
