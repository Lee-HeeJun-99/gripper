"""Actual mapped cable path lengths for fixed-root force-controlled B3."""
import argparse,csv,json
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET
from analyse import BASE,cable_node,sha
def length(p):return np.linalg.norm(np.diff(p,axis=0),axis=1).sum()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tree=ET.parse(src/'scene.scn');records=[];hashes={}
 for f in range(3):
  control=tree.find(f"./Node[@name='finger{f}']/NativeCableSequence")
  if float(control.get('liftHeight','0'))!=0:raise ValueError('moving PullPoint requires actual API journal')
  path=src/f'finger{f}.csv';rows=list(csv.DictReader(path.open()));t=np.array([float(r['time_s']) for r in rows]);hold=(t>=1.6-1e-12)&(t<=2+1e-12)
  for c in range(2):
   node=cable_node(tree,f,c);act=node.find('CableConstraint');ids=np.fromstring(act.get('indices'),sep=' ',dtype=int);pull=np.fromstring(act.get('pullPoint'),sep=' ');rest=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
   initial=length(np.vstack([pull,rest[ids]]));actual=np.array([length(np.vstack([pull,np.fromstring(r[f'guide{c}_q_m'],sep=' ').reshape(-1,3)[ids]])) for r in rows]);short=(initial-actual)*1000
   internal=np.array([float(r[f'cable{c}_displacement_m']) for r in rows])*1000
   records.append(dict(finger=f,cable=c,initial_path_length_mm=float(initial*1000),hold_geometric_shortening_mm=[float(short[hold].min()),float(short[hold].max())],maximum_internal_vs_accepted_geometric_difference_mm=float(abs(internal-short).max()),scope='force control has no prescribed shortening target; internal displacement is not accepted-state geometric length'))
  hashes[str(path.relative_to(BASE))]=sha(path)
 hashes[str((src/'scene.scn').relative_to(BASE))]=sha(src/'scene.scn')
 d=dict(status='ACTUAL_PATH_GEOMETRY_ONLY_NOT_CONSTRAINT_PASS',records=records,input_hashes=hashes,producer_sha256=sha(Path(__file__)),actual_pullpoint_API='NOT MEASURED;fixed XML datum and frozen controller liftHeight0',physical_validation='NOT QUALIFIED')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
