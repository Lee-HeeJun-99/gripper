"""Exact BRep removal-only transfer, never a strength/performance transfer."""
import argparse,json,shutil
from incremental_stage1 import ROOT,read,sha
from build_stage1 import cut,volume
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();paths=[ROOT/'cad/exports'/k/'summary.json' for k in (a.base,a.case)];old,new=[json.loads(f.read_text()) for f in paths];out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);assert set(old['parts'])==set(new['parts']);rows=[]
 for n,v in new['parts'].items():
  before=old['parts'][n];assert sha(ROOT/v['path'])==v['sha256'];assert sha(ROOT/before['path'])==before['sha256']
  if v['sha256']==before['sha256']:continue
  s,o=read(ROOT/v['path']),read(ROOT/before['path']);rows.append(dict(part=n,added_mm3=volume(cut(s,o)),removed_mm3=volume(o)-volume(s)))
 allowed={f'F{i}_{s}' for i in range(3) for s in ('DRUM','IDLER')};ok={r['part'] for r in rows}==allowed and all(abs(r['added_mm3'])<1e-7 and r['removed_mm3']>0 for r in rows)
 refs={}
 # Only exact source case and actual explicit assertions are accepted.
 for tag,expected in [('revY_torque_protocol1','TORQUE_MOTION_SCREEN_PASS'),('revY_shaft_service1','SHAFT_HOLD_AND_SERVICE_PASS'),('revY_fastener_joints1','FASTENER_AXIAL_ENGAGEMENT_PASS'),('revY_preload_path1','METAL_PRELOAD_BYPASS_DESIGN_PASS'),('revY_space1','CASSETTE_SPACE_AND_WIRE_SECTOR_PASS')]:
  f=ROOT/'validation'/tag/'summary.json';j=json.loads(f.read_text());assert a.base=='revY_nut_passage' and j['status']==expected
  refs[tag]=dict(path=str(f.relative_to(ROOT)),sha256=sha(f),status=expected)
 result=dict(status='REMOVAL_ONLY_CLEARANCE_TRANSFER_PASS' if ok else 'REMOVAL_ONLY_CLEARANCE_TRANSFER_FAIL',case=a.case,base=a.base,changed=rows,unchanged=len(new['parts'])-len(rows),evidence=refs,input_sha256=[sha(f) for f in paths],scope='Only6Drum/Idler bodies lose material; unchanged fastener/shaft/coupling/sleeve/tool/fixture geometry and poses retain their proven nonintersection. Rotating parts with same prescribed transform also remain subsets. Does NOT transfer pulley seating/profile, strength/stiffness/mass/inertia/friction/dynamics or machining/retention capacity. Those require separate current-case checks.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],changed=len(rows),unchanged=result['unchanged'])))
if __name__=='__main__':main()
