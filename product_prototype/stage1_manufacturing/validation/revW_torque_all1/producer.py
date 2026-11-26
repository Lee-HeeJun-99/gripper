"""Finite CAD tooling swing/extraction screen, not a torque/hand test.

Actual active fastener moves, rather than leaving a ghost copy in its socket.
Six clockings are physically admissible hex reindexings. Alternate inline
driver is an explicit required finite tool profile, NOT a claimed bought SKU.
"""
import argparse,json,math,shutil,time
import numpy as np
from incremental_stage1 import ROOT,read,bounds,overlap,common,sha
from mechanisms_stage1 import hex_axis,pitch_at
from mechanism_motion import configure,beta
from build_stage1 import cyl,fuse,translate,export
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
def turn(s,c,u,deg,advance):
 tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(*c),gp_Dir(*u)),math.radians(deg));return translate(BRepBuilderAPI_Transform(s,tr,True).Shape(),*(advance*v for v in u))
def frame(n,b,idx):
 c=[(b[i]+b[i+3])/2 for i in range(3)];s=n[3:];pitch=.4 if any(k in s for k in ('SWIVEL','CASSETTE','DRUM_CAP','DRUM_PIN_PLUG')) or (s=='IDLER_AXLE' and idx['design_geometry'].get('idler_shoulder_variant')) else .5
 if s.startswith('DRUM_PIN_PLUG'):u=(1,0,0) if s.endswith('_L') else (-1,0,0);c[0]=b[0] if u[0]>0 else b[3]
 elif s.startswith('SWIVEL_BOLT'):
  x,z=map(float,s.split('_')[-2:]);v=beta([43,0,-92]);c=[43+(x-43)*math.cos(v)+(z+92)*math.sin(v),b[1],-92-(x-43)*math.sin(v)+(z+92)*math.cos(v)];u=(0,1,0)
 elif s.startswith('CAP_L_BOLT'):c[1]=-11;u=(0,1,0)
 elif s.startswith(('CAP_R_BOLT','MOTOR_BOLT','DRUM_CAP_BOLT')):c[1]=b[4];u=(0,-1,0)
 elif s in ('IDLER_AXLE','SWIVEL_AXLE'):
  if s=='IDLER_AXLE' and idx['design_geometry'].get('idler_shoulder_variant'):c[1]=b[4];u=(0,-1,0)
  else:c[1]=b[1];u=(0,1,0)
 elif s.startswith(('ROOT_BOLT','TERMINAL_FLUSH_BOLT')):c[0]=b[0];u=(1,0,0)
 elif s.startswith('CASSETTE_ADAPTER_BOLT'):c[0]=b[3];u=(-1,0,0)
 else:c[2]=b[5];u=(0,0,-1)
 return c,u,pitch
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--keys',required=True);p.add_argument('--nuts',required=True);p.add_argument('--tag',required=True);p.add_argument('--all',action='store_true');p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=10);a=p.parse_args();start=time.monotonic();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());configure(idx);kp=ROOT/'validation'/a.keys/'summary.json';np_=ROOT/'validation'/a.nuts/'summary.json';keys=json.loads(kp.read_text());nuts=json.loads(np_.read_text());assert keys['source_sha256']==nuts['source_sha256']==sha(src);out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 deps=[__file__]+[str(ROOT/'scripts'/n) for n in ('incremental_stage1.py','build_stage1.py','mechanisms_stage1.py','mechanism_motion.py')];initial={str(p):sha(__import__('pathlib').Path(p)) for p in deps};(out/'dependencies').mkdir()
 for pth in deps:shutil.copyfile(pth,out/'dependencies'/__import__('pathlib').Path(pth).name)
 s={n:read(ROOT/v['path']) for n,v in idx['parts'].items()};bs={n:bounds(v) for n,v in s.items()};counter={}
 for row in nuts['jobs']:
  n=row['nut']
  if 'CAD_STEP' not in row or 'SHAFT' in n:continue
  other='F0_IDLER_AXLE' if n=='F0_IDLER_NUT' else 'F0_SWIVEL_AXLE' if n=='F0_SWIVEL_AXLE_NUT' else n.replace('_NUT','_BOLT',1);counter[other]=row
 selected=keys['jobs'][a.start:a.start+a.count] if a.all else [r for r in keys['jobs'] if r['fastener'] in ('F0_IDLER_AXLE','F0_SWIVEL_AXLE','F0_ROOT_BOLT_-16')];rows=[]
 for job in selected:
  n=job['fastener'];c,u,pitch=frame(n,bs[n],idx);opposite=counter.get(n);ct=read(ROOT/opposite['CAD_STEP']) if opposite else None;cutset=set(job['cutset']+(opposite.get('cutset',[]) if opposite else []));cutset.discard(n)
  if n.startswith('F0_SWIVEL_BOLT'):cutset.add('F0_SWIVEL_SLEEVE') # complete bench-off-fork stage
  if n.startswith('F0_DRUM_PIN_PLUG'):cutset.update(('F0_TENDON_WIRE','F0_DRUM_FACTORY_NIPPLE','F0_TIP_FACTORY_NIPPLE')) # before full tendon purchase installation
  foreign={k:v for k,v in s.items() if k!=n and k not in cutset};attempts=[];chosen=None;tool=read(ROOT/job['CAD_STEP']);travel=max(bs[n][j+3]-bs[n][j] for j,x in enumerate(u) if x)+1
  for clock in range(6):
   hits=[];tested=0
   for distance in np.linspace(0,travel,6):
    for angle in range(0,-61,-10):
     posed=turn(tool,c,u,angle+clock*60,-float(distance));pb=bounds(posed);active=turn(s[n],c,u,angle,-float(distance));ab=bounds(active);tested+=1
     # Tool and active socket undergo the same relative rigid motion.
     for k,f in foreign.items():
      for label,obj,b in [('tool',posed,pb),('active_fastener',active,ab)]:
       if overlap(b,bs[k]):
        v=common(obj,f)
        if v>1e-7:hits.append(dict(member=label,part=k,travel_mm=float(distance),swing_deg=angle,volume_mm3=v))
     if ct:
      v=common(posed,ct)
      if v>1e-7:hits.append(dict(member='tool',part='actual_countertool',travel_mm=float(distance),swing_deg=angle,volume_mm3=v))
     if hits:break
    if hits:break
   attempts.append(dict(method='actual_L_key_60deg_swing_and_extraction_grid',clock_delta_deg=clock*60,poses=tested,hits=hits[:4]))
   if not hits:chosen=attempts[-1];break
  if chosen is None:
   # Full rotation+one-pitch outward advance is contained by these finite
   # coaxial swept cylinders. Own active fastener excluded, not deleted.
   af=job['key_AF_mm'];depth=job['engagement_mm'];point=lambda t:tuple(c[j]+u[j]*t for j in range(3));bound=fuse(cyl(af/math.sqrt(3),point(-1-travel),1+travel+depth,u),cyl(1.5,point(-60-travel),59+travel,u));bound=fuse(bound,cyl(12,point(-140-travel),80+travel,u));bb=bounds(bound);hits=[]
   for k,f in foreign.items():
    if overlap(bb,bs[k]):
     v=common(bound,f)
     if v>1e-7:hits.append(dict(member='inline_driver_swept_bound',part=k,volume_mm3=v))
   if ct:
    v=common(bound,ct)
    if v>1e-7:hits.append(dict(member='inline_driver_swept_bound',part='actual_countertool',volume_mm3=v))
   for distance in np.linspace(0,travel,7):
    active=turn(s[n],c,u,-360*float(distance)/pitch,-float(distance));ab=bounds(active)
    for k,f in foreign.items():
     if overlap(ab,bs[k]):
      v=common(active,f)
      if v>1e-7:hits.append(dict(member='active_fastener',part=k,travel_mm=float(distance),volume_mm3=v))
   attempts.append(dict(method='finite_inline_driver_fullrotation_fullwithdrawal_bound',blade_mm=60,round_shank_D_mm=3,handle_D_mm=24,handle_length_mm=80,withdrawal_mm=travel,active_fastener_samples=7,hits=hits[:4],tool_status='Required geometric profile, NOT verified purchased tool/torque rating'))
   if not hits:chosen=attempts[-1];export(bound,out/(n+'_INLINE_BOUND'))
  rows.append(dict(fastener=n,pitch_mm=pitch,socket_point_mm=c,insertion_axis=u,actual_thread_motion_note='RH advance=pitch*angle/360; extraction grid is a superset of these coupled paths, not forced SOFA q/v',declared_cutset=sorted(cutset),countertool=opposite['CAD_STEP'] if opposite else 'fixed tapped body or certified captive pocket',selected=chosen,attempts=attempts));print(json.dumps(dict(fastener=n,selected=None if chosen is None else chosen['method'])),flush=True)
 result=dict(status='TORQUE_MOTION_SCREEN_PASS' if rows and all(r['selected'] for r in rows) else 'TORQUE_MOTION_SCREEN_FAIL',case=a.case,jobs=rows,pilot=not a.all,start=a.start,count=len(rows),runtime_s=time.monotonic()-start,input_sha256={str(p.relative_to(ROOT)):sha(p) for p in (src,kp,np_)},scope='Finite key/countertool and active-fastener geometry. L-key60deg swing x6axial extraction levels sampled, NOT CCD or measured tightening torque; six hex clockings/reindexing admissible. Inline fallback is an explicit conservative full-turn tool exterior requirement, not a bought-tool claim; actual fastener contact/helical forces/operator hands/fixture strength NOT MEASURED.',stage1_release=False)
 final={str(p):sha(__import__('pathlib').Path(p)) for p in deps};assert initial==final,'Tool checker dependencies changed during run; snapshots retained, result not qualified'
 result['dependencies_SHA256']=initial
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],jobs=len(rows),runtime_s=result['runtime_s'],failed=[r['fastener'] for r in rows if not r['selected']])))
if __name__=='__main__':main()
