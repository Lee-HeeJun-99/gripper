"""Actual BRep interFinger clearance margin at prescribed sampled poses.

Not CCD or a generic mating-joint tolerance stack. Broad-phase distance is
a lower bound; native distance resolves every candidate below threshold.
"""
import argparse,json,math,shutil
import numpy as np
from incremental_stage1 import ROOT,read,bounds,sha
from mechanism_motion import configure,tip,beta,rot
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Trsf
def transform(s,T):
 tr=gp_Trsf();tr.SetValues(*[float(v) for v in T[:3].reshape(-1)]);return BRepBuilderAPI_Transform(s,tr,True).Shape()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';j=json.loads(src.read_text());configure(j);out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);base={n:read(ROOT/v['path']) for n,v in j['parts'].items() if n.startswith('F0_') and not n.endswith(('SKIN','RAIL_L','RAIL_R','TENDON_WIRE'))};b0=beta([43,0,-92]);rows=[];minimum=2.;near=[]
 for deg in range(0,61,2):
  T=tip(math.radians(deg));P=(T@np.array([43,0,-92,1]))[:3];S=rot(beta(P)-math.radians(deg)-b0,point=P)@T;posed=[]
  for i in range(3):
   R=rot(i*2*math.pi/3,(0,0,1));group={}
   for n,s in base.items():
    rigid='TERMINAL' in n or n in ('F0_SWIVEL_AXLE','F0_SWIVEL_AXLE_NUT','F0_SWIVEL_SLEEVE') or n.startswith('F0_SWIVEL_SPACER_');swivel=n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE'));q=transform(s,R@(S if swivel else T if rigid else np.eye(4)));group[n.replace('F0_',f'F{i}_',1)]=(q,np.array(bounds(q)))
   posed.append(group)
  count=0;local=2.
  for i,k in ((0,1),(0,2),(1,2)):
   for n,(q,b) in posed[i].items():
    for m,(f,c) in posed[k].items():
     lower=float(np.linalg.norm(np.maximum(np.maximum(b[:3]-c[3:],c[:3]-b[3:]),0)))
     if lower>=2:continue
     dist=BRepExtrema_DistShapeShape(q,f);dist.Perform();assert dist.IsDone();v=dist.Value();count+=1;local=min(local,v)
     if v<.4:near.append(dict(angle_deg=deg,a=n,b=m,distance_mm=v))
  minimum=min(minimum,local);rows.append(dict(angle_deg=deg,native_candidate_pairs=count,certified_rigid_pair_clearance_lower_mm=local))
 result=dict(status='SAMPLED_INTERFINGER_0_4_MARGIN_PASS' if minimum>.4 else 'SAMPLED_INTERFINGER_TOLERANCE_MARGIN_FAIL',case=a.case,rows=rows,minimum_rigid_clearance_lower_mm=minimum,near_pairs=near,uncertainty_allowance_per_part_mm=.2,scope='Actual rigid interFinger STEP at31prescribed poses; native distance for allAABB pairs below2mm, others have certified >=2mm separation.0.4 pair budget is an explicit conservative0.2per-part exterior displacement envelope, NOT a demonstrated blanket process capability. Flexible material/own mating joints/rotor orientation/continuous motion/general tolerance certification are NOT included. Whole motion and own-material tests separately required.',input_sha256=sha(src),stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],minimum=minimum,near_pairs=len(near))))
if __name__=='__main__':main()
