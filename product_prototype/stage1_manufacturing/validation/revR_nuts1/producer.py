"""Actual open-end thin spanners against all retained STEP obstacles."""
import argparse,json,math,shutil
from incremental_stage1 import ROOT,read,bounds,overlap,common,sha
from mechanisms_stage1 import hex_axis,pitch_at
from mechanism_motion import configure,beta
from build_stage1 import box,cyl,cut,fuse,export
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir,gp_Vec
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);configure(idx)
 s={n:read(ROOT/v['path']) for n,v in idx['parts'].items()};bb={n:bounds(q) for n,q in s.items()};jobs=[]
 for n,q in s.items():
  if not n.startswith('F0_') or 'NUT' not in n:continue
  if idx.get('design_geometry',{}).get('captive_swivel_nuts') and n.startswith('F0_SWIVEL_NUT_'):
   jobs.append(dict(nut=n,method='seated0.6mm captive hex pocket; independent actual30deg rotation stop in bend_contract, NO fictitious spanner clearance PASS',hits=[]));continue
  b=bb[n];c=[(b[i]+b[i+3])/2 for i in range(3)];af=8 if 'SHAFT' in n else 4 if 'SWIVEL' in n else 5.5;t=1.2 if af==4 else 1.5;cutset=[];swivel=False
  if 'SHAFT' in n:
   axis=(0,1,0);cutset=[k for k in s if k.startswith(('F0_CAP_','F0_COUPLING'))]
  elif n.startswith('F0_ROOT_NUT'):
   axis=(1,0,0);cutset=[k for k in s if k.startswith(('F0_JAMMING_DOCK','F0_CASSETTE','F0_PEDESTAL','F0_CAP_','F0_BEARING','F0_SHAFT','F0_DRUM','F0_COUPLING','F0_INNER_WASHER'))]
  elif n.startswith('F0_TERMINAL_FLUSH_NUT'):axis=(1,0,0)
  elif 'SWIVEL' in n or n=='F0_IDLER_NUT':
   axis=(0,1,0)
   if n.startswith('F0_SWIVEL_NUT'):
    _,_,_,x,z=n.split('_');c=[float(x),3.8,float(z)];swivel=True;cutset=[k for k in s if k.startswith(('F0_TERMINAL','F0_SWIVEL_AXLE','F0_SWIVEL_SPACER'))]
  else:axis=(0,0,1)
  if n.startswith('F0_RF'):
   cutset=[k for k in s if k.startswith(('F0_JAMMING_DOCK','F0_CASSETTE','F0_PEDESTAL','F0_CAP_','F0_BEARING','F0_SHAFT','F0_DRUM','F0_COUPLING','F0_INNER_WASHER','F0_ROOT_BOLT','F0_ROOT_NUT'))]
  j=next(i for i,v in enumerate(axis) if v);origin=c[:];origin[j]-=t/2
  # Tool frame: local axisY, hex verticesX/Z, opening+X, handle+Z.
  r=7 if af==8 else 5 if af==5.5 else 4
  tool=fuse(cyl(r,(0,-t/2,0),t,(0,1,0)),box(-af/3,-t/2,r-.3,2*af/3,t,25))
  tool=cut(tool,hex_axis((0,-t/2-.1,0),(0,1,0),af,t+.2),box(0,-t/2-.1,-af/2,r+1,t+.2,af))
  # Map canonicalY axis into actual nut normal. Match actual hex flats.
  tr=gp_Trsf()
  if axis==(1,0,0):tr.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(0,0,1)),-math.pi/2)
  elif axis==(0,0,1):tr.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(1,0,0)),math.pi/2)
  tool=BRepBuilderAPI_Transform(tool,tr,True).Shape()
  opening=gp_Vec(1,0,0).Transformed(tr)
  from build_stage1 import translate
  tool=translate(tool,*c);candidates=[]
  for k in range(6):
   tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(*c),gp_Dir(*axis)),k*math.pi/3);tshape=BRepBuilderAPI_Transform(tool,tr,True).Shape()
   direction=opening.Transformed(tr)
   if swivel:tshape=pitch_at(tshape,beta([43,0,-92]),(43,0,-92))
   hits=[]
   for travel in (0,2,4,6,8,10):
    moved=translate(tshape,-travel*direction.X(),-travel*direction.Y(),-travel*direction.Z());tb=bounds(moved)
    for name,f in s.items():
     if name in cutset or not overlap(tb,bb[name]):continue
     v=common(moved,f)
     if v>1e-7:hits.append(dict(travel_mm=travel,part=name,volume_mm3=v))
   candidates.append((hits,k,tshape))
   if not hits:break
  hits,k,tool_shape=min(candidates,key=lambda x:len(x[0]));method='open-end spanner'
  if hits:
   # A real axial nutdriver is preferable to forcing a long side-entry
   # spanner between neighbouring Palm nuts. Deep hex accommodates the
   # protruding screw; hollow extension avoids contacting its thread tip.
   sign=-1 if axis==(0,0,1) or n=='F0_SHAFT_NUT_L' else 1
   direction=tuple(sign*v for v in axis);front=c[:];front[j]=(b[j+3]-.1 if sign<0 else b[j]+.1)
   radius=af/math.sqrt(3)+.9;L=20 if af==8 else 40
   socket=cyl(radius,front,10,direction);stemstart=[front[i]+10*direction[i] for i in range(3)]
   socket=fuse(socket,cyl(3.5 if af==8 else 3,stemstart,L-10,direction))
   socket=cut(socket,hex_axis(tuple(front[i]-.1*direction[i] for i in range(3)),direction,af,10.2),cyl(2.65 if af==8 else 1.75,tuple(front[i]-.1*direction[i] for i in range(3)),L+.2,direction))
   socket_hits=[]
   for travel in (0,2,4,6,8,10):
    moved=translate(socket,*(travel*v for v in direction));tb=bounds(moved)
    for name,f in s.items():
     if name in cutset or not overlap(tb,bb[name]):continue
     v=common(moved,f)
     if v>1e-7:socket_hits.append(dict(travel_mm=travel,part=name,volume_mm3=v))
   if not socket_hits:hits=[];tool_shape=socket;method='axial deep hex nutdriver,20/40mm finite hollow body; no motorized socket assumed'
  export(tool_shape,out/n)
  jobs.append(dict(nut=n,method=method,CAD_STEP=str((out/(n+'.step')).relative_to(ROOT)),AF_mm=af,thickness_mm=t,outer_radius_mm=r,clocking_deg=k*60,removed_before_this_stage=cutset,hits=hits))
 result=dict(status='NUT_TOOL_ACCESS_PASS' if not any(j['hits'] for j in jobs) else 'NUT_TOOL_ACCESS_FAIL',jobs=jobs,scope='Finite spanner or axial hollow nutdriver with6sampled0..10mm insertion positions, staged cutsets. Captive pockets require actual rotation stop proof. Continuous swing, simultaneous screw key, torque capacity and hardware NOT qualified here.',source_sha256=sha(src),stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],jobs=len(jobs),failed=[dict(nut=j['nut'],hits=j['hits'][:3]) for j in jobs if j['hits']])))
if __name__=='__main__':main()
