"""Future chamber space gauge + nominal wire-sector separation certificate."""
import argparse,json,math,shutil
import numpy as np
import trimesh
from mechanism_motion import ROOT,rot,move,intersection,flexible,laminate_ends
from wire_motion import path,arc
import wire_motion as wm
def gauge(a):
 vertices=[];stations=np.linspace(11,75,65)
 for s in stations:
  b=a*s/88;x=50 if not a else 50-88/a*(1-math.cos(b));z=-7-s if not a else -7-88/a*math.sin(b);w=min(9,12-.06*(7+s)-1)
  for d,y in [(.8,-w),(4.8,-w),(4.8,w),(.8,w)]:vertices.append([x+d*math.cos(b),y,z-d*math.sin(b)])
 faces=[[0,2,1],[0,3,2]]
 for j in range(len(stations)-1):
  for k in range(4):
   p=4*j+k;q=4*j+(k+1)%4;faces.extend([[p,q,q+4],[p,q+4,p+4]])
 k=4*(len(stations)-1);faces.extend([[k,k+1,k+2],[k,k+2,k+3]])
 m=trimesh.Trimesh(vertices,faces,process=True)
 if m.volume<0:m.invert()
 assert m.is_volume
 return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();idx=json.loads((ROOT/'cad/exports'/a.case/'summary.json').read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 wm.setup(idx)
 meshes={n:trimesh.load(ROOT/(__import__('pathlib').Path(v['path']).with_suffix('.stl')),force='mesh') for n,v in idx['parts'].items()}
 # Gauge terminates18mm belowRoot, well above the actual rigid distal5mm.
 # Moving tip cannot be omitted: transform its real meshes independently.
 from mechanism_motion import tip,beta
 rigid={n:m for n,m in meshes.items() if n.startswith('F0_') and ('TERMINAL' in n or n in ('F0_SWIVEL_AXLE','F0_SWIVEL_AXLE_NUT','F0_SWIVEL_SPACER_L','F0_SWIVEL_SPACER_R'))}
 swivel={n:m for n,m in meshes.items() if n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE'))}
 fixed={n:m for n,m in meshes.items() if not ('TERMINAL' in n or 'SWIVEL' in n or 'TIP_FACTORY_NIPPLE' in n or n.endswith(('SKIN','RAIL_L','RAIL_R','TENDON_WIRE')))}
 roots,ends=laminate_ends(meshes);rigid.update(ends)
 for i in range(3):fixed.update({n.replace('F0_',f'F{i}_',1):move(m,rot(i*2*math.pi/3,(0,0,1))) for n,m in roots.items()})
 hits=[];sectors=[]
 for deg in range(0,61,2):
  aa=math.radians(deg);G=gauge(aa);T=tip(aa);g=path(deg);S=rot(g['beta']-aa-beta([43,0,-92]),point=g['P'])@T
  targets=dict(fixed)
  for i in range(3):
   R=rot(i*2*math.pi/3,(0,0,1));targets.update({n.replace('F0_',f'F{i}_',1):move(move(m,T),R) for n,m in rigid.items()});targets.update({n.replace('F0_',f'F{i}_',1):move(move(m,S),R) for n,m in swivel.items()});targets[f'F{i}_FLEX']=move(flexible(aa),R)
   if i:targets[f'F{i}_SPACE_GAUGE']=move(G,R)
   targets[f'F{i}_MOVING_WIRE_LINE']=move(wm.segment(g['Q'],g['E'],.26),R)
   tt=np.array([math.sin(g['beta']),0,math.cos(g['beta'])]);targets[f'F{i}_WIRE_EXIT']=move(wm.segment(g['P']+16*tt,g['E'],.26),R)
  for n,m in targets.items():
   v=intersection(G,m)
   if v>1e-6:hits.append(dict(angle_deg=deg,part=n,volume_mm3=v))
  # Entire F0 external wire planarY0; internal lead has0<=Y<=3.6 and
  # rotating control polygon radius<=11mm aroundX80. Therefore absolute
  # polar angle<=atan(3.6/69), radial lower bound external minX minus chord
  # bound. Any two sector-separated wires have gap>=2*rmin*sin(delta/2)-D.
  eta=(path(0)['free']-g['free'])/wm.DRUM_R
  tt=np.array([math.sin(g['beta']),0,math.cos(g['beta'])])
  # Include the internal tip wire all the way to the bottom of the nipple,
  # not merely the external housing outlet used in the first certificate.
  pts=np.vstack([arc((80,20),wm.DRUM_R,wm.START_PHI-eta,g['phi']),arc((44,25),wm.IDLER_R,g['phi'],g['end']),[g['E'],g['Q'],g['P']+5*tt]])
  planar=wm.MODEL=='planar_tangent_nipple'
  rmin=min(float(pts[:,0].min())-.003,63 if planar else 69);polar=0 if planar else math.atan(3.6/69);gap=2*rmin*math.sin((2*math.pi/3-2*polar)/2)-.52
  sectors.append(dict(angle_deg=deg,minimum_radial_bound_mm=rmin,sector_halfangle_deg=math.degrees(polar),wire_to_wire_gap_lower_bound_mm=gap))
  if deg in (0,60):G.export(out/f'SPACE_GAUGE_{deg}.stl')
 result=dict(status='CASSETTE_SPACE_AND_WIRE_SECTOR_PASS' if not hits and min(r['wire_to_wire_gap_lower_bound_mm'] for r in sectors)>0 else 'FAIL',hits=hits,wire_sector_bounds=sectors,space_gauge=dict(natural_Z_range_mm=[-82,-18],normal_offsets_mm=[.8,4.8],width_rule='min(18,Skin width-2)'),mount='Actual blank/datum adapter20x4x2,2M2 threaded, replaces using same2M2x4 and Y+-8/Z-16 interface; not actual vacuum/bladder/pressure physics',scope='31prescribed sampled space reservations and exact planar/polar wire separation lower bounds per pose. No chamber material, seal, hose, pressure or flexible attachment fatigue qualification.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],hits=hits[:5],wire_gap_min_mm=min(r['wire_to_wire_gap_lower_bound_mm'] for r in sectors))))
if __name__=='__main__':main()
