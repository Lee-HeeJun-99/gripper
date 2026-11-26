"""Independent actual BRep subtraction and exact circular-arc relief bound."""
import argparse,json,math,shutil
from incremental_stage1 import ROOT,read,common,sha
from build_stage1 import cut,volume
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--base',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
 out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 paths=[ROOT/'cad/exports'/x/'summary.json' for x in (a.base,a.case)]
 old,new=[json.loads(x.read_text()) for x in paths];changed=[];checks=[]
 for n,v in new['parts'].items():
  ov=old['parts'][n]
  if v['sha256']==ov['sha256']:continue
  changed.append(n);o=read(ROOT/ov['path']);s=read(ROOT/v['path'])
  removed=volume(o)-volume(s);added=volume(cut(s,o))
  checks.append(dict(part=n,removed_mm3=removed,added_mm3=added,pass_geometry=removed>0 and added<1e-7 and n.endswith('TERMINAL_FRONT')))
 R=88/(math.pi/3);intrusion=R-math.sqrt(R*R-11*11)
 result=dict(status='RELIEF_CONTRACT_PASS' if len(changed)==3 and all(x['pass_geometry'] for x in checks) and intrusion<1 else 'RELIEF_CONTRACT_FAIL',case=a.case,base=a.base,changed=changed,checks=checks,unchanged_count=len(new['parts'])-len(changed),exact_rigid_plane_intrusion_bound_mm=intrusion,nominal_relief_margin_mm=1-intrusion,bolt_seat_to_relief_mm=49-48.7,bolt_bore_lateral_web_mm=7.8-7.3,input_sha256=[sha(x) for x in paths],scope='Removal-only transfer preserves foreign-solid nonintersection; actual own-material sampled motion separately REQUIRED. No strength/force/CCD qualification.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result))
if __name__=='__main__':main()
