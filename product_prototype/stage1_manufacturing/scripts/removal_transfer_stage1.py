"""Independent subset proof for nominal clearance evidence, not force transfer."""
import argparse,json,shutil
import trimesh
from incremental_stage1 import ROOT,read,sha
from build_stage1 import cut,volume
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--base',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 paths=[ROOT/'cad/exports'/c/'summary.json' for c in (a.base,a.case)];old,new=[json.loads(p.read_text()) for p in paths];rows=[]
 for n,v in new['parts'].items():
  ov=old['parts'][n]
  if ov['sha256']==v['sha256']:continue
  s=read(ROOT/v['path']);o=read(ROOT/ov['path']);mesh=trimesh.load((ROOT/v['path']).with_suffix('.stl'),force='mesh')
  rows.append(dict(part=n,added_mm3=volume(cut(s,o)),removed_mm3=volume(o)-volume(s),closed_positive_mesh=bool(mesh.is_volume)))
 expected={f'F{i}_{n}' for i in range(3) for n in ('DRUM','IDLER')}
 passed={r['part'] for r in rows}==expected and all(abs(r['added_mm3'])<1e-7 and r['removed_mm3']>0 and r['closed_positive_mesh'] for r in rows)
 result=dict(status='REMOVAL_CLEARANCE_TRANSFER_PASS' if passed else 'FAIL',case=a.case,base=a.base,checks=rows,unchanged_count=len(new['parts'])-len(rows),input_sha256=[sha(p) for p in paths],scope='Subset proof transfers nominal NONINTERSECTION under identical prescribed transforms/declared cutsets. New maximum-wire contact separately tested. Does NOT transfer force, strength, material mass/inertia, retention capacity or driven motion.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result))
if __name__=='__main__':main()
