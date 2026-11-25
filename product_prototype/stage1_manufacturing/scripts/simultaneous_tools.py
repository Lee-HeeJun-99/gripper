"""Actual selected key and countertool solids, not independent access only."""
import argparse,json,shutil
from incremental_stage1 import ROOT,read,common,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--keys',required=True);p.add_argument('--nuts',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 kp=ROOT/'validation'/a.keys/'summary.json';np=ROOT/'validation'/a.nuts/'summary.json';k=json.loads(kp.read_text());n=json.loads(np.read_text());keys={r['fastener']:r for r in k['jobs']};nuts={r['nut']:r for r in n['jobs']};rows=[]
 for name,row in nuts.items():
  if 'CAD_STEP' not in row or 'SHAFT' in name:continue
  if name=='F0_IDLER_NUT':other='F0_IDLER_AXLE'
  elif name=='F0_SWIVEL_AXLE_NUT':other='F0_SWIVEL_AXLE'
  else:other=name.replace('_NUT','_BOLT',1)
  assert other in keys,(name,other)
  v=common(read(ROOT/row['CAD_STEP']),read(ROOT/keys[other]['CAD_STEP']));rows.append(dict(nut=name,key=other,tool_intersection_mm3=v))
 l=nuts['F0_SHAFT_NUT_L'];r=nuts['F0_SHAFT_NUT_R'];rows.append(dict(nut='F0_SHAFT_NUT_L',key='F0_SHAFT_NUT_R',tool_intersection_mm3=common(read(ROOT/l['CAD_STEP']),read(ROOT/r['CAD_STEP']))))
 result=dict(status='SIMULTANEOUS_COUNTERTOOL_PASS' if all(abs(r['tool_intersection_mm3'])<1e-7 for r in rows) else 'FAIL',pairs=rows,captive_nut_note='4swivel nuts use physical anti-rotation pockets instead of a simultaneous spanner; actual30deg stop requires bend_contract PASS',scope='Selected seated finite tools, compatible staged cutsets. Not simultaneous hand envelopes, continuous torque swing or measured torque capacity.',input_sha256={str(kp.relative_to(ROOT)):sha(kp),str(np.relative_to(ROOT)):sha(np)},stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],pairs=len(rows),hits=[r for r in rows if r['tool_intersection_mm3']>1e-7])))
if __name__=='__main__':main()
