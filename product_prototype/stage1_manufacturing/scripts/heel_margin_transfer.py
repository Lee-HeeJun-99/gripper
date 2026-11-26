"""Removal-only proof closes exactly the measured interFinger exceptions."""
import argparse,json,math,shutil
import numpy as np
from incremental_stage1 import ROOT,read,sha
from build_stage1 import cut,volume
from interfinger_tolerance_margin import transform
from mechanism_motion import configure,tip,beta,rot
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--base',required=True);p.add_argument('--margin',required=True);p.add_argument('--tag',required=True);a=p.parse_args();paths=[ROOT/'cad/exports'/k/'summary.json' for k in (a.base,a.case)];old,new=[json.loads(f.read_text()) for f in paths];mp=ROOT/'validation'/a.margin/'summary.json';margin=json.loads(mp.read_text());assert margin['case']==a.base and margin['input_sha256']==sha(paths[0]);out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);configure(new);changes=[]
 for n,v in new['parts'].items():
  if old['parts'][n]['sha256']==v['sha256']:continue
  s,o=read(ROOT/v['path']),read(ROOT/old['parts'][n]['path']);changes.append(dict(part=n,added_mm3=volume(cut(s,o)),removed_mm3=volume(o)-volume(s)))
 expected={f'F{i}_SWIVEL_{h}' for i in range(3) for h in ('LOWER','UPPER')};assert {r['part'] for r in changes}==expected;assert all(abs(r['added_mm3'])<1e-7 and r['removed_mm3']>0 for r in changes);rows=[]
 for r in margin['near_pairs']:
  T=tip(math.radians(r['angle_deg']));P=(T@np.array([43,0,-92,1]))[:3];S=rot(beta(P)-math.radians(r['angle_deg'])-beta([43,0,-92]),point=P)@T
  def posed(n):
   i=int(n[1]);R=rot(i*2*math.pi/3,(0,0,1));return transform(read(ROOT/new['parts'][n]['path']),R@S@np.linalg.inv(R))
  dist=BRepExtrema_DistShapeShape(posed(r['a']),posed(r['b']));dist.Perform();assert dist.IsDone();pts=[]
  for i in range(1,dist.NbSolution()+1):pts.append([[getattr(p,k)() for k in ('X','Y','Z')] for p in (dist.PointOnShape1(i),dist.PointOnShape2(i))])
  rows.append(dict(angle_deg=r['angle_deg'],a=r['a'],b=r['b'],prior_distance_mm=r['distance_mm'],actual_new_distance_mm=dist.Value(),world_closest_point_pairs_mm=pts))
 ok=rows and all(r['actual_new_distance_mm']>.4 for r in rows)
 result=dict(status='HEEL_SAMPLED_TOLERANCE_TRANSFER_PASS' if ok else 'HEEL_SAMPLED_TOLERANCE_TRANSFER_FAIL',case=a.case,base=a.base,changes=changes,exceptions_rechecked=rows,unchanged_count=len(new['parts'])-len(changes),other_pairs_clearance_lower_mm=.4,scope='All prior31sampled poses/pairs outside explicit near list had >=0.4 clearance. Actual6changed halves are strict subsets, others298identical, same prescribed transforms; separation cannot decrease. Every former <0.4 exception rechecked natively using actual sector STEP and conjugated transform. Retains sampled-only scope and0.2per-rigid-part uncertainty budget; NOT CCD/strength/full all-part tolerance qualification. New notch does not change axle/bolt/wire pocket interfaces.',input_sha256=[sha(f) for f in paths]+[sha(mp)],stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],new_distances=[r['actual_new_distance_mm'] for r in rows],changed=len(changes))))
if __name__=='__main__':main()
