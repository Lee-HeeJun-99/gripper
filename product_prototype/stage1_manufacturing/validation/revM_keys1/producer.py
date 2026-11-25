"""Actual hex key bodies, socket engagement, declared staged assembly paths."""
import argparse,json,shutil,math
from incremental_stage1 import ROOT,read,bounds,overlap,common,sha
from mechanisms_stage1 import hex_axis,pitch_at,swivel_beta
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
from build_stage1 import fuse,cyl,translate,export
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 s={n:read(ROOT/v['path']) for n,v in idx['parts'].items()};bb={n:bounds(q) for n,q in s.items()};jobs=[]
 drive=[n for n in s if n.startswith('F0_') and any(k in n for k in ('PEDESTAL','CAP_','BEARING','SHAFT','DRUM','COUPLING','INNER_WASHER'))]
 dock=[n for n in s if n.startswith(('F0_JAMMING','F0_CASSETTE'))]
 for n,q in s.items():
  if not n.startswith('F0_') or not ('BOLT' in n or n in ('F0_IDLER_AXLE','F0_SWIVEL_AXLE')):continue
  b=bb[n];c=[(b[i]+b[i+3])/2 for i in range(3)];short=n[3:];cutset=[];af=2.5;depth=1.25;reach=15;swivel=False
  if short.startswith('SWIVEL_BOLT'):
   _,_,x,z=short.split('_');c=[float(x),-5,float(z)];axis=(0,1,0);af=1.5;depth=.8;swivel=True
  elif short.startswith('CAP_L_BOLT'):c=[c[0],-11,c[2]];axis=(0,1,0);af=2;depth=1;reach=6;cutset=[k for k in drive if 'COUPLING' in k]
  elif short.startswith(('CAP_R_BOLT','MOTOR_BOLT')):c[1]=b[4];axis=(0,-1,0);cutset=drive+dock if short.startswith('MOTOR') else []
  elif short in ('IDLER_AXLE','SWIVEL_AXLE'):
   c[1]=b[1];axis=(0,1,0)
   if short=='SWIVEL_AXLE':af=1.5;depth=.8
  elif short.startswith(('ROOT_BOLT','TERMINAL_FLUSH_BOLT')):c[0]=b[0];axis=(1,0,0);af=2 if 'FLUSH' in short else 2.5;depth=1 if 'FLUSH' in short else 1.25
  elif short.startswith('CASSETTE_ADAPTER_BOLT'):c[0]=b[3];axis=(-1,0,0);af=1.5;depth=.8
  else:
   c[2]=b[5];axis=(0,0,-1)
   if short.startswith(('CASSETTE_','DRUM_CAP')):af=1.5;depth=.8
   if short.startswith('RF'):cutset=dock+drive+[k for k in s if k.startswith(('F0_ROOT_BOLT','F0_ROOT_NUT'))]
   if short.startswith('MF'):cutset=drive+dock
  if short.startswith('DRUM_CAP'):
   c[1]=b[4];c[2]=(b[2]+b[5])/2;axis=(0,-1,0);af=1.5;depth=.8
   cutset=[k for k in drive if any(t in k for t in ('PEDESTAL_R','BEARING_R','CAP_R','INNER_WASHER_R','SHAFT_NUT_R'))]
  if swivel:cutset=[k for k in s if k.startswith(('F0_TERMINAL','F0_SWIVEL_AXLE','F0_SWIVEL_SPACER'))]
  # L-key is an actual finite hex bar with bend body and long leg, not ray.
  start=[c[j]-axis[j]*reach for j in range(3)]
  tool=hex_axis(start,axis,af,reach+depth)
  along=(1,0,0) if axis[2] else (0,0,1)
  tool=fuse(tool,hex_axis(start,along,af,25));tool=fuse(tool,cyl(af/math.sqrt(3),start,af,(0,0,1)))
  candidates=[]
  # Hex socket admits six physical starting orientations, not arbitrary
  # rotation through the material. Record the selected actual key pose.
  for k in range(6):
   tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(*c),gp_Dir(*axis)),k*math.pi/3);candidate=BRepBuilderAPI_Transform(tool,tr,True).Shape()
   if swivel:candidate=pitch_at(candidate,swivel_beta(43,-92),(43,0,-92))
   hits=[]
   for travel in (0,2,4,6,8,10):
    t=translate(candidate,*[-travel*v for v in axis]);tb=bounds(t)
    for name,f in s.items():
     if name in cutset or not overlap(tb,bb[name]):continue
     vol=common(t,f)
     if vol>1e-7:hits.append(dict(travel_mm=travel,part=name,volume_mm3=vol))
   candidates.append((hits,k,candidate))
   if not hits:break
  hits,k,tool=min(candidates,key=lambda x:len(x[0]))
  jobs.append(dict(fastener=n,key_AF_mm=af,key_reach_mm=reach,engagement_mm=depth,hex_start_deg=k*60,cutset=cutset,hits=hits))
  if n.endswith(('CAP_L_BOLT_74','DRUM_CAP_BOLT_72_15','CASSETTE_ADAPTER_BOLT_-8')):export(tool,out/n)
 result=dict(status='STAGED_KEY_ACCESS_PASS' if not any(j['hits'] for j in jobs) else 'STAGED_KEY_ACCESS_FAIL',jobs=jobs,source_sha256=sha(src),scope='F0 actual engaged key/25mm handle and6approach samples checked against all3Finger actual STEP. Specified cutsets removed only at declared assembly stage. Not simultaneous tools, continuous CCD, physical tightening or wrench-torque strength. Nut-spanner and component extraction require separate evidence.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],jobs=len(jobs),failed=[dict(fastener=j['fastener'],hits=j['hits'][:3]) for j in jobs if j['hits']])))
if __name__=='__main__':main()
