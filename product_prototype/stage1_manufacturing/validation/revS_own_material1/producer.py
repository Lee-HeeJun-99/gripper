"""Independent exported-mesh screen. Prescribed kinematics, NOT dynamics/CCD.

88mm flexible length; actual last5mm rigid clamp. Swivel rotates about its
physical axle to the tangent of the retained idler, not rigidly with the tip.
"""
import argparse, hashlib, json, math, shutil
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
IDLER_R=4.75
def configure(index):
 global IDLER_R
 IDLER_R=index.get('design_geometry',{}).get('idler_wire_radius_mm',4.75)
def rot(a,axis=(0,1,0),point=None):
 return trimesh.transformations.rotation_matrix(a,axis,point)
def tip(a):
 p=np.array([50.,0.,-100.])
 end=p if not a else np.array([50-88/a*(1-math.cos(a))-5*math.sin(a),0,-7-88/a*math.sin(a)-5*math.cos(a)])
 T=rot(a);T[:3,3]=end-T[:3,:3]@p
 return T
def beta(p):
 vx,vz=44-p[0],25-p[2]
 return -(math.atan2(vz,vx)-math.acos(IDLER_R/math.hypot(vx,vz)))
def move(m,T):
 q=m.copy();q.apply_transform(T);return q
def flexible(a,component='envelope'):
 # Conservative union envelope for actual tapered skin AND rails. No
 # terminal indexing-hole claim: own pin/tongue checked separately at REST.
 s=np.linspace(0,88,89);vertices=[]
 for t in s:
  b=a*t/88;x=50 if not a else 50-88/a*(1-math.cos(b));z=-7-t if not a else -7-88/a*math.sin(b)
  w=12-.06*(7+t);low,high=0,.5;yl,yh=-w,w
  if component=='skin':high=.3
  elif component=='railR':low,high=.3,.5;yl,yh=8.5-.06*(7+t),11.5-.06*(7+t)
  elif component=='railL':low,high=.3,.5;yl,yh=-11.5+.06*(7+t),-8.5+.06*(7+t)
  for d,y in [(low,yl),(high,yl),(high,yh),(low,yh)]:vertices.append([x+d*math.cos(b),y,z-d*math.sin(b)])
 faces=[[0,2,1],[0,3,2]]
 for j in range(len(s)-1):
  for k in range(4):
   p=j*4+k;q=j*4+(k+1)%4;faces.extend([[p,q,q+4],[p,q+4,p+4]])
 k=4*(len(s)-1);faces.extend([[k,k+1,k+2],[k,k+2,k+3]])
 m=trimesh.Trimesh(vertices,faces,process=True)
 if m.volume<0:m.invert()
 assert m.is_volume
 return m
def intersection(a,b):
 if np.any(np.minimum(a.bounds[1],b.bounds[1])-np.maximum(a.bounds[0],b.bounds[0])<=1e-8):return 0.
 return float(trimesh.boolean.intersection([a,b],engine='manifold').volume)
def laminate_ends(meshes):
 roots={};ends={}
 for suffix in ('SKIN','RAIL_L','RAIL_R'):
  m=meshes['F0_'+suffix]
  for target,z,h,label in [(roots,1.5,17,'ROOT_FIXED'),(ends,-97.5,5,'DISTAL_RIGID')]:
   clip=trimesh.creation.box(extents=[5,40,h]);clip.apply_translation([50,0,z])
   q=trimesh.boolean.intersection([m,clip],engine='manifold');assert q.is_volume
   target['F0_'+suffix+'_'+label]=q
 return roots,ends
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);args=p.parse_args()
 src=ROOT/'cad/exports'/args.case;index=json.loads((src/'summary.json').read_text());out=ROOT/'validation'/args.tag;out.mkdir(exist_ok=False)
 configure(index)
 shutil.copyfile(__file__,out/'producer.py')
 meshes={};quality=[];hashes={}
 for n,v in index['parts'].items():
  f=ROOT/Path(v['path']).with_suffix('.stl');m=trimesh.load(f,force='mesh');meshes[n]=m
  quality.append(dict(part=n,watertight=bool(m.is_watertight),volume=bool(m.is_volume),faces=len(m.faces)))
  hashes[str(f.relative_to(ROOT))]=hashlib.sha256(f.read_bytes()).hexdigest()
 if not all(q['volume'] for q in quality):
  (out/'summary.json').write_text(json.dumps(dict(status='MESH_FAIL',quality=quality,stage1_release=False),indent=2));raise RuntimeError('invalid STL')
 fixed={n:m for n,m in meshes.items() if not any(n.endswith(s) for s in ('SKIN','RAIL_L','RAIL_R','TENDON_WIRE')) and not any(k in n for k in ('TERMINAL','SWIVEL','TIP_FACTORY_NIPPLE'))}
 rigid={n:m for n,m in meshes.items() if n.startswith('F0_') and ('TERMINAL' in n or n in ('F0_SWIVEL_AXLE','F0_SWIVEL_AXLE_NUT','F0_SWIVEL_SPACER_L','F0_SWIVEL_SPACER_R'))}
 swivel={n:m for n,m in meshes.items() if n.startswith('F0_') and (n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE')))}
 roots,ends=laminate_ends(meshes);rigid.update(ends)
 for i in range(3):
  R=rot(i*2*math.pi/3,(0,0,1));fixed.update({n.replace('F0_',f'F{i}_',1):move(m,R) for n,m in roots.items()})
 hits=[];poses=[];b0=beta([43,0,-92])
 for deg in range(0,61,2):
  a=math.radians(deg);T=tip(a);pivot=(T@np.array([43,0,-92,1]))[:3];b=beta(pivot);S=rot(b-a-b0,point=pivot)@T
  local={n:move(m,T) for n,m in rigid.items()};local.update({n:move(m,S) for n,m in swivel.items()});local['F0_FLEX_ENVELOPE']=flexible(a)
  groups=[]
  for i in range(3):
   R=rot(i*2*math.pi/3,(0,0,1));groups.append({n.replace('F0_',f'F{i}_'):move(m,R) for n,m in local.items()})
  for i in range(3):
   for n,m in groups[i].items():
    for k,f in fixed.items():
     v=intersection(m,f)
     if v>1e-6:hits.append(dict(angle_deg=deg,a=n,b=k,volume_mm3=v))
   for j in range(i+1,3):
    for n,m in groups[i].items():
     for k,f in groups[j].items():
      v=intersection(m,f)
      if v>1e-6:hits.append(dict(angle_deg=deg,a=n,b=k,volume_mm3=v))
  # Relative swivel-to-terminal articulation, not suppressed as a rigid mate.
  for n in swivel:
   for k in rigid:
    v=intersection(local[n],local[k])
    if v>1e-6:hits.append(dict(angle_deg=deg,a=n,b=k,volume_mm3=v))
  # Important independent extension: the nominal pose and interFinger
  # tests do not prove own flexible sheet clears the extended rigid ears.
  # Continuous-material split interfaces are not separate hardware pairs;
  # their mapping has positiveJacobian1-kappa*d and common tangent plane.
  for material in ('skin','railL','railR'):
   fm=flexible(a,material)
   for name,m in local.items():
    if name=='F0_FLEX_ENVELOPE' or name.endswith('DISTAL_RIGID'):continue
    v=intersection(fm,m)
    if v>1e-6:hits.append(dict(angle_deg=deg,a='F0_FLEX_'+material,b=name,volume_mm3=v,kind='own flexible material vs actual hardware'))
  poses.append(dict(angle_deg=deg,pivot_mm=pivot.tolist(),swivel_deg=math.degrees(b)))
 result=dict(status='SAMPLED_MOTION_PASS' if not hits else 'SAMPLED_MOTION_FAIL',case=args.case,quality=quality,hits=hits,poses=poses,static_bulk_collision_count=len(index['collisions']),scope='31prescribed0..60deg; actual clipped root17/distal5mm, tapered88mm flexible envelope AND separate skin/rail solids against own actual hardware, rigid tip/swivel, fixed/interFinger. Shared material split boundaries excluded analytically, not physical hardware collision removal. No CCD/force/FEM/hardware qualification.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'input_sha256.json').write_text(json.dumps(hashes,indent=2));print(json.dumps(dict(status=result['status'],parts=len(quality),hits=len(hits),first_hits=hits[:5])))
if __name__=='__main__':main()
