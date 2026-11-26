"""Finite counterhold and staged motor/coupling removal; sampled, not CCD."""
import argparse,json,math,shutil
import numpy as np
from incremental_stage1 import ROOT,read,bounds,overlap,common,sha
from build_stage1 import box,cyl,cut,fuse,translate,export
from torque_motion_stage1 import turn
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--nuts',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);s={n:read(ROOT/v['path']) for n,v in idx['parts'].items()};bb={n:bounds(q) for n,q in s.items()};nj=json.loads((ROOT/'validation'/a.nuts/'summary.json').read_text());assert nj['source_sha256']==sha(src)
 tool=cut(fuse(cyl(5,(80,-15.6,20),1.2,(0,1,0)),box(84.5,-15.6,18.7,25,1.2,2.6)),box(77.95,-15.7,17.4,4.1,1.4,10));export(tool,out/'SHAFT_AF4_COUNTERHOLD');hits=[];tb=bounds(tool)
 removed={n for n in s if n.startswith(('F0_CAP_','F0_COUPLING'))};counterhits=[]
 for n,q in s.items():
  if n not in removed and overlap(tb,bb[n]):
   v=common(tool,q)
   if v>1e-7:hits.append(dict(part=n,volume_mm3=v))
 rotated=turn(s['F0_SHAFT'],(80,0,20),(0,1,0),30,0);stop=common(tool,rotated)
 for row in nj['jobs']:
  if not row['nut'].startswith('F0_SHAFT_NUT'):continue
  n=row['nut'];nt=read(ROOT/row['CAD_STEP']);c=[(bb[n][i]+bb[n][i+3])/2 for i in range(3)]
  for deg in range(0,61,10):
   posed=turn(nt,c,(0,1,0),deg,0)
   for k,q in s.items():
    if k==n or k in removed:continue
    if overlap(bounds(posed),bb[k]):
     v=common(posed,q)
     if v>1e-7:counterhits.append(dict(nut=n,deg=deg,part=k,volume_mm3=v))
   v=common(posed,tool)
   if v>1e-7:counterhits.append(dict(nut=n,deg=deg,part='SHAFT_COUNTERHOLD',volume_mm3=v))
 paths=[]
 def path(name,members,removed,offsets):
  found=[]
  for step,d in enumerate(offsets):
   for n in members:
    q=translate(s[n],*d);b=bounds(q)
    for k,f in s.items():
     if k in members or k in removed:continue
     if overlap(b,bb[k]):
      v=common(q,f)
      if v>1e-7:found.append(dict(step=step,member=n,obstacle=k,volume_mm3=v))
  paths.append(dict(name=name,members=sorted(members),cutset=sorted(removed),samples=len(offsets),hits=found))
 coupling={n for n in s if n.startswith('F0_COUPLING')};bolts={n for n in coupling if 'BOLT' in n}
 for name,sign in [('F0_COUPLING_UPPER',1),('F0_COUPLING_LOWER',-1)]:
  offsets=[(0,0,sign*z) for z in np.linspace(0,8,17)]+[(x,0,sign*8) for x in np.linspace(0,30,16)]
  path(name,{name},coupling-{name},offsets)
 module={n for n in s if n in ('F0_MOTOR','F0_MOTOR_PLATE','F0_MF0_BOLT','F0_MF1_BOLT') or n.startswith('F0_MOTOR_BOLT')}
 path('motor_module_lift',module,coupling|{'F0_MF0_NUT','F0_MF1_NUT'},[(0,0,z) for z in np.linspace(0,60,31)])
 path('idler_base_screw_clear_then_side',{'F0_IDLER_BASE_BOLT'},{'F0_IDLER_BASE_NUT','F0_TENDON_WIRE','F0_DRUM_FACTORY_NIPPLE','F0_TIP_FACTORY_NIPPLE'},[(0,0,z) for z in np.linspace(0,12.1,14)]+[(0,-y,12.1) for y in np.linspace(0,20,11)])
 result=dict(status='SHAFT_HOLD_AND_SERVICE_PASS' if not hits and stop>1e-7 and not counterhits and not any(r['hits'] for r in paths) else 'SHAFT_HOLD_AND_SERVICE_FAIL',case=a.case,counterhold_hits=hits,rotation_stop_common_mm3=stop,nut_swing_hits=counterhits,paths=paths,scope='Finite AF4 tool and actual shafts/nut tools; sampled60deg nut swing and staged module paths, NOT CCD/torque/preload/strength. Slide nut over plain grip BEFORE installing counterhold, hand-thread then counterhold for final adjustment. Remove counterhold before withdrawing nut. Coupling removed only for service, full operating CAD retained.',input_sha256=sha(src),stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],counterhold_hits=hits,stop=stop,nut_hits=len(counterhits),paths=[(r['name'],len(r['hits'])) for r in paths])))
if __name__=='__main__':main()
